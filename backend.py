from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth

app = Flask(__name__)

# Initialize Firebase Admin SDK with your credentials
cred = credentials.Certificate("/Users/zeynep/Desktop/tune-mosaic-firebase-adminsdk-twt4o-bc55e51dbc.json")
firebase_admin.initialize_app(cred)

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
        database.child('users').child(user_id).set(user_data)

        return {'success': True, 'message': 'User registered successfully'}
    except Exception as e:
        return {'success': False, 'message': str(e)}

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

if __name__ == '__main__':
    app.run(debug=True)
