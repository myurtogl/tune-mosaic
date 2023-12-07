import React, { useState } from "react";
import "./LoginSignup.css";
import { FcGoogle } from 'react-icons/fc';
import { BsLinkedin } from 'react-icons/bs';
import { ImYoutube2 } from 'react-icons/im';
import { FaFacebookSquare } from 'react-icons/fa';


const LoginSignup = () => {
    const [containerActive, setContainerActive] = useState(false);
    const [name, setName] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const handleRegisterClick = async () => {
        try {
          // Your request data
          const requestData = {
            email: email,
            password: password,
            user_data: { name: name },
          };
    
          const response = await fetch('http://127.0.0.1:5000/register', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData),
          });
    
          if (response.ok) {
            const responseData = await response.json();
            console.log(responseData);
            // Handle success, e.g., redirect or show a success message
          } else {
            // Handle errors here
            console.error('Error:', response.status, response.statusText);
            // You may want to show an error message to the user
          }
        } catch (error) {
          console.error('Error:', error);
          // Handle unexpected errors here
        }
        setContainerActive(true);
      };
    const handleLoginClick = async () => {
      try {
        // Your login request data
        const loginData = {
          email: email,
          password: password,
        };
  
        const response = await fetch('http://127.0.0.1:5000/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(loginData),
        });
  
        if (response.ok) {
          const responseData = await response.json();
          console.log(responseData);
          // Handle success, e.g., redirect or show a success message
        } else {
          // Handle errors here
          console.error('Error:', response.status, response.statusText);
          // You may want to show an error message to the user
        }
      } catch (error) {
        console.error('Error:', error);
        // Handle unexpected errors here
      }
  
      setContainerActive(false);
    };
  return (
    <div className={`container ${containerActive ? "active" : ""}`} id="container">
        <div className="container" id="container">
            <div className="form-container sign-up">
                <form>
                    <h1>Create Account</h1>
                    <div class="social-icons">
                        <a href="#" class="icon"><FcGoogle/></a>
                        <a href="#" class="icon"><FaFacebookSquare/></a>
                        <a href="#" class="icon"><BsLinkedin/></a>
                        <a href="#" class="icon"><ImYoutube2/></a>
                    </div>
                    <span>or use your email for registeration</span>
                    <input type="text" placeholder="Name" value={name} onChange={(e) => setName(e.target.value)} />
                    <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
                    <input type="password" placeholder="Password" value={email} onChange={(e) => setEmail(e.target.value)} />
                    <button type="button" onClick={handleRegisterClick}>Sign Up</button>
                </form>
            </div>
            <div class="form-container sign-in">
                <form>
                    <h1>Sign In</h1>
                    <div class="social-icons">
                        <a href="#" class="icon"><FcGoogle/></a>
                        <a href="#" class="icon"><FaFacebookSquare/></a>
                        <a href="#" class="icon"><BsLinkedin/></a>
                        <a href="#" class="icon"><ImYoutube2/></a>
                    </div>
                    <span>or use your email password</span>
                    <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
                    <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
                    <a href="#">Forget Your Password?</a>
                    <button type="button" onClick={handleLoginClick}>Sign In</button>
                </form>
            </div>
            <div class="toggle-container">
                <div class="toggle">
                    <div class="toggle-panel toggle-left">
                        <h1>Welcome Back!</h1>
                        <p>Enter your personal details to use all of site features</p>
                        <button class="hidden" onClick={handleLoginClick}>Sign In</button>
                    </div>
                    <div class="toggle-panel toggle-right">
                        <h1>Hello, Friend!</h1>
                        <p>Register with your personal details to use all of site features</p>
                        <button class="hidden" onClick={handleRegisterClick}>Sign Up</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
  );
};

export default LoginSignup;
