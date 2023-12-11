import React, { useState } from 'react';
import { auth } from './firebaseConfig'; // Ensure this path is correct
import { signInWithEmailAndPassword } from 'firebase/auth';
import './LoginSignup.css';
import { useNavigate } from 'react-router-dom';
function LoginSignup() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();
    const handleSubmit = async (event) => {
        event.preventDefault();
        setError(''); // Clear any previous error messages

        try {
            const userCredential = await signInWithEmailAndPassword(auth, email, password);
            // If needed, you can access the signed-in user via userCredential.user
            console.log('Logged in user:', userCredential.user);
            navigate('/userpage');
            // Redirect to another page or update the UI as needed
        } catch (error) {
            console.error('Error signing in with email and password:', error);
            setError(error.message); // Set error message to display to the user
        }
    };

    return (
        <div className="login-container">
            <h1>Welcome to TuneMosaic</h1>
            {error && <p style={{ color: 'red' }}>{error}</p>}
            <form onSubmit={handleSubmit}>
                <div>
                    <label htmlFor="email">Email:</label>
                    <input
                        type="email"
                        id="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                    />
                </div>
                <div>
                    <label htmlFor="password">Password:</label>
                    <input
                        type="password"
                        id="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                </div>
                <button type="submit">Login</button>
            </form>
        </div>
    );
}

export default LoginSignup;