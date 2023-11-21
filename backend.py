from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, db, auth
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Initialize Firebase Admin SDK with your credentials
cred = credentials.Certificate("/Users/nupelem/Desktop/tune-mosaic-firebase-adminsdk-twt4o-076c7f19ae.json")
firebase_admin.initialize_app(cred, {'databaseURL': 'https://your-firebase-project-id.firebaseio.com/'})

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

# Endpoint to register a new user
@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        email = data['email']
        password = data['password']
        user_data = data['user_data']

        registration_result = register_user(email, password, user_data)

        if registration_result['success']:
            return jsonify({'success': True, 'message': 'User registered successfully'})
        else:
            return jsonify({'success': False, 'message': registration_result['message']})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# Endpoint to add a single song manually
@app.route('/add-song', methods=['POST'])
def add_single_song():
    try:
        data = request.get_json()
        user_id = data['user_id']
        song_data = data['song_data']

        addition_result = add_song(user_id, song_data)

        if addition_result['success']:
            return jsonify({'success': True, 'message': 'Song added successfully'})
        else:
            return jsonify({'success': False, 'message': addition_result['message']})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# Endpoint to add songs from a text file
@app.route('/add-songs-from-file', methods=['POST'])
def add_songs_from_file_endpoint():
    try:
        data = request.get_json()
        user_id = data['user_id']
        file_path = data['file_path']

        file_addition_result = add_songs_from_file(user_id, file_path)

        if file_addition_result['success']:
            return jsonify({'success': True, 'message': 'Songs added from file successfully'})
        else:
            return jsonify({'success': False, 'message': file_addition_result['message']})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# Endpoint to add songs from a file upload
@app.route('/add-songs-from-upload', methods=['POST'])
def add_songs_from_upload_endpoint():
    try:
        data = request.form
        user_id = data['user_id']

        # Check if the user provided a file in the request
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file provided'})

        file = request.files['file']

        # Check if the file is allowed and add songs
        file_addition_result = add_songs_from_upload(user_id, file)

        if file_addition_result['success']:
            return jsonify({'success': True, 'message': 'Songs added from upload successfully'})
        else:
            return jsonify({'success': False, 'message': file_addition_result['message']})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True)

