from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, db, auth
import os
from werkzeug.utils import secure_filename
import requests
from base64 import b64encode
import json
from datetime import datetime

client_id = '0effabc56654497f80d57c69729f0161'
client_secret = 'f2bbcaf09cb643d789d384ca508f8f70'

# Encode as Base64
credentialsSpotify = b64encode(f"{client_id}:{client_secret}".encode()).decode('utf-8')

headers = {
    'Authorization': f'Basic {credentialsSpotify}',
    'Content-Type': 'application/x-www-form-urlencoded'
}

data = {
    'grant_type': 'client_credentials'
}

response = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=data)

access_token = response.json().get('access_token')

app = Flask(__name__)
CORS(app)

# Initialize Firebase Admin SDK with your credentials
cred = credentials.Certificate("/Users/zeynep/Downloads/tune-mosaic-firebase-adminsdk-twt4o-1a651b2af6.json")
firebase_admin.initialize_app(cred, {'databaseURL': 'https://tune-mosaic-default-rtdb.firebaseio.com/'})  # Replace 'tune-mosaic' with your actual Firebase project name

@app.route('/verify-token', methods=['POST'])
def verify_token():
    token = request.json.get('token')
    try:
        # Verify the token with Firebase Admin SDK
        decoded_token = auth.verify_id_token(token)
        return jsonify({'uid': decoded_token['uid']})
    except Exception as e:
        return jsonify({'error': str(e)}), 401

@app.route('/add-song', methods=['POST'])
def add_song():
    data = request.get_json()
    user_id = data['user_id']
    song_data = data['song_data']

    ref = db.reference(f'/users/{user_id}/songs')
    ref.push(song_data)

    return jsonify({'success': True, 'message': 'Song added successfully'})

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

    # Get the user_id from the request (you can pass it as a header or a parameter)
    user_id = request.form.get('user_id')

    # Add each song data to the user's data
    ref = db.reference(f'/users/{user_id}/songs')
    for song_data in song_data_list:
        ref.push(song_data)

    return jsonify({'success': True, 'message': 'Songs added successfully'})

@app.route('/rate-song', methods=['POST'])
def rate_song():
    data = request.get_json()
    user_id = data['user_id']
    song_id = data['song_id']  # Unique ID of the song
    new_rating = data['rating']

    # Reference to the specific song using the song ID
    ref = db.reference(f'/users/{user_id}/songs/{song_id}')

    try:
        # Check if the song exists
        if ref.get() is None:
            return jsonify({'success': False, 'message': 'Song not found'})

        # Update the song's rating and date of rating
        ref.update({
            'rating': new_rating,
            'dateOfRating': datetime.now().strftime('%Y-%m-%d')
        })

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

if __name__ == '__main__':
    app.run(debug=True)
