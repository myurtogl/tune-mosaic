import React, { useState, useEffect } from 'react';
import './RatingInterface.css';

const RatingInterface = () => {
  const initialSongs = [
    { id: 1, title: 'Song A', artist: 'Artist A', rating: null },
    { id: 2, title: 'Song B', artist: 'Artist B', rating: null },
    { id: 3, title: 'Song C', artist: 'Artist C', rating: null },
    // Add more songs as needed
  ];

  const [songs, setSongs] = useState([...initialSongs]);

  const handleRatingChange = (songId, newRating) => {
    setSongs((prevSongs) =>
      prevSongs.map((song) =>
        song.id === songId ? { ...song, rating: newRating } : song
      )
    );
  };

  const handleRefresh = () => {
    // Find the index of the rated song
    const ratedSongIndex = songs.findIndex((song) => song.rating !== null);

    // Remove the rated song from the list
    const updatedSongs = [...songs];
    if (ratedSongIndex !== -1) {
      updatedSongs.splice(ratedSongIndex, 1);
    }

    // Select a new random song from the remaining list
    const randomIndex = Math.floor(Math.random() * updatedSongs.length);
    const newSong = updatedSongs[randomIndex];

    // Update the songs array with the new list and reset ratings
    setSongs((prevSongs) =>
      prevSongs.map((song) =>
        song.id === newSong.id ? { ...song, rating: null } : song
      )
    );
  };

  return (
    <div className="rating-interface">
      <h2>Rate Songs</h2>
      <div className="song-list">
        {songs.map((song) => (
          <div key={song.id} className="song-item">
            <p>{`${song.title} - ${song.artist}`}</p>
            <RatingStars
              value={song.rating}
              onChange={(newRating) => handleRatingChange(song.id, newRating)}
              onRefresh={handleRefresh}
            />
          </div>
        ))}
      </div>
    </div>
  );
};

const RatingStars = ({ value, onChange, onRefresh }) => {
  const [rating, setRating] = useState(value);

  useEffect(() => {
    setRating(value);
  }, [value]);

  const handleStarClick = (starValue) => {
    setRating(starValue);
    onChange && onChange(starValue);

    // Select a new random song after clicking a star
    onRefresh && onRefresh();
  };

  return (
    <div className="rating-stars">
      {[1, 2, 3, 4, 5].map((star) => (
        <span
          key={star}
          className={star <= rating ? 'star-filled' : 'star-empty'}
          onClick={() => handleStarClick(star)}
        >
          ★
        </span>
      ))}
    </div>
  );
};

export default RatingInterface;
