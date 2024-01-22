# Tune-Mosaic

Welcome to the tune-mosaic! This system is designed to collect and analyze liked-song data from various sources and provide users with insightful musical recommendations based on their preferences. Whether you're a music enthusiast looking to discover new tracks or a data enthusiast interested in exploring musical taste patterns, this project has something for you.

## Project Overview

In this project, we aim to:

- Collect Liked-Song Data: We gather liked-song information from different platforms and sources, allowing users to consolidate their music preferences in one place.

- Musical Flavor Analysis: Our system offers various types of analysis, helping users understand their musical flavor. This includes genre preferences, artist exploration, and more.

- Personalized Recommendations: Leveraging the collected data and analysis, we provide tailored music recommendations to users. Whether you're in the mood for something new or similar to your existing favorites, we've got you covered.

## Getting Started

To get started with the Liked-Song Analysis and Recommendation System, follow these steps:
 *Clone the Repository:* Clone this repository to your local machine using the following command:

   
   git clone https://github.com/your-username/liked-song-analysis.git
   
**For the backend setup:**

1. Install the required Python packages by running the following command in your terminal:

   pip install -r requirements.txt
   
2.Update the Firebase authentication JSON file with your own credentials. Replace the existing "cred.json" file with your Firebase authentication JSON file.


3.Modify the client_id and client_secret in the configuration file to match your Spotify API credentials. Update these values in the configuration file to ensure proper authentication and access to the Spotify API.
   

**Web setup and usage:** 

Prerequisites:

   *Node.js
  
   *npm


1. Install the dependencies by running the following command in your terminal:

   npm install


2. Start the system by running:
   
   cd /directory_name


   npm start
   

