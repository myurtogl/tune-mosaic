import React, { useState, useEffect } from 'react';
import './SongInputForm.css';
import { onAuthStateChanged } from 'firebase/auth';
import fetch from 'cross-fetch';
import { auth } from '../LoginSignup/firebaseConfig';
import { useNavigate } from 'react-router-dom';

const SongInputForm = () => {
  const navigate = useNavigate();
  const [songData, setSongData] = useState({
    songName: '',
    albumName: '',
    performer: '',
    genre: '',
    mood: '',
    rating: 0,
    dateOfRating: null,
  });
  const [isSubmitting1, setIsSubmitting1] = useState(false);
  const [userId, setUserId] = useState(null);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      if (user) {
        setUserId(user.uid);
      } else {
        setUserId(null);
      }
    });

    return () => unsubscribe();
  }, [auth]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting1(true);

    try {
      if (userId) {
        const requestBody = {
          user_id: userId,
          song_data: songData,
        };

        const response = await fetch('/add-song', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(requestBody),
        });

        if (!response.ok) {
          console.error('HTTP error:', response.status);
          throw new Error('Network response was not ok');
        }

        // Simulating an API request delay
        await new Promise((resolve) => setTimeout(resolve, 1500));

        // Reset form and animation after successful submission
        setSongData({
          songName: '',
          albumName: '',
          performer: '',
          genre: '',
          mood: '',
          rating: 0,
          dateOfRating: null,
        });

        // Navigate to another page after successful submission
        navigate('/userpage');
      }
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setIsSubmitting1(false);
    }
  };

  return (
    <div className="song-input-form">
      <div className="form-container">
        <h2>Manual Song Input</h2>
        <form onSubmit={handleSubmit}>
          <label>
            Song Title:
            <input
              type="text"
              value={songData.songName}
              onChange={(e) => setSongData((prevData) => ({ ...prevData, songName: e.target.value }))}
              required
            />
          </label>
          {/* Add similar input fields for other song data */}
          <button type="submit" className={`submit-button ${isSubmitting1 ? 'submitting' : ''}`} disabled={isSubmitting1}>
            {isSubmitting1 ? 'Submitting...' : 'Submit'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default SongInputForm;
