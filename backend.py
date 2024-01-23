from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, db, auth
import os
from werkzeug.utils import secure_filename
import requests
from base64 import b64encode
import json
from datetime import datetime, timedelta
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from urllib.parse import quote
import uuid
from statistics import mean
import tempfile

client_id = ''
client_secret = ''

# Initialize Spotipy with the credentials manager
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

app = Flask(__name__)
CORS(app)

# Initialize Firebase Admin SDK with your credentials
cred = credentials.Certificate("")
firebase_admin.initialize_app(cred, {'databaseURL': 'https://tune-mosaic-default-rtdb.firebaseio.com/'})  # Replace 'tune-mosaic' with your actual Firebase project name

@app.route('/verify-token', methods=['POST'])
def verify_token():
    # Extract the token from the request
    token = request.json.get('token')
    
    # Case 1: Token exists, meaning it's a login attempt
    if token:
        try:
            # Verify the token with Firebase Admin SDK
            decoded_token = auth.verify_id_token(token)
            # Get user by UID
            user = auth.get_user(decoded_token['uid'])
            return jsonify({'uid user login': decoded_token['uid']})
        except Exception as e:
            return jsonify({'error': str(e)}), 401
    
    # Case 2: No token, treat it as a registration attempt
    else:
        try:
            # Extract user registration data from the request JSON
            user_data = request.get_json()
            # Create a new user in Firebase Authentication
            user = auth.create_user(
                email=user_data['email'],
                password=user_data['password'],
                username=user_data['username']
            )
            
            # Store additional user information in the Firebase Realtime Database
            user_ref = db.reference(f'/users/{user.uid}')
            user_ref.set({
                'email': user_data['email'],
                'username': user_data['username'],
            })
            
            # Generate a Firebase custom token for the registered user
            custom_token = auth.create_custom_token(user.uid)
            
            return jsonify({'custom_token user register': custom_token.decode()})
        except Exception as e:
            return jsonify({'error': str(e)})

@app.route('/google-signin', methods=['POST'])
def google_signin():
    # Extract the ID token from the request
    id_token = request.json.get('idToken')
    
    try:
        # Verify the ID token using Firebase Admin SDK
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        
        # Check if user already exists in your database
        user_ref = db.reference(f'/users/{uid}')
        user = user_ref.get()

        if user:
            # User exists, handle login
            return jsonify({'status': 'success', 'message': 'User logged in', 'uid': uid})
        else:
            # New user, handle registration
            user_data = {
                'email': decoded_token['email'],
                'username': decoded_token.get('name', '')  # Use the name from decoded token if available
            }
            user_ref.set(user_data)
            return jsonify({'status': 'success', 'message': 'User registered', 'uid': uid})
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 401

def add_songs_to_all_songs(song_data):
    try:
        # Ensure song_data is a list, even if it's a single song dictionary
        if not isinstance(song_data, list):
            song_data = [song_data]

        # Reference to the all-songs node in the database
        all_songs_ref = db.reference('/all-songs')
        existing_songs = all_songs_ref.get() or {}

        # Add each song data to the all-songs node after checking for duplicates
        for song in song_data:
            song_name = song.get('Name')
            artist_name = song.get('Artist')

            # Check for duplicates in existing songs
            duplicate_found = any(
                existing_song.get('Name') == song_name and existing_song.get('Artist') == artist_name
                for existing_song in existing_songs.values()
            )

            if not duplicate_found:
                # Prepare the full song data, setting rating and dateOfRating to default values
                full_song_data = {
                    'Name': song.get('Name'),
                    'Artist': song.get('Artist'),
                    'Album': song.get('Album'),
                    'Release Date': song.get('Release Date'),
                    'Duration (ms)': song.get('Duration (ms)'),
                    'Preview URL': song.get('Preview URL'),
                    'Genre': song.get('Genre', 'Unknown'),
                    'Danceability': song.get('Danceability'),
                    'Energy': song.get('Energy'),
                    'Valence': song.get('Valence'),
                    'rating': 0,  # Default rating
                    'dateOfRating': '1-1-2001'  # Default date of rating
                }

                # Add the full song data to the all-songs node
                all_songs_ref.push(full_song_data)

        return {'success': True, 'message': 'Songs added to /all-songs successfully, duplicates skipped'}
    except Exception as e:
        return {'success': False, 'message': str(e)}


