import React, { useState } from 'react';

import axios from 'axios';
import { Form , Button } from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';

import FormField from './FormField';
import { routes } from './Routes';
import 'bootstrap/dist/css/bootstrap.min.css';
import '../styles/CustomButton.css';
import '../styles/index.css';

function RegisterForm() {
    const navigate = useNavigate();

    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [password2, setPassword2] = useState('');

    const handleRegister = (e) => {
        e.preventDefault();

        axios.post('/register', {
            username,
            email,
            password,
            password2
        })
        .then(response => {
            console.log(response.data);
            navigate(routes.login);
            // handle successful registration here
        })
        .catch(error => {
            console.log(error);
            // handle errors here
        });
    }

    return (
        <div className="home-bg">
            <img src={require('../assets/RankWebLogo.png')} alt="RankWeb Logo" className="home-logo" />
            <div className="centered-container">
                <Form onSubmit={handleRegister} className="form-container">
                    <div className='form-grid'>
                        <div className='form-column'>
                            <FormField 
                                id="username" 
                                label="Username" 
                                type="text" 
                                value={username} 
                                onChange={(e) => setUsername(e.target.value)} 
                            />
                            <FormField 
                                id="email" 
                                label="Email" 
                                type="email" 
                                value={email} 
                                onChange={(e) => setEmail(e.target.value)}
                            />
                        </div>
                        <div className='form-column'>
                            <FormField 
                                id="password" 
                                label="Password" 
                                type="password" 
                                value={password} 
                                onChange={(e) => setPassword(e.target.value)}
                            />
                            <FormField 
                                id="password2" 
                                label="Confirm Password" 
                                type="password" 
                                value={password2} 
                                onChange={(e) => setPassword2(e.target.value)}
                            />
                        </div>
                    </div>
                    <div className='form-footer'>
                        <Link to={routes.login} className="link">
                            Login
                        </Link>
                        <Button type="submit" className="custom-btn">
                            Register
                        </Button>
                    </div>
                </Form>
            </div>
        </div>
    );
}

export default RegisterForm;