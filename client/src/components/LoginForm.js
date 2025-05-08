import React, { useState } from 'react';

import axios from 'axios';
import { Form, Button } from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';

import FormField from './FormField';
import { routes } from './Routes';
import 'bootstrap/dist/css/bootstrap.min.css';
import '../styles/CustomButton.css';
import '../styles/index.css';

import { jwtDecode } from 'jwt-decode';

function LoginForm() {
    // States to store username, password, and error message
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [errorMessage, setErrorMessage] = useState('');
    const navigate = useNavigate();

    // Function to handle form submission
    const handleLogin = (e) => {
        e.preventDefault();
        
        axios.post('/login', {
            username,
            password
        })
        .then(response => {
            const token = response.data.token; // Assuming the token is returned in the response
            localStorage.setItem('authToken', token); // Store the token in local storage
            const user = jwtDecode(token); // Decode the token to get user info
            console.log("Logged in user: ", user); // Log the user info for debugging
            navigate('/dashboard'); // Handle successful login here (e.g., redirect to dashboard)
        })
        .catch(error => {
            console.log(error);
            setErrorMessage('Invalid username or password'); // Set the error message
        });
    };
    
    return (
        <div className="home-bg">
            <img src={require('../assets/RankWebLogo.png')} alt="RankWeb Logo" className="home-logo" />
            <div className="centered-container">
                <Form onSubmit={handleLogin} className="form-container">
                    <>
                        {errorMessage && <p className="error-message">{errorMessage}</p>} {/* Display error message */}
                        <FormField 
                            id="username" 
                            label="Username" 
                            type="text" 
                            value={username} 
                            onChange={(e) => setUsername(e.target.value)} 
                        />
                        <FormField 
                            id="password" 
                            label="Password" 
                            type="password" 
                            value={password} 
                            onChange={(e) => setPassword(e.target.value)}
                        />
                        <div className='form-footer'>
                            <Link to={routes.register} className="link">
                                Register
                            </Link>
                            <Button type="submit" className="custom-btn">
                                Login
                            </Button>
                        </div>
                    </>
                </Form>
            </div>
        </div>
    );
}

export default LoginForm;