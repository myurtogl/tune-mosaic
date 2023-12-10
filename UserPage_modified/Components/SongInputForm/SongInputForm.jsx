import React, { useState, useEffect } from 'react';
import './SongInputForm.css';
import { initializeApp } from 'firebase/app';
import { getAuth, onAuthStateChanged } from 'firebase/auth'
import firebaseConfig from '../backend/firebaseConfig'; // Adjust the path as necessary
// Import fetch
import fetch from 'cross-fetch';

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

const SongInputForm = () => {
  const [songTitle, setSongTitle] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [userId, setUserId] = useState(null);
  
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      if (user) {
        setUserId(user.uid);
      } else {
        setUserId(null);
      }
    });
  
    // Cleanup the subscription when the component unmounts
    return () => unsubscribe();
  }, []);
  ;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    try  {
      if (userId) {
        const requestBody = {
          user_id: userId,
          song_data: {
            title: songTitle,
            // Add other song data fields as needed
          },
        };
        const response = await fetch('/add-song', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(requestBody),
        });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      // Simulating an API request delay
      await new Promise((resolve) => setTimeout(resolve, 1500));

      // Reset form and animation after submission
      setSongTitle('');
    }
  } catch (error) {
      console.error('Error:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className={`song-input-form ${isSubmitting ? 'submitting' : ''}`}>
      <div className="form-container">
        <h2>Manual Song Input</h2>
        <form onSubmit={handleSubmit}>
          <label>
            Song Title:
            <input
              type="text"
              value={songTitle}
              onChange={(e) => setSongTitle(e.target.value)}
              required
            />
          </label>
          <button type="submit" className={isSubmitting ? 'submitting' : ''}>
            {isSubmitting ? 'Submitting...' : 'Submit'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default SongInputForm;
