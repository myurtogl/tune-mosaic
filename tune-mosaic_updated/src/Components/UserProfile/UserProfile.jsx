import React from 'react';
import './UserProfile.css'; // Create a corresponding CSS file for styling

const UserProfile = ({ username }) => {
  return (
    <div className="user-profile">
      <div className="profile-photo"></div>
      <div className="profile-info">
        <span className="username">{username}</span>
        <div className="profile-menu">
          <button>Edit Profile</button>
          <button>Change Password</button>
          <button>Logout</button>
        </div>
      </div>
    </div>
  );
};

export default UserProfile;
