import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './RatingInterface.css';
import axios from 'axios';
import { auth } from './firebaseConfig';

// Placeholder component for Navbar
const PlaceholderNavbar = () => (
  <nav>
    <ul>
      <li>
        <Link to="/">Home</Link>
      </li>
      <li>
        <Link to="/about">About</Link>
      </li>
      {/* Add more links as needed */}
    </ul>
  </nav>
);

function RatingInterface() {
  const [formData, setFormData] = useState({
    songName: '',
    album: '',
    artist: '',
    year: '',
    rating: '5',
    userId: '', // This should be fetched from the user's session or state
  });

  useEffect(() => {
    // This effect sets the userId once the user is authenticated
    auth.onAuthStateChanged((user) => {
      if (user) {
        setFormData((prevFormData) => ({
          ...prevFormData,
          userId: user.email, // Assuming you want to use the UID as the userId
        }));
      } else {
        // Handle user not logged in
        console.log('User is not logged in');
        // Redirect to login page or show a message
      }
    });
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevState) => ({
      ...prevState,
      [name]: value,
    }));
  };

  const handleFileInputChange = (e) => {
    const { name, files } = e.target;
    setFormData((prevState) => ({
      ...prevState,
      [name]: files[0], // Assuming you want to store the file object in the state
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.userId) {
      alert('You must be logged in to add a song.');
      return;
    }
    try {
      const formDataToSend = new FormData();
      for (const key in formData) {
        formDataToSend.append(key, formData[key]);
      }

      const response = await axios.post('http://localhost:3000/api/add-song', formDataToSend);
      console.log(response.data);
      // Handle success, clear form, show message, etc.
    } catch (error) {
      console.error('Error adding song:', error);
      // Handle error, show error message, etc.
    }
  };

  return (
    <div className="black-container">
      <PlaceholderNavbar />
      <div className="home-page">
        <div className="home-container">
          <h1 className="home-header">Welcome to Your Music Library</h1>
          <form onSubmit={handleSubmit}>
            <input
              name="songName"
              value={formData.songName}
              onChange={handleInputChange}
              placeholder="Song Name"
              required
            />
            <input
              name="artist"
              value={formData.artist}
              onChange={handleInputChange}
              placeholder="Artist Name"
              required
            />
            <input
              name="album"
              value={formData.album}
              onChange={handleInputChange}
              placeholder="Album"
              required
            />
            <input
              name="year"
              value={formData.year}
              onChange={handleInputChange}
              placeholder="Year"
              required
            />
            <label htmlFor="rating">Add a rating:</label>
            <input
              id="rating"
              name="rating"
              type="range"
              value={formData.rating}
              onChange={handleInputChange}
              min="1"
              max="10"
            />
            <div className="rating-display">Rating: {formData.rating}</div>

            {/* File input fields */}
            <label htmlFor="audioFile">Upload Audio File:</label>
            <input
              id="audioFile"
              name="audioFile"
              type="file"
              onChange={handleFileInputChange}
              accept="audio/*"
              required
            />

            <label htmlFor="imageFile">Upload Image File:</label>
            <input
              id="imageFile"
              name="imageFile"
              type="file"
              onChange={handleFileInputChange}
              accept="image/*"
              required
            />

            <button className="home-button" type="submit">
              Add Song
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default RatingInterface;
