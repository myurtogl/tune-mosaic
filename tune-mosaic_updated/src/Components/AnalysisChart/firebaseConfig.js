// Import the functions you need from the SDKs you need
import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';

const firebaseConfig = {
	apiKey: "AIzaSyA5NtH5fU0AfaZrA6s4wmheNMWfDMPIxy8",
	authDomain: "tune-mosaic.firebaseapp.com",
	databaseURL: "https://tune-mosaic-default-rtdb.firebaseio.com",
	projectId: "tune-mosaic",
	storageBucket: "tune-mosaic.appspot.com",
	messagingSenderId: "775271234021",
	appId: "1:775271234021:web:74665823f1dbd60be5d70c",
	measurementId: "G-1PN6Y2DVHH"
  };

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Get a reference to the authentication service
const auth = getAuth(app);

export { auth };
