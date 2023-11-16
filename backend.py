from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
from firebase_admin import db

app = Flask(__name__)

# Initialize Firebase Admin SDK with your credentials

cred = credentials.Certificate("/Users/zeynep/Desktop/tune-mosaic-firebase-adminsdk-twt4o-1a651b2af6.json") 
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://tune-mosaic-default-rtdb.firebaseio.com/'
})

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
        database = firebase_admin.db.reference()
        database.child('users').child(user_id).set( user_data)

        return {'success': True, 'message': 'User registered successfully'}
    except Exception as e:
        return {'success': False, 'message': str(e)}

def retrieve_user_data(email):
    ref = db.reference('users')
    users = ref.order_by_child('email').equal_to(email).get()

    for user_id, user_data in users.items():
        if user_data['email'] == email:
            return user_data

    return None  # User not found
    
def login_user(email, password):
    try:
        # Retrieve the user by email
        user = auth.get_user_by_email(email)

        # Retrieve and verify the hashed password from your database
        user_data = retrieve_user_data(email)  # Implement this function
        if bcrypt.checkpw(password.encode('utf-8'), user_data['hashed_password'].encode('utf-8')):
            token = auth.create_custom_token(user.uid)
            return {'success': True, 'message': 'User logged in successfully', 'token': token.decode('utf-8')}
        else:
            return {'success': False, 'message': 'Invalid password'}
    except Exception as e:
        return {'success': False, 'message': str(e)}

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data['email']
        password = data['password']

        login_result = login_user(email, password)

        return jsonify(login_result)

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

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

# Function to add a single song manually
def add_song(user_id, song_data):
    try:
        # Add the song data to the user's collection in the Firebase Realtime Database
        database = firebase_admin.db.reference()
        songs_ref = database.child('users').child(user_id).child('songs')
        songs_ref.push().set(song_data)

        return {'success': True, 'message': 'Song added successfully'}
    except Exception as e:
        return {'success': False, 'message': str(e)}

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

if __name__ == '__main__':
    app.run(debug=True)
