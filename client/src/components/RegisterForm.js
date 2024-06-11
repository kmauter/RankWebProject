import React, { useState } from 'react';

import axios from 'axios';
import { Form , Button } from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';

import FormField from './FormField';
import { routes } from './Routes';
import 'bootstrap/dist/css/bootstrap.min.css';
import '../styles/CustomButton.css';

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
        <div className="flex justify-center items-center min-h-screen w-full px-4">
            <Form onSubmit={handleRegister} className="w-full max-w-2xl mx-auto bg-white rounded-lg shadow-lg p-4 md:p-8">
                <div className='flex flex-col md:flex-row'>
                    <div className='flex flex-col w-full md:w-1/2 md:pr-2'>
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
                    <div className='flex flex-col w-full md:w-1/2 md:pl-2'>
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
                <div className='flex justify-between'>
                    <Link to={routes.login} className="text-blue-600 hover:text-blue-800">
                        Login
                    </Link>
                    <Button type="submit" className="custom-btn">
                        Register
                    </Button>
                </div>
            </Form>
        </div>
    );
}

export default RegisterForm;