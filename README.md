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



