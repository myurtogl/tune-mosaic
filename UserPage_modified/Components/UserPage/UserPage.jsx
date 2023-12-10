import React from "react";
import SongInputForm from "../SongInputForm/SongInputForm";
import BatchInputForm from "../BatchInputForm/BatchInputForm";
import DatabaseTransfer from "../DatabaseTransfer/DatabaseTransfer";
import RatingInterface from "../RatingInterface/RatingInterface";
import RemoveItem from "../RemoveItem/RemoveItem";
import ExternalSystemTransfer from "../ExternalSystemTransfer/ExternalSystemTransfer";
import "./UserPage.css";
import UserProfile from "../UserProfile/UserProfile";

const UserPage = () => {
  const username = 'SampleUser';
  return (
    <div className="user-page">
      <UserProfile username={username} />
      <div className="forms-wrapper">
        <RatingInterface />
        <DatabaseTransfer />
        <BatchInputForm />
        <SongInputForm />
        <ExternalSystemTransfer />
        <RemoveItem />
      </div>
    </div>
  );
};

export default UserPage;