@app.route('/add-song', methods=['POST'])
def add_song():
    data = request.get_json()
    user_id = data.get('user_id')  # Get user_id from request JSON

    # Check if user_id exists
    if not user_id:
        return jsonify({'success': False, 'message': 'User ID is required'}), 400

    # Check if the user_id exists in your database
    user_ref = db.reference(f'/users/{user_id}')
    user_data = user_ref.get()

    if user_data is None:
        return jsonify({'success': False, 'message': 'User does not exist'}), 404

    song_data = data.get('song_data')  # Get the nested song_data from request JSON
    if not song_data:
        return jsonify({'success': False, 'message': 'Song data is required'}), 400

    song_name = song_data.get('Name')  # Get song_name from song_data
    artist_name = song_data.get('Artist')  # Get artist_name from song_data
    if not song_name or not artist_name:
        return jsonify({'success': False, 'message': 'Song name and artist name are required'}), 400

    # Search for the song on Spotify
    results = sp.search(q=f'track:{song_name} artist:{artist_name}', type='track', limit=1)
    if results['tracks']['items']:
        track = results['tracks']['items'][0]

        # Fetch additional details from Spotify API
        artist = sp.artist(track['artists'][0]['id'])
        audio_features = sp.audio_features(track['id'])[0]
    else:
        return jsonify({'success': False, 'message': 'Song not found on Spotify'}), 404

    # Prepare the full song data including details from Spotify
    full_song_data = {
        'Name': track['name'],
        'Artist': track['artists'][0]['name'],
        'Album': track['album']['name'],
        'Release Date': track['album']['release_date'],
        'Duration (ms)': track['duration_ms'],
        'Preview URL': track['preview_url'],
        'Genre': artist['genres'][0] if artist['genres'] else 'Unknown',
        'Danceability': audio_features['danceability'],
        'Energy': audio_features['energy'],
        'Valence': audio_features['valence'],
        'rating': 0,
        'dateOfRating': '1-1-2001'
    }

    # Get the user's songs from the database
    user_ref = db.reference(f'/users/{user_id}')
    songs_ref = user_ref.child('songs')
    existing_songs = songs_ref.get()

    # Check if the song already exists in the user's songs
    if existing_songs:
        for song_id, existing_song_data in existing_songs.items():
            if existing_song_data['Name'] == full_song_data['Name'] and existing_song_data['Artist'] == full_song_data['Artist']:
                return jsonify({'success': False, 'message': 'Song already exists'}), 409

    # Add the song data to the user's songs in the database if no duplicate was found
    new_song_ref = songs_ref.push(full_song_data)
    add_songs_to_all_songs(full_song_data)
    return jsonify({'success': True, 'message': 'Song added successfully', 'song_id': new_song_ref.key})


# Define the allowed file extensions and the upload folder
ALLOWED_EXTENSIONS = {'txt'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB in bytes

# Function to check if a file has an allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload-songs', methods=['POST'])
def upload_songs():
    # Get the uploaded file
    uploaded_file = request.files['file']

    if not uploaded_file:
        return jsonify({'success': False, 'message': 'No file uploaded'})

    # Check if the file has an allowed extension
    if not allowed_file(uploaded_file.filename):
        return jsonify({'success': False, 'message': 'Invalid file format. Only .txt files are allowed'})

    if uploaded_file.content_length is not None and uploaded_file.content_length > MAX_FILE_SIZE:
        return jsonify({'success': False, 'message': 'File size exceeds the limit (5MB)'})

    # Read the content of the uploaded file (assuming it's a text file)
    file_content = uploaded_file.read()

   # Parse the JSON data from the file content
    try:
        song_data_list = json.loads(file_content)
    except json.JSONDecodeError:
        return jsonify({'success': False, 'message': 'Invalid JSON data in the file'})

    # Get the user_id from the request
    user_id = request.form.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'User ID is required'}), 400

    # Reference to the user's songs
    user_ref = db.reference(f'/users/{user_id}')
    songs_ref = user_ref.child('songs')
    existing_songs = songs_ref.get() or {}

    # Add each song data to the user's data after validating and fetching additional details
    for song_data in song_data_list:
        song_name = song_data.get('Name')
        artist_name = song_data.get('Artist')

        # Check if the song already exists in the user's songs
        duplicate_found = any(
            song['Name'] == song_name and song['Artist'] == artist_name
            for song in existing_songs.values()
        )

        if duplicate_found:
            continue  # Skip this song if it's a duplicate

        # Search for the song on Spotify
        results = sp.search(q=f'track:{song_name} artist:{artist_name}', type='track', limit=1)
        if not results['tracks']['items']:
            continue  # Skip this song if not found on Spotify

        track = results['tracks']['items'][0]
        artist = sp.artist(track['artists'][0]['id'])
        audio_features = sp.audio_features(track['id'])[0]

        # Prepare the full song data including details from Spotify
        full_song_data = {
            'Name': track['name'],
            'Artist': track['artists'][0]['name'],
            'Album': track['album']['name'],
            'Release Date': track['album']['release_date'],
            'Duration (ms)': track['duration_ms'],
            'Preview URL': track['preview_url'],
            'Genre': artist['genres'][0] if artist['genres'] else 'Unknown',
            'Danceability': audio_features['danceability'],
            'Energy': audio_features['energy'],
            'Valence': audio_features['valence'],
            'rating': 0,
            'dateOfRating': datetime.now().strftime('%Y-%m-%d')
        }

        # Add the full song data to the user's songs in the database
        songs_ref.push(full_song_data)
        add_songs_to_all_songs(full_song_data)

    return jsonify({'success': True, 'message': 'Songs added successfully'})

