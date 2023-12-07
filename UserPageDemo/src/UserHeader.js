import React from 'react';
import './UserHeader.scss'
import pic from './pic.jpg';

const userHeader = () => {
    return(
        <div className="user-header">
            <div className="user-info">
            <img className="user-photo" src={pic} alt="User"/>
                <div className="user-details">
                    <span>UserName</span>
                    
                    </div>
                        <div className="follower-info">
                            <span> Followers: 100</span>
                            <span> Following: 100</span>
                        </div> 
                    </div>
                    <hr />
                </div>

    );
};

export default userHeader;