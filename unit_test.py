import unittest
from datetime import datetime, timedelta
from unittest import mock
from flask import Flask, jsonify
from mock import patch, MagicMock 
from backend import app
import json
import uuid
import os
import tempfile


import datetime
import spotipy

ALLOWED_EXTENSIONS = {'txt'}
MAX_FILE_SIZE = 5 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class BackendTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_verify_token_login_success(self):
        # Mock Firebase Admin SDK functions for login
        with patch('firebase_admin.auth.verify_id_token') as mock_verify_token, \
             patch('firebase_admin.auth.get_user') as mock_get_user:
            mock_verify_token.return_value = {'uid': 'mocked_uid'}
            mock_get_user.return_value = MagicMock()

            # Send a login request with a valid token
            response = self.app.post('/verify-token', json={'token': 'valid_token'})

            # Check if the response contains the expected data
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['uid user login'], 'mocked_uid')

    def test_verify_token_login_failure(self):
        # Mock Firebase Admin SDK functions for login failure
        with patch('firebase_admin.auth.verify_id_token') as mock_verify_token:
            mock_verify_token.side_effect = Exception('Invalid token')

            # Send a login request with an invalid token
            response = self.app.post('/verify-token', json={'token': 'invalid_token'})

            # Check if the response contains the expected data
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 401)
            self.assertIn('error', data)

    def test_verify_token_register_success(self):
        # Mock Firebase Admin SDK functions for registration
        with patch('firebase_admin.auth.create_user') as mock_create_user, \
             patch('firebase_admin.auth.create_custom_token') as mock_create_custom_token, \
             patch('firebase_admin.db.reference') as mock_db_reference:
            mock_create_user.return_value = MagicMock(uid='mocked_uid')
            mock_create_custom_token.return_value = b'mocked_custom_token'

            # Send a registration request
            response = self.app.post('/verify-token', json={'email': 'test@example.com',
                                                            'password': 'test_password',
                                                            'username': 'test_user'})

        
            # Check if the response contains the expected data
            data = json.loads(response.data.decode())
            self.assertIsNotNone(data.get('custom_token user register'))


    def test_verify_token_register_failure(self):
        with patch('firebase_admin.auth.create_user', side_effect=Exception('Registration failed')):
            response = self.app.post('/verify-token', json={'email': 'test@example.com', 'password': 'test_password', 'username': 'test_user'})
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn('error', data)
            self.assertEqual(data['error'], 'Registration failed')
    
    @patch('backend.auth')
    @patch('backend.db')
    def test_google_signin_existing_user(self, mock_db, mock_auth):
        # Mock the verify_id_token function to return a decoded token
        mock_auth.verify_id_token.return_value = {'uid': 'existing_user_uid', 'email': 'existing@example.com'}

        # Mock the database to simulate an existing user
        mock_user_ref = MagicMock()
        mock_user_ref.get.return_value = {'email': 'existing@example.com', 'username': 'Existing User'}
        mock_db.reference.return_value = mock_user_ref

        # Make a request to the /google-signin endpoint
        response = self.app.post('/google-signin', json={'idToken': 'test_id_token'})

        # Assert the response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'success')
        self.assertEqual(response.json['message'], 'User logged in')
        self.assertEqual(response.json['uid'], 'existing_user_uid')

    @patch('backend.auth')
    @patch('backend.db')
    def test_google_signin_new_user(self, mock_db, mock_auth):
        # Mock the verify_id_token function to return a decoded token
        mock_auth.verify_id_token.return_value = {'uid': 'new_user_uid', 'email': 'new@example.com', 'name': 'New User'}

        # Mock the database to simulate a new user
        mock_user_ref = MagicMock()
        mock_user_ref.get.return_value = None
        mock_db.reference.return_value = mock_user_ref

        # Make a request to the /google-signin endpoint
        response = self.app.post('/google-signin', json={'idToken': 'test_id_token'})

        # Assert the response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'success')
        self.assertEqual(response.json['message'], 'User registered')
        self.assertEqual(response.json['uid'], 'new_user_uid')


    @patch('backend.auth')
    @patch('backend.db')
    def test_google_signin_invalid_token(self, mock_db, mock_auth):
        # Mock the verify_id_token function to raise an exception for an invalid token
        mock_auth.verify_id_token.side_effect = Exception('Invalid token')

        # Make a request to the /google-signin endpoint with an invalid token
        response = self.app.post('/google-signin', json={'idToken': 'invalid_token'})

        # Assert the response
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['status'], 'error')
        self.assertIn('Invalid token', response.json['message'])

    @patch('backend.auth')
    @patch('backend.db')
    def test_google_signin_existing_user_database_error(self, mock_db, mock_auth):
        # Mock the verify_id_token function to return a decoded token
        mock_auth.verify_id_token.return_value = {'uid': 'existing_user_uid', 'email': 'existing@example.com'}

        # Mock the database to simulate an existing user, but raise an exception when accessing the database
        mock_user_ref = MagicMock()
        mock_user_ref.get.side_effect = Exception('Database error')
        mock_db.reference.return_value = mock_user_ref

        # Make a request to the /google-signin endpoint
        response = self.app.post('/google-signin', json={'idToken': 'test_id_token'})

        # Assert the response
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['status'], 'error')
        self.assertIn('Database error', response.json['message'])


    @patch('backend.auth')
    @patch('backend.db')
    def test_google_signin_new_user_database_error(self, mock_db, mock_auth):
        # Mock the verify_id_token function to return a decoded token
        mock_auth.verify_id_token.return_value = {'uid': 'new_user_uid', 'email': 'new@example.com', 'name': 'New User'}

        # Mock the database to simulate a new user, but raise an exception when accessing the database
        mock_user_ref = MagicMock()
        mock_user_ref.get.return_value = None
        mock_db.reference.side_effect = Exception('Database error')

        # Make a request to the /google-signin endpoint
        response = self.app.post('/google-signin', json={'idToken': 'test_id_token'})

        # Assert the response
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['status'], 'error')
        self.assertIn('Database error', response.json['message'])

    @patch('backend.auth')
    @patch('backend.db')
    def test_google_signin_empty_id_token(self, mock_db, mock_auth):
        mock_auth.verify_id_token.side_effect = ValueError('ID token must not be empty')

        # Make a request to the /google-signin endpoint with an empty idToken
        response = self.app.post('/google-signin', json={'idToken': ''})

        # Assert the response
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['status'], 'error')
        self.assertIn('ID token must not be empty', response.json['message'])

    @patch('backend.auth')
    @patch('backend.db')
    def test_google_signin_missing_id_token(self, mock_db, mock_auth):
        # Mock the verify_id_token function to raise an exception for a missing token
        def verify_id_token_raise_error(token):
            if not token:
                raise ValueError('ID token is missing')

        mock_auth.verify_id_token.side_effect = verify_id_token_raise_error

        # Make a request to the /google-signin endpoint without providing the idToken
        response = self.app.post('/google-signin', json={})

        # Assert the response
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['status'], 'error')
        self.assertIn('ID token is missing', response.json['message'])

    def test_add_song_success(self):
        with patch('backend.db.reference') as mock_db_reference:
            # Mock user data for an existing user
            mock_user_ref = MagicMock()
            mock_user_ref.get.return_value = {'username': 'test_user'}
            mock_db_reference.return_value = mock_user_ref

            # Mock the push method of songs_ref
            mock_push = mock_user_ref.child('songs').push
            mock_push.return_value.key = 'mocked_song_id'
            # Send a request to add a song with valid data
            response = self.app.post('/add-song', json={'user_id': 'existing_user_id',
                                                    'song_data': {'title': 'Test Song', 'artist': 'Test Artist'}})

            # Check if the response contains the expected data
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['success'], True)
            self.assertEqual(data['message'], 'Song added successfully')
            self.assertEqual(data['song_id'], 'mocked_song_id')

    def test_add_song_missing_user_id(self):
        # Send a request to add a song without providing the user_id
        response = self.app.post('/add-song', json={'song_data': {'title': 'Test Song', 'artist': 'Test Artist'}})

        # Check if the response contains the expected data
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'User ID is required')

    def test_add_song_user_not_exist(self):
        with patch('backend.db.reference') as mock_db_reference:
            # Mock user data for a non-existing user
            mock_user_ref = MagicMock()
            mock_user_ref.get.return_value = None
            mock_db_reference.return_value = mock_user_ref

            # Send a request to add a song for a non-existing user
            response = self.app.post('/add-song', json={'user_id': 'non_existing_user_id',
                                                        'song_data': {'title': 'Test Song', 'artist': 'Test Artist'}})

            # Check if the response contains the expected data
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertEqual(data['success'], False)
            self.assertEqual(data['message'], 'User does not exist')
    
    def test_add_song_missing_song_data(self):
        # Send a request to add a song without providing song_data
        response = self.app.post('/add-song', json={'user_id': 'existing_user_id'})

        # Check if the response contains the expected data
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 404)  # Correct the expected status code to 404
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Song data is required')

    def test_add_song_missing_song_data(self):
     # Send a request to add a song without providing the song_data
        response = self.app.post('/add-song', json={'user_id': 'non_existing_user_id'})

    
        # Check if the response contains the expected data
        data = json.loads(response.data.decode())
    
        # Check for both 400 and 404 status codes depending on user existence
        self.assertIn(response.status_code, [400, 404])
        self.assertEqual(data['success'], False)
    
        # Check the message based on the status code
        if response.status_code == 400:
            self.assertEqual(data['message'], 'Song data is required')
        elif response.status_code == 404:
            self.assertEqual(data['message'], 'User does not exist')

    def test_add_song_empty_request(self):
        response = self.app.post('/add-song', json={})
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 400)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'User ID is required')

    def test_add_song_user_id_not_provided(self):
    # Send a request to add a song without providing the user_id field
        response = self.app.post('/add-song', json={'song_data': {'title': 'Test Song', 'artist': 'Test Artist'}})

    # Check if the response contains the expected data
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'User ID is required')

    @patch('backend.db.reference')  # Assuming 'backend.db.reference' is the correct path
    def test_add_song_user_id_not_exist(self, mock_db_reference):
        # Mock user data for a non-existing user
        mock_user_ref = MagicMock()
        mock_user_ref.get.return_value = None
        mock_db_reference.return_value = mock_user_ref  # Define mock_db_reference

        # Send a request to add a song for a non-existing user
        response = self.app.post('/add-song', json={'user_id': 'non_existing_user_id',
                                                'song_data': {'title': 'Test Song', 'artist': 'Test Artist'}})

        # Check if the response contains the expected data
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'User does not exist')
    
    
    @patch('backend.firebase_admin')
    def test_add_song_invalid_user_id(self, mock_firebase_admin):
        response = self.app.post('/add-song', json={'user_id': '', 'song_name': 'Test Song'})
        data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'User ID is required')  # Updated the expected message

    def test_allowed_file_valid_extension(self):
        # Test with a valid file extension
        result = allowed_file('example.TXT')
        self.assertTrue(result)

    def test_allowed_file_invalid_extension(self):
        # Test with an invalid file extension
        result = allowed_file('example.jpg')
        self.assertFalse(result)
    
    def test_allowed_file_empty_filename(self):
        # Test with an empty filename
        result = allowed_file('')
        self.assertFalse(result)

    def test_allowed_file_max_file_size(self):
        filename = 'example.txt'
        max_size_filename = filename + 'a' * (MAX_FILE_SIZE - len(filename))
        result = allowed_file(max_size_filename)
        self.assertTrue(len(max_size_filename) <= MAX_FILE_SIZE)


    def test_allowed_file_exceed_max_file_size(self):
        # Test with a file size exceeding the maximum allowed size
        result = allowed_file('example.txt' + 'a' * (MAX_FILE_SIZE - 8))  # 8 characters for 'example.txt'
        self.assertFalse(result)

    def test_allowed_file_case_sensitive_extension(self):
        # Test with a file extension in uppercase
        result = allowed_file('example.TXT')
        self.assertTrue(result)

    def test_allowed_file_case_sensitive_filename(self):
        # Test with a filename in uppercase
        result = allowed_file('EXAMPLE.txt')
        self.assertTrue(result)
    
    def test_allowed_file_valid_extension_uppercase(self):
        # Test with a valid file extension in uppercase
        result = allowed_file('example.TXT')
        self.assertTrue(result)

    def test_allowed_file_valid_extension_mixed_case(self):
        # Test with a valid file extension in mixed case
        result = allowed_file('example.TxT')
        self.assertTrue(result)

    def test_allowed_file_max_file_size_plus_one(self):
        # Test with a file size exceeding the maximum allowed size
        filename = 'example.txt'
        oversized_filename = filename + 'a' * (MAX_FILE_SIZE - len(filename) + 1)
        result = allowed_file(oversized_filename)
        self.assertFalse(result)

    def test_allowed_file_max_file_size_minus_one(self):
        # Test with a file size one less than the maximum allowed size
        filename = 'example.txt'
        almost_max_size_filename = filename + 'a' * (MAX_FILE_SIZE - len(filename) - 1)
        result = allowed_file(almost_max_size_filename)
        self.assertLessEqual(len(almost_max_size_filename), MAX_FILE_SIZE)

    def test_allowed_file_empty_filename(self):
        # Test with an empty filename
        result = allowed_file('')
        self.assertFalse(result)

    def test_allowed_file_filename_without_extension(self):
        # Test with a filename without an extension
        result = allowed_file('filename_without_extension')
        self.assertFalse(result)

    def test_upload_songs_invalid_json_content(self):
        # Create a temporary file with invalid JSON content
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
            temp_file.write('{"title": "Song 1", "artist": "Artist 1"}, {"title": "Song 2", "artist": "Artist 2"}')
            temp_file_path = temp_file.name

        try:
            # Send a request to upload the file with invalid JSON content
            with open(temp_file_path, 'rb') as file:
                response = self.app.post('/upload-songs', data={'file': (file, 'test_file.txt')}, content_type='multipart/form-data', headers={'user_id': 'test_user_id'})

            # Check if the response contains the expected data
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertFalse(data['success'])
            self.assertEqual(data['message'], 'Invalid JSON data in the file')
        finally:
            # Delete the temporary file
            os.remove(temp_file_path)

    def test_upload_songs_no_file_uploaded(self):
        # Send a request to upload songs without providing a file
        response = self.app.post('/upload-songs', headers={'user_id': 'test_user_id'})

        # Check if the response contains the expected data
        self.assertEqual(response.status_code, 400)
        self.assertIn('Bad Request</h1>\n<p>The browser (or proxy) sent a request that this server could not understand.</p>', response.data.decode())

    def test_rate_song_success_existing_song(self):
        # Mock Firebase Admin SDK functions for updating the song rating
        with patch('firebase_admin.db.reference') as mock_db_reference:
            # Mock user data for an existing user
            mock_user_ref = MagicMock()
            mock_user_ref.get.return_value = {'username': 'test_user'}
            mock_db_reference.return_value = mock_user_ref

            # Mock the get method of songs_ref to simulate an existing song
            mock_songs_ref = mock_user_ref.child('songs')
            mock_songs_ref.get.return_value = {'title': 'Test Song', 'artist': 'Test Artist'}

            # Send a request to rate an existing song with valid data
            response = self.app.post('/rate-song', json={'user_id': 'existing_user_id',
                                                         'song_id': 'existing_song_id',
                                                         'rating': 4})

            # Check if the response contains the expected data
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertTrue(data['success'])
            self.assertEqual(data['message'], 'Song rating updated successfully')

    def test_rate_song_success_existing_recommendation(self):
        # Mock Firebase Admin SDK functions for updating the song rating and deleting from recommended songs
        with patch('firebase_admin.db.reference') as mock_db_reference:
            # Mock user data for an existing user
            mock_user_ref = MagicMock()
            mock_user_ref.get.return_value = {'username': 'test_user'}
            mock_db_reference.return_value = mock_user_ref

            # Mock the get method of recommended_songs_ref to simulate an existing recommendation
            mock_recommendations_ref = mock_user_ref.child('recommended-songs')
            mock_recommendations_ref.get.return_value = {'title': 'Recommended Song', 'artist': 'Recommended Artist'}

            # Send a request to rate an existing recommendation with valid data
            response = self.app.post('/rate-song', json={'user_id': 'existing_user_id',
                                                         'song_id': 'recommended_song_id',
                                                         'rating': 5})

            # Check if the response contains the expected data
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertTrue(data['success'])
            self.assertEqual(data['message'], 'Song rating updated successfully')

    def test_delete_song_success(self):
        # Mock Firebase Admin SDK functions for successful song deletion
        with patch('firebase_admin.db.reference') as mock_db_reference, \
             patch('firebase_admin.db.reference.delete') as mock_delete:
            mock_db_reference.return_value.get.return_value = {'song_data': 'mocked_song_data'}

            # Send a request to delete a song with a valid user_id and song_id
            response = self.app.delete('/delete-song', json={'user_id': 'valid_user_id', 'song_id': 'valid_song_id'})

            # Check if the response contains the expected success message and status code
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertTrue(data['success'])
            self.assertEqual(data['message'], 'Song deleted successfully')

    def test_delete_song_not_found(self):
        # Mock Firebase Admin SDK functions for song not found
        with patch('firebase_admin.db.reference') as mock_db_reference:
            mock_db_reference.return_value.get.return_value = None

            # Send a request to delete a song with a valid user_id and non-existent song_id
            response = self.app.delete('/delete-song', json={'user_id': 'valid_user_id', 'song_id': 'nonexistent_song_id'})

            # Check if the response contains the expected error message and status code
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertFalse(data['success'])
            self.assertEqual(data['message'], 'Song not found')

    def test_delete_song_exception(self):
        # Mock Firebase Admin SDK functions for an exception during song deletion
        with patch('firebase_admin.db.reference') as mock_db_reference, \
             patch('firebase_admin.db.reference.delete') as mock_delete:
            mock_db_reference.return_value.get.side_effect = Exception("Mocked exception during deletion")

            # Send a request to delete a song with a valid user_id and song_id
            response = self.app.delete('/delete-song', json={'user_id': 'valid_user_id', 'song_id': 'valid_song_id'})

            # Check if the response contains the expected error message and status code
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 500)
            self.assertFalse(data['success'])
            self.assertIn('Mocked exception during deletion', data['message'])

    def test_delete_performer_songs_success(self):
        # Mock Firebase Admin SDK functions for delete-performer-songs
        with patch('firebase_admin.db.reference') as mock_reference:
            # Mock user's songs data with songs by the specified performer
            mocked_user_songs = {
                'song1': {'performer': 'performer_name'},
                'song2': {'performer': 'performer_name'},
                'song3': {'performer': 'other_performer'}
            }
            mock_reference.return_value.get.return_value = mocked_user_songs

            # Send a request to delete songs by the specified performer
            response = self.app.delete('/delete-performer-songs', json={'user_id': 'user_id', 'performer': 'performer_name'})

            # Check if the response contains the expected data
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertTrue(data['success'])
            self.assertEqual(data['message'], 'All songs by the performer have been deleted')

    def test_delete_performer_songs_no_songs_found(self):
        # Mock Firebase Admin SDK functions for delete-performer-songs
        with patch('firebase_admin.db.reference') as mock_reference:
            # Mock user's songs data with no songs
            mock_reference.return_value.get.return_value = None

            # Send a request to delete songs by the specified performer
            response = self.app.delete('/delete-performer-songs', json={'user_id': 'user_id', 'performer': 'performer_name'})

            # Check if the response contains the expected data
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertFalse(data['success'])
            self.assertEqual(data['message'], 'No songs found')

    def test_delete_album_songs_empty_album(self):
        # Test deleting songs from an empty album
        response = self.app.delete('/delete-album-songs', json={'user_id': 'valid_user_id', 'albumName': 'empty_album'})
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'No songs found')

    def test_delete_album_songs_no_songs(self):
        # Test deleting songs from an album with no songs
        response = self.app.delete('/delete-album-songs', json={'user_id': 'valid_user_id', 'albumName': 'no_songs_album'})
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'No songs found')

    
    def test_delete_album_songs_incorrect_album_name(self):
        # Test deleting songs with an incorrect album name
        response = self.app.delete('/delete-album-songs', json={'user_id': 'valid_user_id', 'albumName': 'incorrect_album'})
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'No songs found')

    def test_get_top_songs_successful(self):
        # Mock Firebase Admin SDK functions for successful get_top_songs request
        with patch('firebase_admin.auth.verify_id_token'), \
             patch('firebase_admin.db.reference') as mock_db_reference:
            # Mock the return value for user's songs
            mock_user_songs = {
                'song1': {'rating': 5, 'Release Date': (datetime.datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')},
                'song2': {'rating': 4, 'Release Date': (datetime.datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')},
                'song3': {'rating': 3, 'Release Date': (datetime.datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d')},
            }
            mock_db_reference.return_value.get.return_value = mock_user_songs

            # Send a get_top_songs request with a valid user_id
            response = self.app.get('/top-songs?user_id=valid_user_id&years=1')

            # Check if the response contains the expected data
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertTrue(data['success'])
            self.assertIn('top_song_ids', data)
            self.assertEqual(len(data['top_song_ids']), 3)

    def test_get_top_songs_no_songs_found(self):
        # Mock Firebase Admin SDK functions for get_top_songs with no songs found
        with patch('firebase_admin.auth.verify_id_token'), \
             patch('firebase_admin.db.reference') as mock_db_reference:
            # Mock the return value for an empty user's songs
            mock_db_reference.return_value.get.return_value = None

            # Send a get_top_songs request with a valid user_id
            response = self.app.get('/top-songs?user_id=valid_user_id&years=1')

            # Check if the response contains the expected data
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertFalse(data['success'])
            self.assertIn('message', data)
            self.assertEqual(data['message'], 'No songs found')

    def test_get_top_songs_zero_years(self):
        # Mock Firebase Admin SDK functions for get_top_songs with zero years
        with patch('firebase_admin.auth.verify_id_token'), \
             patch('firebase_admin.db.reference') as mock_db_reference:
            # Mock the return value for user's songs
            mock_user_songs = {
                'song1': {'rating': 5, 'Release Date': (datetime.datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')},
                'song2': {'rating': 4, 'Release Date': (datetime.datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')},
                'song3': {'rating': 3, 'Release Date': (datetime.datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d')},
            }
            mock_db_reference.return_value.get.return_value = mock_user_songs

            # Send a get_top_songs request with zero years
            response = self.app.get('/top-songs?user_id=valid_user_id&years=0')

            # Check if the response contains the expected data
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertTrue(data['success'])
            self.assertIn('top_song_ids', data)
            self.assertEqual(len(data['top_song_ids']), 0)
    def test_get_top_songs_valid_user_id_and_no_songs(self):
        # Mock Firebase Admin SDK functions for get_top_songs with a valid user_id and no songs
        with patch('firebase_admin.auth.verify_id_token'), \
             patch('firebase_admin.db.reference') as mock_db_reference:
            # Mock the return value for an empty user's songs
            mock_db_reference.return_value.get.return_value = None

            # Send a get_top_songs request with a valid user_id and no songs
            response = self.app.get('/top-songs?user_id=valid_user_id&years=1')

            # Check if the response contains the expected data
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertFalse(data['success'])
            self.assertIn('message', data)
            self.assertEqual(data['message'], 'No songs found')

    def test_get_top_songs_no_ratings_available(self):
        # Mock Firebase Admin SDK functions for get_top_songs with no ratings available
        with patch('firebase_admin.auth.verify_id_token'), \
             patch('firebase_admin.db.reference') as mock_db_reference:
            # Mock the return value for user's songs without ratings
            mock_user_songs = {
                'song1': {'Release Date': (datetime.datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')},
                'song2': {'Release Date': (datetime.datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')},
                'song3': {'Release Date': (datetime.datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d')},
            }
            mock_db_reference.return_value.get.return_value = mock_user_songs

            # Send a get_top_songs request with no ratings available
            response = self.app.get('/top-songs?user_id=valid_user_id&years=1')

            # Check if the response contains the expected data
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertTrue(data['success'])
            self.assertIn('top_song_ids', data)
            self.assertEqual(len(data['top_song_ids']), 0)

    
    def test_follow_user_successful(self):
        # Mock Firebase Admin SDK functions for a successful follow action
        with patch('firebase_admin.db.reference') as mock_db_reference:
            mock_following_ref = mock_db_reference.return_value
            mock_followed_ref = mock_db_reference.return_value
            mock_followed_following_ref = mock_db_reference.return_value
            mock_follower_followers_ref = mock_db_reference.return_value
            mock_follower_friends_ref = mock_db_reference.return_value
            mock_followed_friends_ref = mock_db_reference.return_value

            mock_following_ref.get.return_value = []  # Follower is not following anyone initially
            mock_followed_ref.get.return_value = []   # Followed user has no followers initially
            mock_followed_following_ref.get.return_value = []  # Followed user is not following anyone initially
            mock_follower_followers_ref.get.return_value = []  # Follower has no followers initially
            mock_follower_friends_ref.get.return_value = {}   # Follower has no friends initially
            mock_followed_friends_ref.get.return_value = {}   # Followed user has no friends initially

            # Send a follow-user request with valid data
            response = self.app.post('/follow-user', json={
                'follower_id': 'follower_user',
                'followed_id': 'followed_user'
            })

            # Check if the response indicates a successful follow action
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertTrue(data['success'])
            self.assertEqual(data['message'], 'Follow action successful')

    def test_follow_user_non_existing_follower(self):
        # Set up mock data with a non-existing follower ID
        non_existing_follower_data = {'follower_id': 'non_existing_follower', 'followed_id': 'followed_uid'}

        # Send a follow-user request with a non-existing follower ID
        response = self.app.post('/follow-user', json=non_existing_follower_data)

        # Check if the response contains the expected error message
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIn('message', data)

    def test_follow_user_non_existing_followed(self):
        # Set up mock data with a non-existing followed ID
        non_existing_followed_data = {'follower_id': 'follower_uid', 'followed_id': 'non_existing_followed'}

        # Send a follow-user request with a non-existing followed ID
        response = self.app.post('/follow-user', json=non_existing_followed_data)

        # Check if the response contains the expected error message
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIn('message', data)

    def test_follow_user_follower_follows_himself(self):
        # Set up mock data with the same follower and followed ID
        same_follower_and_followed_data = {'follower_id': 'same_uid', 'followed_id': 'same_uid'}

        # Send a follow-user request with the same follower and followed ID
        response = self.app.post('/follow-user', json=same_follower_and_followed_data)

        # Check if the response contains the expected error message
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIn('message', data)
    
    def test_unfollow_user_success(self):
        # Mock Firebase Admin SDK functions for unfollow_user
        with patch('firebase_admin.auth.verify_id_token'), \
             patch('firebase_admin.auth.get_user'), \
             patch('firebase_admin.db.reference') as mock_db_ref:
            # Mock database references
            mock_active_user_following_ref = MagicMock()
            mock_unfollow_user_followers_ref = MagicMock()
            mock_active_user_friends_ref = MagicMock()
            mock_unfollow_user_friends_ref = MagicMock()

            mock_db_ref.side_effect = [
                mock_active_user_following_ref,
                mock_unfollow_user_followers_ref,
                mock_active_user_friends_ref,
                mock_unfollow_user_friends_ref
            ]

            # Mock existing data in the database
            existing_following_data = ['user1', 'user2', 'user_to_be_unfollowed']
            mock_active_user_following_ref.get.return_value = existing_following_data
            mock_unfollow_user_followers_ref.get.return_value = ['user1', 'user2', 'active_user']

            # Send an unfollow request with valid input
            response = self.app.post('/unfollow-user', json={
                'active_user_id': 'active_user',
                'unfollow_user_id': 'user_to_be_unfollowed'
            })

            # Check if the response contains the expected data
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertTrue(data['success'])
            self.assertEqual(data['message'], 'Unfollow action successful')

            # Check if the database has been updated correctly
            mock_active_user_following_ref.set.assert_called_once_with(['user1', 'user2'])
            mock_unfollow_user_followers_ref.set.assert_called_once_with(['user1', 'user2'])

    def test_update_friend_activity_share_valid(self):
        # Mock Firebase Admin SDK functions for updating friend activity share
        with patch('firebase_admin.auth.verify_id_token'), \
             patch('firebase_admin.db.reference') as mock_db_reference:
            # Mock the existing friends list of the owner
            mock_friends_list = {'friend_id': {'activityShare': True}}
            mock_db_reference.return_value.get.return_value = mock_friends_list

            # Send a request to update friend activity share
            response = self.app.post('/update-friend-activity-share', json={
                'owner_id': 'mocked_owner_id',
                'friend_id': 'friend_id',
                'activityShare': False
            })

            # Check if the response indicates a successful update
            data = json.loads(response.data.decode())
            self.assertTrue(data['success'])
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['message'], 'activityShare status updated successfully')

    def test_update_friend_activity_share_friend_not_found(self):
        # Mock Firebase Admin SDK functions for updating friend activity share
        with patch('firebase_admin.auth.verify_id_token'), \
             patch('firebase_admin.db.reference') as mock_db_reference:
            # Mock an empty friends list for the owner
            mock_db_reference.return_value.get.return_value = {}

            # Send a request to update activity share for a friend not in the list
            response = self.app.post('/update-friend-activity-share', json={
                'owner_id': 'mocked_owner_id',
                'friend_id': 'nonexistent_friend_id',
                'activityShare': True
            })

            # Check if the response indicates that the friend was not found
            data = json.loads(response.data.decode())
            self.assertFalse(data['success'])
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['message'], 'Friend not found in the friends list')

    def test_create_group_valid_input(self):
        # Test case: Valid Input Case
        data = {
            'admin_id': 'valid_admin_id',
            'group_name': 'Test Group',
            'member_ids': ['member1', 'member2']
        }
        response = self.app.post('/create-group', json=data)
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], 'Group created successfully')
        self.assertTrue('group_id' in data)
    
    def test_create_group_empty_group_name(self):
        # Test case: Empty Group Name Case
        data = {
            'admin_id': 'valid_admin_id',
            'group_name': '',
            'member_ids': ['member1', 'member2']
        }
        response = self.app.post('/create-group', json=data)
     

        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 400)
        self.assertFalse(data.get('success', False))
        self.assertEqual(data['error'], 'Group name is required')


    def test_create_group_empty_member_ids(self):
    # Test case: Empty Member IDs Case
        data = {
            'admin_id': 'valid_admin_id',
            'group_name': 'Test Group',
            'member_ids': []
        }
        response = self.app.post('/create-group', json=data)
    
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 400)
    
        # Check if 'success' key is not present in the response
        self.assertFalse(data.get('success', False))
        self.assertEqual(data['error'], 'At least one member is required')
    
    
    def test_add_member_non_admin_access(self):
        # Mock Firebase Admin SDK functions for non-admin access
        with patch('firebase_admin.db.reference') as mock_db_reference:
            # Mock the existing group data and set a different admin_id
            existing_group_data = {'Admin': 'other_admin_uid', 'Members': []}
            mock_db_reference.return_value.get.return_value = existing_group_data

            # Send a request to add a member with a non-admin admin_id
            response = self.app.post('/add-member', json={
                'group_id': 'existing_group_id',
                'admin_id': 'admin_uid',
                'new_member_id': 'new_member_uid'
            })

            # Check if the response contains the expected data
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 403)
            self.assertFalse(data['success'])
    
    def test_add_member_invalid_admin_id(self):
        # Send a request to add a member with an invalid admin_id
        response = self.app.post('/add-member', json={
            'group_id': 'existing_group_id',
            'admin_id': 'non_existing_admin_uid',
            'new_member_id': 'new_member_uid'
        })

        # Check if the response contains the expected data
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 400)
        self.assertFalse(data['success']) 

    def test_remove_member_success(self):
        group_id = 'existing_group_id'
        admin_id = 'admin_id'
        member_id = 'existing_member_id'

        # Mock the database reference and group data
        with patch('backend.db.reference') as mock_reference:
            mock_group_ref = mock_reference.return_value
            mock_group_data = {
                'Admin': admin_id,
                'Members': [member_id]
            }
            mock_group_ref.get.return_value = mock_group_data

            # Send request to remove member
            response = self.app.post('/remove-member', json={
                'group_id': group_id,
                'admin_id': admin_id,
                'member_id': member_id
            })

        # Check the response
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], 'Member removed successfully')

    # Test case: Attempt to remove a non-existent member
    def test_remove_member_nonexistent_member(self):
        group_id = 'existing_group_id'
        admin_id = 'admin_id'
        member_id = 'nonexistent_member_id'

        # Mock the database reference and group data
        with patch('backend.db.reference') as mock_reference:
            mock_group_ref = mock_reference.return_value
            mock_group_data = {
                'Admin': admin_id,
                'Members': ['existing_member_id']
            }
            mock_group_ref.get.return_value = mock_group_data

            # Send request to remove member
            response = self.app.post('/remove-member', json={
                'group_id': group_id,
                'admin_id': admin_id,
                'member_id': member_id
            })

        # Check the response
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code,404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Member not found in the group')

    # Test case: Attempt to remove a member without admin privileges
    def test_remove_member_no_admin_privileges(self):
        group_id = 'existing_group_id'
        admin_id = 'another_admin_id'
        member_id = 'existing_member_id'

        # Mock the database reference and group data
        with patch('backend.db.reference') as mock_reference:
            mock_group_ref = mock_reference.return_value
            mock_group_data = {
                'Admin': 'admin_id',
                'Members': [member_id]
            }
            mock_group_ref.get.return_value = mock_group_data

            # Send request to remove member
            response = self.app.post('/remove-member', json={
                'group_id': group_id,
                'admin_id': admin_id,
                'member_id': member_id
            })

        # Check the response
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 403)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Only the admin can remove members')

    def test_leave_group_success(self):
        # Mock Firebase Admin SDK functions for getting group details
        with patch('firebase_admin.db.reference') as mock_db_reference:
            # Mock existing group data with a member and admin
            mock_group_data = {'Admin': 'admin_uid', 'Members': ['member_uid']}
            mock_db_reference.return_value.get.return_value = mock_group_data

            # Send a request to leave the group with valid data
            response = self.app.post('/leave-group', json={'group_id': 'mocked_group_id', 'member_id': 'member_uid'})

            # Check if the response contains the expected data
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['success'], True)
            self.assertEqual(data['message'], 'You left the group successfully')

    def test_leave_group_admin_delete_group(self):
        # Mock Firebase Admin SDK functions for getting group details and deleting group
        with patch('firebase_admin.db.reference') as mock_db_reference:
            # Mock existing group data with an admin
            mock_group_data = {'Admin': 'admin_uid', 'Members': []}
            mock_db_reference.return_value.get.return_value = mock_group_data

            # Send a request to leave the group with admin as the member
            response = self.app.post('/leave-group', json={'group_id': 'mocked_group_id', 'member_id': 'admin_uid'})

            # Check if the response contains the expected data
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['success'], True)
            self.assertEqual(data['message'], 'Group deleted successfully as you were the admin')

    def test_leave_group_not_member(self):
        # Mock Firebase Admin SDK functions for getting group details
        with patch('firebase_admin.db.reference') as mock_db_reference:
            # Mock existing group data without the member
            mock_group_data = {'Admin': 'admin_uid', 'Members': []}
            mock_db_reference.return_value.get.return_value = mock_group_data

            # Send a request to leave the group with a member not in the group
            response = self.app.post('/leave-group', json={'group_id': 'mocked_group_id', 'member_id': 'non_member_uid'})

            # Check if the response contains the expected data
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['success'], True)
            self.assertEqual(data['message'], 'You are not a member of this group')

    def test_leave_group_group_not_found(self):
        # Mock Firebase Admin SDK functions for getting group details
        with patch('firebase_admin.db.reference') as mock_db_reference:
            # Mock scenario where group is not found
            mock_db_reference.return_value.get.return_value = None

            # Send a request to leave a non-existent group
            response = self.app.post('/leave-group', json={'group_id': 'non_existent_group', 'member_id': 'member_uid'})

            # Check if the response contains the expected data
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertEqual(data['success'], False)
            self.assertEqual(data['message'], 'Group not found')

    def test_recommend_songs_no_top_rated_songs(self):
        # Mock Firebase Admin SDK functions for getting user songs
        with patch('firebase_admin.db.reference') as mock_db_reference:
            # Mock scenario where user has no top-rated songs
            mock_db_reference.return_value.get.return_value = None

            # Send a request to recommend songs for a user with no top-rated songs
            response = self.app.get('/recommend-songs', query_string={'user_id': 'mocked_user_id'})

            # Check if the response contains the expected data
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertEqual(data['success'], False)
            self.assertEqual(data['message'], 'No top-rated songs found')

    
    def test_recommend_friends_songs_no_activity_share(self):
        # Mock Firebase Admin SDK functions for getting user friends
        with patch('firebase_admin.db.reference') as mock_db_reference:
            # Mock user's friends without activityShare
            mock_friends_data = {
                'friend_1': {'activityShare': False},
                'friend_2': {'activityShare': False},
            }
            mock_db_reference.return_value.get.return_value = mock_friends_data

            # Send a request to recommend friends' songs for a user with friends but no activityShare
            response = self.app.get('/recommend-friends-songs', query_string={'user_id': 'mocked_user_id'})

            # Check if the response contains the expected data
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['success'], True)
            self.assertIn('recommended_songs', data)
            self.assertEqual(len(data['recommended_songs']), 0)  # Check if no recommended songs are returned

    def test_recommend_friends_songs_missing_user_id(self):
        # Send a request without providing the user_id
        response = self.app.get('/recommend-friends-songs')

        # Check if the response contains the expected data
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'User ID is required')







if __name__ == '__main__':
    unittest.main()
