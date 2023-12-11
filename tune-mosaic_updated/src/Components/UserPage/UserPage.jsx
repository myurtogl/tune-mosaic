// UserPage.jsx
import React from "react";
import "./UserPage.css";
import SongInputForm from "../SongInputForm/SongInputForm";
import BatchInputForm from "../BatchInputForm/BatchInputForm";
import DatabaseTransfer from "../DatabaseTransfer/DatabaseTransfer";
import RatingInterface from "../RatingInterface/RatingInterface";
import RemoveItem from "../RemoveItem/RemoveItem";
import UserProfile from "../UserProfile/UserProfile";
import MusicDashboard from "../AnalysisChart/AnalysisChart";

const UserPage = () => {
  const username = "SampleUser";

  return (
    <div className="user-page">
      <div className="forms-wrapper">
        <UserProfile username={username} />
        <RatingInterface />
        <DatabaseTransfer />
        <BatchInputForm />
        <SongInputForm />
        <RemoveItem />
      </div>
    </div>
  );
};

export default UserPage;