@app.route('/rate-song', methods=['POST'])
def rate_song():
    data = request.get_json()
    user_id = data['user_id']
    song_id = data['song_id']  # Unique ID of the song
    new_rating = data['rating']

    # Reference to the user's songs and recommended songs
    songs_ref = db.reference(f'/users/{user_id}/songs')
    recommended_songs_ref = db.reference(f'/users/{user_id}/recommended-songs/{song_id}')
    
    try:
        # Try to get the song from the user's songs
        song = songs_ref.child(song_id).get()
        
        if song:
            # If the song is in the user's songs, update its rating
            songs_ref.child(song_id).update({
                'rating': new_rating,
                'dateOfRating': datetime.now().strftime('%Y-%m-%d')
            })
        else:
            # If the song is not in the user's songs, check recommended songs
            recommended_song = recommended_songs_ref.get()
            if recommended_song:
                recommended_songs_ref.delete()  # Remove from recommended songs
                recommended_song['rating'] = new_rating
                recommended_song['dateOfRating'] = datetime.now().strftime('%Y-%m-%d')

                # Check for duplicate song in the user's songs tab
                duplicate_found = False
                existing_songs = songs_ref.get()
                if existing_songs:
                    for existing_song_id, existing_song_data in existing_songs.items():
                        if existing_song_data['Name'] == recommended_song['Name'] and existing_song_data['Artist'] == recommended_song['Artist']:
                            # Duplicate found, update rating of the existing song
                            songs_ref.child(existing_song_id).update({
                                'rating': new_rating,
                                'dateOfRating': datetime.now().strftime('%Y-%m-%d')
                            })
                            duplicate_found = True
                            break
                
                if not duplicate_found:
                    # No duplicate found, add the song to the user's songs tab
                    songs_ref.child(song_id).set(recommended_song)
            else:
                return jsonify({'success': False, 'message': 'Song not found in songs or recommended songs'})

        return jsonify({'success': True, 'message': 'Song rating updated successfully'})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/delete-song', methods=['DELETE'])