3. Access the web interface at [http://localhost:3000](http://localhost:3000) to explore your musical analysis and receive personalized recommendations.


**For mobile setup and usage:**

Prerequisites:


   *Xcode
   
   *Swift

1. Install the dependencies by running the following command in your terminal:

      pod install

2. Open the Xcode project by the following command:

      open YourApp.xcworkspace



## Use Case Scenario: Discovering Personalized Music Recommendations
User Story: 

1.**Logging In:**
   -The user visits the web interface or mobile app and logs in using their credentials.

2. **Inputting Liked Songs:**
   - After logging in, the user navigates to the Liked-Song input section.
   - They provide information about songs they like, including genres, artists, and specific        tracks.
   - Input can be entered as text, or a file containing song information can be used.

3.**Musical Flavor Analysis:**
   -The system analyzes the provided liked-song data, identifying the user's musical preferences.
   -The user explores insightful charts and graphs depicting their genre preferences, artist        exploration, and more.

4.**Personalized Recommendations:**
   -Leveraging the analyzed data, the system generates personalized music recommendations for       the user.
   -The user receives a list of suggested songs that align with their existing favorites.
     

**Additional Notes:**
Encourage users to regularly update their liked-song data for more accurate recommendations.
Highlight any specific features or settings that enhance the user experience.


## Backlog in Gherkin Format
Feature: Deciding the Data Format
  Scenario: Determine the most suitable data format for system needs
    Given the need to store and process various types of data
    When evaluating different data formats
    Then decide on a data format that optimizes performance, flexibility, and scalability

Feature: Database Setup
  Scenario: Initialize and configure the system database
    Given the decided data format and system requirements
    When setting up the database
    Then the database should be properly configured for performance, integrity, and security

Feature: Web Login Page Design
  Scenario: Design an intuitive and aesthetically pleasing login page for web users
    Given the web platform interface requirements
    When designing the login page
    Then the page should provide an excellent user experience and align with design standards

Feature: User Login Registration - Backend
  Scenario: Implement the backend logic for user login and registration
    Given the web and mobile interface requirements
    When a user tries to register or log in
    Then the backend should handle the process securely, efficiently, and without errors

Feature: User Login Design - Mobile
  Scenario: Design an intuitive and aesthetically pleasing login page for mobile users
    Given the mobile platform interface requirements
    When designing the login page for mobile
    Then the page should provide an excellent user experience and align with mobile design standards

Feature: Web-User Registration Integration
  Scenario: Ensure seamless integration of the registration feature with the web interface
    Given the web interface and backend registration logic
    When a user registers through the web interface
    Then the system should accurately process and store user information

Feature: Mobile-User Registration Integration
  Scenario: Ensure seamless integration of the registration feature with the mobile interface
    Given the mobile interface and backend registration logic
    When a user registers through the mobile interface
    Then the system should accurately process and store user information

Feature: Data Collection from User Input
  Scenario: Collect and store data entered by users
    Given the need to collect user data through various interfaces
    When a user submits data
    Then the system should accurately capture and store the data

Feature: Data Collection from TXT File
  Scenario: Import and process data from TXT files
    Given the need to ingest data from TXT file sources
    When a TXT file is uploaded to the system
    Then the system should accurately parse and store the data

Feature: Web-User Data Input Design
  Scenario: Design an intuitive and efficient data input interface for web users
    Given the web platform interface requirements
    When designing the data input interface
    Then it should provide a seamless experience for users to input and submit their data

Feature: Mobile-User Data Input Design
  Scenario: Design an intuitive and efficient data input interface for mobile users
    Given the mobile platform interface requirements
    When designing the data input interface for mobile
    Then it should provide a seamless experience for users to input and submit their data

Feature: Firebase Hosting
  Scenario: Deploy the system on Firebase for hosting
    Given the system's requirements for hosting
    When deploying the application to Firebase
    Then the system should be accessible and perform well, with minimal downtime

Feature: Backend-Database Check After Inputs
  Scenario: Validate and confirm data integrity after user inputs
    Given the system's need for accurate and reliable data
    When data is entered into the system
    Then the backend should verify the integrity and correctness of the data

Feature: Rate Songs - Backend
  Scenario: Implement song rating functionality in the backend
    Given the user's need to rate songs
    When a user rates a song
    Then the backend should accurately record and reflect the rating in the user's profile and song metadata

Feature: Rate Songs - Mobile
  Scenario: Provide a user-friendly interface for rating songs on mobile devices
    Given the mobile interface requirements
    When a user rates a song on a mobile device
    Then the interface should record the rating and update the user's profile and song metadata accordingly

Feature: Spotify API Integration - Backend
  Scenario: Integrate Spotify API to enrich the system's music functionalities
    Given the system's requirement to interface with Spotify's services
    When integrating the Spotify API
    Then the system should be able to access, retrieve, and utilize Spotify's data and functionalities

Feature: User Page Design Adjustments - Mobile
  Scenario: Refine the design of the user page on mobile for better user experience
    Given user feedback and mobile interface design principles
    When adjusting the design of the user page on mobile
    Then the page should become more intuitive, aesthetically pleasing, and user-friendly

Feature: Login Re-Do - Backend
  Scenario: Enhance the login process and backend logic
    Given the need to improve the user login experience and security
    When redesigning the login process and backend logic
    Then the login process should become more secure, efficient, and user-friendly

Feature: Delete Song - Backend
  Scenario: Enable users to delete songs from their profile or playlists
    Given the user's need to manage their songs
    When a user deletes a song
    Then the backend should remove the song from the user's profile, playlists, and handle all associated data correctly

Feature: Delete Song - Mobile
  Scenario: Provide an intuitive interface for users to delete songs on mobile devices
    Given the mobile interface requirements
    When a user deletes a song on a mobile device
    Then the interface should facilitate the deletion and the backend should process it correctly

Feature: Delete Album - Backend
  Scenario: Enable users to delete albums from their profile or collections
    Given the user's need to manage their albums
    When a user deletes an album
    Then the backend should remove the album from the user's profile, collections, and handle all associated data correctly

Feature: Delete Album - Mobile
  Scenario: Provide an intuitive interface for users to delete albums on mobile devices
    Given the mobile interface requirements
    When a user deletes an album on a mobile device
    Then the interface should facilitate the deletion and the backend should process it correctly

Feature: Documentation - Last Version on GitHub
  Scenario: Maintain and update the system documentation on GitHub
    Given the system's ongoing development and changes
    When updating the system
    Then the documentation on GitHub should be updated to reflect the latest version and changes

Feature: Documentation - ER Diagram
  Scenario: Create and maintain an Entity-Relationship (ER) diagram for the system
    Given the system's database and data relationship complexities
    When designing or updating the system's database
    Then an ER diagram should be created or updated to accurately represent the data model

Feature: Listing Top Favourite Songs - Backend
  Scenario: Generate a list of top favourite songs for each user
    Given the users' song ratings and preferences
    When a user requests to see their top songs
    Then the backend should generate and provide a list of the user's top favourite songs

Feature: Listing Top Favourite Songs - Mobile
  Scenario: Display the list of top favourite songs on mobile devices
    Given the mobile interface requirements and the backend's list of top songs
    When a user views their top songs on a mobile device
    Then the interface should display the list in an intuitive and aesthetically pleasing manner

Feature: Giving Recommendations - Backend
  Scenario: Provide music recommendations to users based on their preferences
    Given the users' music preferences and listening history
    When a user seeks music recommendations
    Then the backend should analyze the data and provide relevant music recommendations

Feature: Add Song - Backend
  Scenario: Allow the addition of songs to the system's database
    Given the need to expand the system's music library
    When a new song is added
    Then the backend should process and include the song in the system's database correctly

Feature: Upload Song Information from File - Backend
  Scenario: Enable bulk upload of song information from files
    Given the need to ingest multiple song details at once
    When a file containing song information is uploaded
    Then the backend should parse the file and accurately store the song details in the database

Feature: Test and Re-Do Upload/Add Song Functions - Backend
  Scenario: Ensure the reliability and accuracy of upload and add song functionalities
    Given the critical nature of song data integrity
    When testing the upload and add song functions
    Then any issues should be identified and rectified to ensure the system's data accuracy and reliability

Feature: Friendship Interface - Mobile
  Scenario: Design and implement a user-friendly friendship interface on mobile devices
    Given the mobile platform requirements
    When designing the friendship interface
    Then it should facilitate users in managing and interacting with their friends list intuitively and efficiently

Feature: Friendship Feature - Backend
  Scenario: Manage and support friendship functionalities in the backend
    Given the need for users to connect and interact with friends
    When a user manages their friendships
    Then the backend should handle the friendship data and interactions securely and efficiently

Feature: Recommendations Listing - Mobile
  Scenario: Display music recommendations on mobile devices effectively
    Given the mobile interface requirements and backend recommendations
    When a user views music recommendations on a mobile device
    Then the interface should present the recommendations in an intuitive and engaging manner

Feature: Recommendation via Genre/Mood - Backend
  Scenario: Generate music recommendations based on specific genres or moods
    Given the user's preference for certain genres or moods
    When a user seeks recommendations for a specific genre or mood
    Then the backend should analyze the available data and provide suitable music recommendations

Feature: Friendship Recommendations - Backend
  Scenario: Suggest friends or connections based on user preferences and activities
    Given the user's social and musical preferences
    When a user explores friendship or connection options
    Then the backend should provide recommendations for potential friends or connections

Feature: Data Collection Managing - Backend
  Scenario: Efficiently manage and handle data collection from various sources
    Given the diverse sources and types of data collected by the system
    When data is being collected and processed
    Then the backend should manage the data securely, efficiently, and accurately

Feature: Test Units
  Scenario: Develop and implement test units to ensure system functionality and reliability
    Given the complex functionalities and integrations of the system
    When developing and executing test units
    Then they should thoroughly test the system components and ensure they work as intended

Feature: Diagrams
  Scenario: Create and maintain various system diagrams for better understanding and documentation
    Given the system's complexity and the need for clear documentation
    When creating or updating system diagrams
    Then they should accurately represent the system's architecture, data flow, and component interactions
## API Documentation
1. User Authentication and Registration
1.1 Verify Token
Endpoint: /verify-token
Method: POST
Description: Verifies a user's ID token for login attempts or registers a new user if no token is provided.
Request Body:
token (optional): The ID token from the client side.
email, password, username (required for registration): User credentials for account creation.
Responses:
200 OK:
On successful login: Returns the UID of the logged-in user.
On successful registration: Returns a custom token for the registered user.
401 Unauthorized: Returns an error message if the token is invalid or registration details are incomplete or incorrect.
1.2 Google Sign-In
Endpoint: /google-signin
Method: POST
Description: Authenticates users via Google Sign-In, creating a new user record if it's the first login.
Request Body:
idToken: The ID token received from the Google Sign-In SDK on the client.
Responses:
200 OK: Returns a success message with the user's UID.
401 Unauthorized: Returns an error message if the ID token is invalid.
2. Song Management
2.1 Add Song
Endpoint: /add-song
Method: POST
Description: Adds a new song to the user's collection.
Request Body:
user_id: The ID of the user adding the song.
song_data: The details of the song (e.g., name, artist, album).
Responses:
200 OK: Returns a success message with the newly added song's ID.
400 Bad Request: Returns an error message if user_id or song_data is missing.
404 Not Found: Returns an error message if the user does not exist.
2.2 Rate Song
Endpoint: /rate-song
Method: POST
Description: Updates the rating of a song in the user's collection.
Request Body:
user_id: The ID of the user who owns the song.
song_id: The ID of the song to be rated.
rating: The new rating for the song.
Responses:
200 OK: Returns a success message stating that the song rating was updated.
500 Internal Server Error: Returns an error message if an exception occurs during the process.
2.3 Delete Song
Endpoint: /delete-song
Method: DELETE
Description: Removes a song from the user's collection.
Request Body:
user_id: The ID of the user who owns the song.
song_id: The ID of the song to be deleted.
Responses:
200 OK: Returns a success message stating that the song was deleted.
404 Not Found: Returns an error message if the song is not found.
500 Internal Server Error: Returns an error message if an exception occurs during the process.
3. Social Features
3.1 Follow User
Endpoint: /follow-user
Method: POST
Description: Allows a user to follow another user, updating both their 'following' and 'followers' lists.
Request Body:
follower_id: The ID of the user who wants to follow.
followed_id: The ID of the user to be followed.
Responses:
200 OK: Returns a success message stating the follow action was successful.
500 Internal Server Error: Returns an error message if an exception occurs during the process.
3.2 Unfollow User
Endpoint: /unfollow-user
Method: POST
Description: Allows a user to unfollow another user, updating both their 'following' and 'followers' lists.
Request Body:
active_user_id: The ID of the user who initiates the unfollow.
unfollow_user_id: The ID of the user to be unfollowed.
Responses:
200 OK: Returns a success message stating the unfollow action was successful.
500 Internal Server Error: Returns an error message if an exception occurs during the process.
4. Music Recommendation
4.1 Recommend Songs
Endpoint: /recommend-songs
Method: GET
Description: Provides song recommendations based on the user's top-rated songs.
Request Parameters:
user_id: The ID of the user for whom recommendations are to be generated.
Responses:
200 OK: Returns a list of recommended songs.
404 Not Found: Returns an error message if no top-rated songs are found.
500 Internal Server Error: Returns an error message if an exception occurs during the process.
4.2 Recommend Friends' Songs
Endpoint: /recommend-friends-songs
Method: GET
Description: Provides song recommendations based on the songs rated by the user's friends.
Request Parameters:
user_id: The ID of the user for whom friend-based recommendations are to be generated.
Responses:
200 OK: Returns a list of recommended songs from friends.
400 Bad Request: Returns an error message if user_id is missing.
404 Not Found: Returns an error message if no friends or songs are found.
500 Internal Server Error: Returns an error message if an exception occurs during the process.
## Sequence Diagrams
 Google Sign-In Flow
![Google Sign-In Flow](https://github.com/myurtogl/tune-mosaic/assets/127950404/b3ca1cd7-dcb6-455b-bb61-86732c0d1a90)


 Group Management Flow
![Enhanced Group Management Flow](https://github.com/myurtogl/tune-mosaic/assets/127950404/758d7fc9-63ce-4309-8b88-073b00655e5c)

   
