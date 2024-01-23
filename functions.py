@patch('backend.db')
def test_recommend_friends_songs_success(self, mock_db):
    user_id = 'test_user_id'
    friend_id = 'friend_user_id'

    # Mock data for user's friends and their songs
    mock_friends_data = {friend_id: {'activityShare': True}}
    mock_friend_songs = {
        'song1_id': {'rating': 5, 'title': 'Song1', 'artist': 'Artist1'},
        'song2_id': {'rating': 5, 'title': 'Song2', 'artist': 'Artist2'}
    }

    # Setup mock database responses
    mock_friends_ref = MagicMock()
    mock_friends_ref.get.return_value = mock_friends_data
    mock_friend_songs_ref = MagicMock()
    mock_friend_songs_ref.get.return_value = mock_friend_songs
    mock_db.reference.side_effect = lambda ref: mock_friends_ref if 'friends' in ref else mock_friend_songs_ref

    # Perform the request
    response = self.app.get(f'/recommend-friends-songs?user_id={user_id}')

    # Assert response
    self.assertEqual(response.status_code, 200)
    data = json.loads(response.data.decode())
    self.assertEqual(data['success'], True)
    self.assertGreater(len(data['recommended_songs']), 0, "Expected some recommended songs")
pass

@patch('backend.db')
def test_recommend_friends_songs_no_friends(self, mock_db):
    user_id = 'test_user_id'

    # Setup mock database response for no friends
    mock_friends_ref = MagicMock()
    mock_friends_ref.get.return_value = {}
    mock_db.reference.return_value = mock_friends_ref

    # Perform the request
    response = self.app.get(f'/recommend-friends-songs?user_id={user_id}')

    # Assert response
    self.assertEqual(response.status_code, 200)
    data = json.loads(response.data.decode())
    self.assertEqual(data['success'], True)
    self.assertEqual(len(data['recommended_songs']), 0, "Expected no recommended songs due to no friends")
pass

@patch('backend.db')
def test_recommend_friends_songs_no_shared_songs(self, mock_db):
    user_id = 'test_user_id'
    friend_id = 'friend_user_id'

    # Setup mock data for user's friends without shared songs
    mock_friends_data = {friend_id: {'activityShare': True}}
    mock_friends_ref = MagicMock()
    mock_friends_ref.get.return_value = mock_friends_data
    mock_friend_songs_ref = MagicMock()
    mock_friend_songs_ref.get.return_value = {}  # No songs
    mock_db.reference.side_effect = lambda ref: mock_friends_ref if 'friends' in ref else mock_friend_songs_ref

    # Perform the request
    response = self.app.get(f'/recommend-friends-songs?user_id={user_id}')

    # Assert response
    self.assertEqual(response.status_code, 200)
    data = json.loads(response.data.decode())
    self.assertEqual(data['success'], True)
    self.assertEqual(len(data['recommended_songs']), 0, "Expected no recommended songs due to no shared songs")
    pass
#Kullanıcının Yüksek Puanlı Şarkılarına Göre Öneri Yapmak
@patch('backend.sp')
@patch('backend.db')
def test_recommend_songs_high_rated(self, mock_db, mock_sp):
    user_id = 'test_user_id'

    # Mock database call for user's high rated songs
    mock_user_songs_ref = MagicMock()
    mock_user_songs_ref.get.return_value = {
        'song1_id': {'rating': 5, 'title': 'High Rated Song1', 'artist': 'Artist1'},
        'song2_id': {'rating': 5, 'title': 'High Rated Song2', 'artist': 'Artist2'}
    }
    mock_db.reference.return_value = mock_user_songs_ref

    # Mock Spotify API calls
    mock_sp.search.return_value = {'tracks': {'items': [{'id': 'spotify_track_id'}]}}
    mock_sp.recommendations.return_value = {'tracks': [{'name': 'Recommended Song', 'artists': [{'name': 'Recommended Artist'}]}]}

    # Perform the request
    response = self.app.get(f'/recommend-songs?user_id={user_id}')

    # Assert response
    self.assertEqual(response.status_code, 200)
    data = json.loads(response.data.decode())
    self.assertEqual(data['success'], True)
    self.assertGreater(len(data['recommended_tracks']), 0, "Expected recommendations for high rated songs")
#Kullanıcının Yüksek Puanlı Şarkısı Olmadığında Öneri Yapılmaması
@patch('backend.sp')
@patch('backend.db')
def test_recommend_songs_no_high_rated_songs(self, mock_db, mock_sp):
    user_id = 'test_user_id'

    # Mock database call for user's songs without high ratings
    mock_user_songs_ref = MagicMock()
    mock_user_songs_ref.get.return_value = {
        'song1_id': {'rating': 3, 'title': 'Song1', 'artist': 'Artist1'},
        'song2_id': {'rating': 4, 'title': 'Song2', 'artist': 'Artist2'}
    }
    mock_db.reference.return_value = mock_user_songs_ref

    # Perform the request
    response = self.app.get(f'/recommend-songs?user_id={user_id}')

    # Assert response
    self.assertEqual(response.status_code, 200)
    data = json.loads(response.data.decode())
    self.assertEqual(data['success'], True)
    self.assertEqual(len(data['recommended_tracks']), 0, "Expected no recommendations due to lack of high-rated songs")
#Spotify API'sinden Hata Alındığında Test
@patch('backend.sp')
@patch('backend.db')
def test_recommend_songs_spotify_error(self, mock_db, mock_sp):
    user_id = 'test_user_id'

    # Mock database call for user's high rated songs
    mock_user_songs_ref = MagicMock()
    mock_user_songs_ref.get.return_value = {
        'song1_id': {'rating': 5, 'title': 'High Rated Song1', 'artist': 'Artist1'}
    }
    mock_db.reference.return_value = mock_user_songs_ref

    # Mock Spotify API calls to simulate an error
    mock_sp.search.side_effect = Exception("Spotify API error")
    
    # Perform the request
    response = self.app.get(f'/recommend-songs?user_id={user_id}')

    # Assert response
    self.assertEqual(response.status_code, 500)  # Assuming your API returns 500 on Spotify errors
    data = json.loads(response.data.decode())
    self.assertEqual(data['success'], False)
    self.assertIn("Spotify API error", data['message'])



# Testleri çalıştırmak için bu if bloğunu kullanabil
if __name__ == '__main__':
    unittest.main()