def delete_song():
    data = request.get_json()
    user_id = data['user_id']
    song_id = data['song_id']

    # Reference to the specific song
    ref = db.reference(f'/users/{user_id}/songs/{song_id}')

    try:
        # Check if the song exists
        if ref.get() is None:
            return jsonify({'success': False, 'message': 'Song not found'}), 404

        # Delete the song
        ref.delete()

        return jsonify({'success': True, 'message': 'Song deleted successfully'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/delete-performer-songs', methods=['DELETE'])
def delete_performer_songs():
    data = request.get_json()
    user_id = data['user_id']
    performer_name = data['performer']

    # Reference to the user's songs
    user_songs_ref = db.reference(f'/users/{user_id}/songs')

    try:
        # Retrieve all songs
        all_songs = user_songs_ref.get()

        if not all_songs:
            return jsonify({'success': False, 'message': 'No songs found'}), 404

        # Iterate over the songs and delete those by the specified performer
        for song_id, song_details in all_songs.items():
            if song_details.get('performer') == performer_name:
                user_songs_ref.child(song_id).delete()

        return jsonify({'success': True, 'message': 'All songs by the performer have been deleted'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/delete-album-songs', methods=['DELETE'])
def delete_album_songs():
    data = request.get_json()
    user_id = data['user_id']
    album_name = data['albumName']

    # Reference to the user's songs
    user_songs_ref = db.reference(f'/users/{user_id}/songs')

    try:
        # Retrieve all songs
        all_songs = user_songs_ref.get()

        if not all_songs:
            return jsonify({'success': False, 'message': 'No songs found'}), 404

        # Iterate over the songs and delete those in the specified album
        for song_id, song_details in all_songs.items():
            if song_details.get('albumName') == album_name:
                user_songs_ref.child(song_id).delete()

        return jsonify({'success': True, 'message': 'All songs in the album have been deleted'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/top-songs', methods=['GET'])
def get_top_songs():
    user_id = request.args.get('user_id')  # Get user_id from query parameter
    years = int(request.args.get('years', 1))  # Get the number of years (default to 1 if not provided)

    # Calculate the cutoff date
    cutoff_date = datetime.now() - timedelta(days=365 * years)
    cutoff_date_str = cutoff_date.strftime('%Y-%m-%d')

    # Reference to the user's songs
    ref = db.reference(f'/users/{user_id}/songs')

    try:
        # Retrieve all songs
        all_songs = ref.get()

        if not all_songs:
            return jsonify({'success': False, 'message': 'No songs found'}), 404

        # Filter, sort songs, and collect song_ids
        top_song_ids = [
            song_id for song_id, song in sorted(all_songs.items(), key=lambda item: item[1].get('rating', 0), reverse=True)
            if song.get('Release Date') >= cutoff_date_str and song.get('rating', 0) > 0
        ][:10]  # Get top 10 song ids

        return jsonify({'success': True, 'top_song_ids': top_song_ids})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/follow-user', methods=['POST'])
def follow_user():
    # Extracts data from the incoming request in JSON format
    data = request.get_json()
    follower_id = data['follower_id']  # UserID of the person who follows
    followed_id = data['followed_id']  # UserID of the person being followed

    # Firebase database references
    follower_ref = db.reference(f'/users/{follower_id}/following')
    followed_ref = db.reference(f'/users/{followed_id}/followers')
    followed_following_ref = db.reference(f'/users/{followed_id}/following')  # Added
    follower_followers_ref = db.reference(f'/users/{follower_id}/followers')  # Added
    follower_friends_ref = db.reference(f'/users/{follower_id}/friends')
    followed_friends_ref = db.reference(f'/users/{followed_id}/friends')

    try:
        # Update 'following' list for the follower
        following = follower_ref.get() or []
        if followed_id not in following:
            following.append(followed_id)
            follower_ref.set(following)

        # Update 'followers' list for the followed user
        followers = followed_ref.get() or []
        if follower_id not in followers:
            followers.append(follower_id)
            followed_ref.set(followers)

        # Fetch the current 'followers' list of the follower and 'following' list of the followed
        followed_following = followed_following_ref.get() or []  # Followers of the one being followed
        follower_followers = follower_followers_ref.get() or []  # Followers of the follower

        # Check mutual following relationship before updating friends list
        if follower_id in followed_following and followed_id in follower_followers:
            # Update friends list for the follower
            follower_friends = follower_friends_ref.get() or {}
            if followed_id not in follower_friends:
                follower_friends[followed_id] = {"activityShare": True}
                follower_friends_ref.set(follower_friends)

            # Update friends list for the followed user
            followed_friends = followed_friends_ref.get() or {}
            if follower_id not in followed_friends:
                followed_friends[follower_id] = {"activityShare": True}
                followed_friends_ref.set(followed_friends)

        # Return a success message
        return jsonify({'success': True, 'message': 'Follow action successful'})

    # Error handling in case of exceptions
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

    # Error handling in case of exceptions
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/unfollow-user', methods=['POST'])
def unfollow_user():
    # Extract data from the incoming request in JSON format
    data = request.get_json()
    active_user_id = data['active_user_id']  # UserID of the person who initiates the unfollow
    unfollow_user_id = data['unfollow_user_id']  # UserID of the person to be unfollowed

    # Firebase database references
    active_user_following_ref = db.reference(f'/users/{active_user_id}/following')
    unfollow_user_followers_ref = db.reference(f'/users/{unfollow_user_id}/followers')
    active_user_friends_ref = db.reference(f'/users/{active_user_id}/friends')
    unfollow_user_friends_ref = db.reference(f'/users/{unfollow_user_id}/friends')

    try:
        # Process active_user's following list
        following = active_user_following_ref.get()
        if isinstance(following, list) and unfollow_user_id in following:
            following.remove(unfollow_user_id)
            active_user_following_ref.set(following)
        elif isinstance(following, dict) and unfollow_user_id in following:
            del following[unfollow_user_id]
            active_user_following_ref.set(following)

        # Process unfollow_user's followers list
        followers = unfollow_user_followers_ref.get()
        if isinstance(followers, list) and active_user_id in followers:
            followers.remove(active_user_id)
            unfollow_user_followers_ref.set(followers)
        elif isinstance(followers, dict) and active_user_id in followers:
            del followers[active_user_id]
            unfollow_user_followers_ref.set(followers)

        # Process active_user's friends list
        friends = active_user_friends_ref.get()
        if isinstance(friends, list) and unfollow_user_id in friends:
            friends.remove(unfollow_user_id)
            active_user_friends_ref.set(friends)
        elif isinstance(friends, dict) and unfollow_user_id in friends:
            del friends[unfollow_user_id]
            active_user_friends_ref.set(friends)

        # Process unfollow_user's friends list
        unfollow_user_friends = unfollow_user_friends_ref.get()
        if isinstance(unfollow_user_friends, list) and active_user_id in unfollow_user_friends:
            unfollow_user_friends.remove(active_user_id)
            unfollow_user_friends_ref.set(unfollow_user_friends)
        elif isinstance(unfollow_user_friends, dict) and active_user_id in unfollow_user_friends:
            del unfollow_user_friends[active_user_id]
            unfollow_user_friends_ref.set(unfollow_user_friends)

        # Return a success message
        return jsonify({'success': True, 'message': 'Unfollow action successful'})

    # Error handling in case of exceptions
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/update-friend-activity-share', methods=['POST'])
def update_friend_activity_share():
    # Extract data from the incoming request in JSON format
    data = request.get_json()
    owner_id = data['owner_id']  # UserID of the person whose friends list is to be updated
    friend_id = data['friend_id']  # UserID of the friend whose activityShare is to be updated
    new_activity_share = data['activityShare']  # New value for activityShare (True or False)

    # Firebase database reference to the owner's friends list
    friends_ref = db.reference(f'/users/{owner_id}/friends')

    try:
        # Fetch the current friends list of the owner
        friends = friends_ref.get() or {}

        # Check if the specified friend is in the owner's friends list
        if friend_id in friends:
            # Update the activityShare value for the specified friend
            friends[friend_id]['activityShare'] = new_activity_share
            friends_ref.set(friends)

            # Return a success message
            return jsonify({'success': True, 'message': 'activityShare status updated successfully'})

        else:
            # Return an error message if the friend is not in the owner's friends list
            return jsonify({'success': False, 'message': 'Friend not found in the friends list'})

    # Error handling in case of exceptions
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/create-group', methods=['POST'])
def create_group():
    data = request.get_json()
    admin_id = data['admin_id']
    group_name = data['group_name']
    member_ids = data['member_ids']  # List of member IDs

    if not group_name:
        return jsonify({'error': 'Group name is required'}), 400
    if not member_ids:
        return jsonify({'error': 'At least one member is required'}), 400
    # Generate a unique group ID (could be a UUID or based on a database sequence)
    group_id = str(uuid.uuid4())


    # Create group structure
    group_data = {
        'Name': group_name,
        'Admin': admin_id,
        'Members': member_ids
    }

    # Save group to database
    path = f'/groups/{group_id}'
    ref = db.reference(path)
    ref.set(group_data)

    return jsonify({'success': True, 'message': 'Group created successfully', 'group_id': group_id}),200

@app.route('/add-member', methods=['POST'])
def add_member():
    data = request.get_json()
    group_id = data['group_id']
    admin_id = data['admin_id']
    new_member_id = data['new_member_id']

    # Get group details
    group_ref = db.reference(f'/groups/{group_id}')
    group_data = group_ref.get()

    if group_data is None or 'Admin' not in group_data:
        return jsonify({'success': False, 'message': 'Invalid group data or missing admin information'}), 400
    
    # Check if the requester is the admin of the group
    if group_data['Admin'] != admin_id:
        return jsonify({'success': False, 'message': 'Only the admin can add members'}), 403

    # Add new member
    if new_member_id not in group_data['Members']:
        group_data['Members'].append(new_member_id)
        group_ref.set(group_data)

    return jsonify({'success': True, 'message': 'Member added successfully'})

@app.route('/remove-member', methods=['POST'])
def remove_member():
    data = request.get_json()
    group_id = data['group_id']
    admin_id = data['admin_id']
    member_id = data['member_id']

    # Get group details
    group_ref = db.reference(f'/groups/{group_id}')
    group_data = group_ref.get()

    # Check if the requester is the admin of the group
    if group_data['Admin'] != admin_id:
        return jsonify({'success': False, 'message': 'Only the admin can remove members'}), 403

    # Remove member
    if member_id in group_data['Members']:
        group_data['Members'].remove(member_id)
        group_ref.set(group_data)
    else:
        return jsonify({'success': False, 'message': 'Member not found in the group'}), 404
    return jsonify({'success': True, 'message': 'Member removed successfully'})

@app.route('/leave-group', methods=['POST'])
def leave_group():
    data = request.get_json()
    group_id = data['group_id']
    member_id = data['member_id']

    # Get group details
    group_ref = db.reference(f'/groups/{group_id}')
    group_data = group_ref.get()

    if not group_data:
        return jsonify({'success': False, 'message': 'Group not found'}), 404

    if member_id == group_data['Admin']:
        # If the member is the admin, delete the group
        group_ref.delete()
        message = 'Group deleted successfully as you were the admin'
    else:
        # Member leaves the group
        if member_id in group_data['Members']:
            group_data['Members'].remove(member_id)
            group_ref.set(group_data)
            message = 'You left the group successfully'
        else:
            message = 'You are not a member of this group'

    return jsonify({'success': True, 'message': message})

@app.route('/recommend-songs', methods=['GET'])
def recommend_songs():
    user_id = request.args.get('user_id').strip()
    songs_path = f'/users/{user_id}/songs'
    recommended_songs_path = f'/users/{user_id}/recommended-songs'
    all_songs_path = '/all-songs'

    # Get references to user's songs, recommended songs, and all songs
    songs_ref = db.reference(songs_path)
    recommended_songs_ref = db.reference(recommended_songs_path)
    all_songs_ref = db.reference(all_songs_path)

    # Fetch all songs, recommended songs, and all songs in the database
    user_songs = songs_ref.get() or {}
    recommended_songs = recommended_songs_ref.get() or {}
    all_songs = all_songs_ref.get() or {}

    # Initialize recommended_tracks, filter top-rated songs, etc.
    recommended_tracks = []
    max_recommendations = 10
    max_internal_recommendations = 5
    similarity_threshold = 0.8  # Adjust this value based on your preference

    # Calculate the profile for the user's most liked songs
    top_songs = [song for song in user_songs.values() if song.get('rating') == 5]
    if top_songs:
        profile = {
            'Danceability': mean([song['Danceability'] for song in top_songs]),
            'Energy': mean([song['Energy'] for song in top_songs]),
            'Valence': mean([song['Valence'] for song in top_songs]),
        }

        # Find similar songs in all_songs
        similar_songs = []
        for song_id, song in all_songs.items():
            # Calculate similarity (you can define the similarity function as needed)
            similarity = 1 - sum(abs(song[feature] - profile[feature]) for feature in ['Danceability', 'Energy', 'Valence']) / 3
            
            # If the song is similar enough and not already in user's songs or recommended songs
            if similarity > similarity_threshold and song_id not in user_songs and song_id not in recommended_songs:
                song['similarity'] = similarity  # Add similarity score for sorting
                similar_songs.append(song)

        # Sort the similar songs based on similarity and take the top N
        similar_songs = sorted(similar_songs, key=lambda x: x['similarity'], reverse=True)[:max_internal_recommendations]

        # Add similar songs to the recommendations
        for song in similar_songs:
            # Check for duplicates in the recommended tracks
            if not any(rec_track['Name'] == song['Name'] and rec_track['Artist'] == song['Artist'] for rec_track in recommended_tracks):
                recommended_tracks.append({'Name': song['Name'], 'Artist': song['Artist']})
                song_name = song.get('Name')
                artist_name = song.get('Artist')
                # Check for duplicates in existing songs
                duplicate_found = any(
                    recommended_song.get('Name') == song_name and recommended_song.get('Artist') == artist_name
                    for recommended_song in recommended_songs.values()
                )
                if not duplicate_found:
                    recommended_songs_ref.push(song)
                    add_songs_to_all_songs(song)  # Add to /all-songs if not a duplicate
    print(recommended_tracks)
    # If we haven't reached the max recommendations, fill the remaining spots from Spotify API
    remaining_slots = max_recommendations - len(recommended_tracks)
    if remaining_slots > 0:
        # Extract track names and artist names from top-rated songs
        track_names = [song['Name'] for song in top_songs]
        artist_names = [song['Artist'] for song in top_songs]

        # Get track IDs for the top-rated songs and retrieve recommendations
        for i in range(len(track_names)):
            if len(recommended_tracks) >= max_recommendations:
                break  # Stop if we already have max recommendations
            results = sp.search(q=f"track:{track_names[i]} artist:{artist_names[i]}", type='track')
            if results['tracks']['items']:
                track_id = results['tracks']['items'][0]['id']
                recommendations = sp.recommendations(seed_tracks=[track_id], limit=remaining_slots)
                for track in recommendations['tracks']:
                    song_name = track['name']
                    artist_name = track['artists'][0]['name']

                    # Check if the song is already in the recommended tracks
                    if not any(rec_track['Name'] == song_name and rec_track['Artist'] == artist_name for rec_track in recommended_tracks):
                        recommended_tracks.append({'Name': song_name, 'Artist': artist_name})

                        # Fetch additional details for the song
                        artist_id = track['artists'][0]['id']
                        artist = sp.artist(artist_id)
                        audio_features = sp.audio_features(track['id'])[0]

                        # Check for duplicates in existing songs
                        duplicate_found = any(
                            recommended_song.get('Name') == song_name and recommended_song.get('Artist') == artist_name
                            for recommended_song in recommended_songs.values()
                        )

                        if not duplicate_found:
                            # Prepare the full song data
                            full_song_data = {
                                'Name': track['name'],
                                'Artist': track['artists'][0]['name'],
                                'Album': track['album']['name'],
                                'Release Date': track['album']['release_date'],
                                'Duration (ms)': track['duration_ms'],
                                'Preview URL': track['preview_url'],
                                'Genre': artist['genres'][0] if artist['genres'] else 'Unknown',
                                'Danceability': audio_features['danceability'],
                                'Energy': audio_features['energy'],
                                'Valence': audio_features['valence'],
                                'rating': 0,
                                'dateOfRating': '1-1-2001'
                            }

                            # Add the song to recommended songs and /all-songs
                            recommended_songs_ref.push(full_song_data)
                            add_songs_to_all_songs(full_song_data)  # Add to /all-songs if not a duplicate
                            
                            remaining_slots -= 1
                            if remaining_slots <= 0:
                                break  # Stop if we have enough recommendations

    return jsonify({'success': True, 'recommended_tracks': recommended_tracks})

@app.route('/recommend-friends-songs', methods=['GET'])
def recommend_friends_songs():
    user_id = request.args.get('user_id')

    if not user_id:
        return jsonify({'success': False, 'message': 'User ID is required'}), 400

    # Get friends list
    friends_ref = db.reference(f'/users/{user_id}/friends')
    friends_data = friends_ref.get() or {}
    recommended_songs = []

    # Iterate over friends and check if activityShare is true
    for friend_id, details in friends_data.items():
        if details.get('activityShare'):  # Check if activityShare is true
            friend_songs_ref = db.reference(f'/users/{friend_id}/songs')
            friend_songs = friend_songs_ref.get() or {}
            # Iterate through each song entry in friend_songs
            for song_id, song_data in friend_songs.items():
                # Extract the song_id from the unique key
                recommended_songs.append({'friend_id': friend_id, 'song_id': song_id, **song_data})

    # Sort the recommended_songs by rating
    recommended_songs = sorted(recommended_songs, key=lambda song: song.get('rating', 0), reverse=True)
    
    # Get the top 5 recommended songs
    top_recommended_songs = recommended_songs[:5]
    if top_recommended_songs == []:
            return jsonify({'success': True, 'Make more friends or enable activityShare with friends for friend recommendations.': top_recommended_songs})
    return jsonify({'success': True, 'recommended_songs': top_recommended_songs})

@app.route('/recommend-songs-for-group', methods=['GET'])
def recommend_songs_for_group():
    group_id = request.args.get('group_id').strip()

    # Paths for the group, users, and all songs
    group_path = f'groups/{group_id}'
    users_path = '/users'
    all_songs_path = '/all-songs'

    # Get reference to the group, users, and all songs
    group_ref = db.reference(group_path)
    users_ref = db.reference(users_path)
    all_songs_ref = db.reference(all_songs_path)

    # Fetch the group details, all user's songs, and all songs in the database
    group_details = group_ref.get() or {}
    all_songs = all_songs_ref.get() or {}

    # Initialize variables
    member_ids = group_details.get('Members', [])
    admin_id = group_details.get('Admin')
    if admin_id:
        member_ids.append(admin_id)  # Include admin in the members list
    top_songs = []
    recommended_tracks = []
    max_recommendations_per_song = len(member_ids)

    # Fetch top-rated song for each member
    for member_id in member_ids:
        member_songs_path = f'{users_path}/{member_id}/songs'
        member_songs_ref = db.reference(member_songs_path)
        member_songs = member_songs_ref.get() or {}

        # Find the top-rated song of the user
        top_song = max(member_songs.values(), key=lambda song: int(song.get('rating', 0)), default=None)
        if top_song:
            top_songs.append(top_song)
            # Create a copy of top_song to modify its rating and dateOfRating
            recommended_song = top_song.copy()
            recommended_song['rating'] = 0
            recommended_song['dateOfRating'] = '1-1-2001'
            recommended_tracks.append(recommended_song)
    # For each top song, find 3 similar songs based on Danceability, Energy, and Valence
    for top_song in top_songs:
        similar_songs = []
        profile = {
            'Danceability': top_song['Danceability'],
            'Energy': top_song['Energy'],
            'Valence': top_song['Valence'],
        }

        for song_id, song in all_songs.items():
            # Calculate similarity
            similarity = 1 - mean(abs(song[feature] - profile[feature]) for feature in ['Danceability', 'Energy', 'Valence']) / 3
            
            # If the song is similar enough and not already in the recommended tracks
            if similarity > 0.8 and not any(rec_track['Name'] == song['Name'] and rec_track['Artist'] == song['Artist'] for rec_track in recommended_tracks):
                song['similarity'] = similarity  # Add similarity score for sorting
                similar_songs.append(song)

        # Sort the similar songs based on similarity and take the top N
        similar_songs = sorted(similar_songs, key=lambda x: x['similarity'], reverse=True)[:max_recommendations_per_song]

        # Add similar songs to the recommendations
        for song in similar_songs:
            # Remove the similarity feature from the song
            song.pop('similarity', None)  # The second argument ensures no error if 'similarity' key is not present
            recommended_tracks.append(song)

    return jsonify({'success': True, 'recommended_tracks': recommended_tracks})

@app.route('/export-songs', methods=['GET'])
def export_songs():
    user_id = request.args.get('user_id').strip()
    songs_path = f'/users/{user_id}/songs'
    
    # Get reference to user's songs
    songs_ref = db.reference(songs_path)
    
    # Fetch user's songs
    user_songs = songs_ref.get()
    
    # Check if the user has songs
    if user_songs is None or not user_songs:
        return jsonify({'error': 'No songs found for the user.'}), 404
    
    # Convert to JSON
    json_output = json.dumps(user_songs, indent=4)
    
    # Directory for temporary storage of the file
    directory = tempfile.gettempdir()
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = secure_filename(f'user_{user_id}_songs.json')
    filepath = os.path.join(directory, filename)
    
    with open(filepath, 'w') as file:
        file.write(json_output)
    
    # Send the file for download
    return send_from_directory(directory, filename, as_attachment=True, mimetype='application/json')

@app.after_request
def cleanup(response):
    user_id = request.args.get('user_id', default='').strip()
    filename = secure_filename(f'user_{user_id}_songs.json')
    directory = tempfile.gettempdir()
    filepath = os.path.join(directory, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    return response

if __name__ == '__main__':
    app.run(debug=True)

