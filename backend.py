from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, db, auth
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Initialize Firebase Admin SDK with your credentials
cred = credentials.Certificate("/Users/nupelem/Desktop/tune-mosaic-firebase-adminsdk-twt4o-076c7f19ae.json")
firebase_admin.initialize_app(cred, {'databaseURL': 'https://tune-mosaic.firebaseio.com/'})  # Replace 'tune-mosaic' with your actual Firebase project name

# Define the allowed file extensions and the upload folder
ALLOWED_EXTENSIONS = {'txt', 'csv', 'json'}
UPLOAD_FOLDER = '/path/to/your/upload/folder'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to check if a file has an allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to register a new user and store user data in Firebase
def register_user(email, password, user_data):
    try:
        # Create a new user using Firebase Authentication
        user = auth.create_user(
            email=email,
            password=password,
        )

        # Store user data in the Firebase Realtime Database
        user_id = user.uid
        database = db.reference()
        database.child('users').child(user_id).set(user_data)

        return {'success': True, 'message': 'User registered successfully'}
    except Exception as e:
        return {'success': False, 'message': str(e)}

# Function to add a single song manually
def add_song(user_id, song_data):
    try:
        # Add the song data to the user's collection in the Firebase Realtime Database
        database = db.reference()
        songs_ref = database.child('users').child(user_id).child('songs')
        songs_ref.push().set(song_data)

        return {'success': True, 'message': 'Song added successfully'}
    except Exception as e:
        return {'success': False, 'message': str(e)}

# Function to add songs from a text file
def add_songs_from_file(user_id, file_path):
    try:
        with open(file_path, 'r') as file:
            # Read each line from the file and add the song to the database
            for line in file:
                song_data = {'name': line.strip()}
                add_song(user_id, song_data)

        return {'success': True, 'message': 'Songs added from file successfully'}
    except Exception as e:
        return {'success': False, 'message': str(e)}

# Function to add songs from a file upload
def add_songs_from_upload(user_id, file):
    try:
        if file and allowed_file(file.filename):
            # Save the uploaded file to the specified upload folder
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Read the file and add songs to the database
            add_songs_from_file(user_id, file_path)

            # Remove the uploaded file after processing (optional)
            os.remove(file_path)

            return {'success': True, 'message': 'Songs added from upload successfully'}
        else:
            return {'success': False, 'message': 'Invalid file format'}

    except Exception as e:
        return {'success': False, 'message': str(e)}

# Function to transfer songs from an external database
def transfer_songs_from_external_db(user_id, external_db_info):
    try:
        # Extract necessary information from external_db_info
        # (Replace these placeholders with the actual information needed to connect to the external database)
        external_db_host = external_db_info['host']
        external_db_user = external_db_info['user']
        external_db_password = external_db_info['password']
        external_db_name = external_db_info['db_name']

        # Connect to the external database (use the appropriate library for your chosen database)
        # For example, if using MySQL:
        # import pymysql
        # connection = pymysql.connect(host=external_db_host, user=external_db_user, password=external_db_password, db=external_db_name)
        # cursor = connection.cursor()

        # Fetch song data from the external database
        # Example: Fetch all songs from a hypothetical 'songs' table
        # cursor.execute("SELECT * FROM songs")
        # external_songs = cursor.fetchall()

        # Assuming you have fetched the songs from the external database,
        # you can now add them to the user's collection in the Firebase Realtime Database
        # database = db.reference()
        # songs_ref = database.child('users').child(user_id).child('songs')

        # for external_song in external_songs:
        #     song_data = {'name': external_song['name'], 'artist': external_song['artist'], ...}
        #     songs_ref.push().set(song_data)

        # Close the connection to the external database
        # connection.close()

        return {'success': True, 'message': 'Songs transferred successfully from the external database'}
    except Exception as e:
        return {'success': False, 'message': str(e)}

# Function to rate a song
def rate_song(user_id, song_id, rating):
    try:
        # Update the rating of the song in the Firebase Realtime Database
        database = db.reference()
        song_ref = database.child('users').child(user_id).child('songs').child(song_id)
        song_ref.update({'rating': rating})

        return {'success': True, 'message': 'Song rated successfully'}
    except Exception as e:
        return {'success': False, 'message': str(e)}

# Endpoint to transfer songs from an external database
@app.route('/transfer-songs-from-external-db', methods=['POST'])
def transfer_songs_from_external_db_endpoint():
    try:
        data = request.get_json()
        user_id = data['user_id']
        external_db_info = data['external_db_info']

        transfer_result = transfer_songs_from_external_db(user_id, external_db_info)

        if transfer_result['success']:
            return jsonify({'success': True, 'message': 'Songs transferred successfully from the external database'})
        else:
            return jsonify({'success': False, 'message': transfer_result['message']})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# Endpoint to rate a song
@app.route('/rate-song', methods=['POST'])
def rate_song_endpoint():
    try:
        data = request.get_json()
        user_id = data['user_id']
        song_id = data['song_id']
        rating = data['rating']

        rating_result = rate_song(user_id, song_id, rating)

        if rating_result['success']:
            return jsonify({'success': True, 'message': 'Song rated successfully'})
        else:
            return jsonify({'success': False, 'message': rating_result['message']})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
