import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import './App.css';
import LoginSignup from './Components/LoginSignup/LoginSignup';
import UserPage from './Components/UserPage/UserPage';

function App() {
  const [isAuthenticated, setAuthenticated] = useState(false);

  const handleAuthentication = () => {
    // Perform your authentication logic here
    // For example, you might use Firebase authentication
    // After successful authentication, update the state
    setAuthenticated(true);
  };

  return (
    <Router>
      <Routes>
        <Route>
          <Route index element={<LoginSignup />} />
          <Route path="userpage" element={<UserPage />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;

/*  
return (
    <Router>
      <Routes>
        <Route
          path="/login"
          element={<LoginSignup onAuthentication={handleAuthentication} />}
        />
        <Route
          path="/userpage"
          element={
            isAuthenticated ? (
              <UserPage />
            ) : (
              <Navigate to="/login" />
            )
          }
        />
      </Routes>
    </Router>
  );

*/