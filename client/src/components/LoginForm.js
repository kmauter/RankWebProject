import React, { useState } from 'react';

import axios from 'axios';
import { Form , Button } from 'react-bootstrap';
import { Link } from 'react-router-dom';

import FormField from './FormField';
import { routes } from './Routes';
import 'bootstrap/dist/css/bootstrap.min.css';
import '../styles/CustomButton.css';


function LoginForm() {
    // States to store username and password
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');

    // Function to handle form submission
    const handleLogin = (e) => {
        e.preventDefault();
        
        axios.post('/login', {
            username,
            password
        })
        .then(response => {
            console.log(response.data);
            // Handle successful login here (e.g., redirect to dashboard)
        })
        .catch(error => {
            console.log(error);
            // Handle errors here (e.g., show error message on failure)
        });
    }
    
    return (
        <div className="flex justify-center items-center min-h-screen w-full px-4">
            <Form onSubmit={handleLogin} className="w-full max-w-md mx-auto bg-white rounded-lg shadow-lg p-4 md:p-8">
                <>
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
                    <div className='flex justify-between'>
                        <Link to={routes.register} className="text-blue-600 hover:text-blue-800">
                            Register
                        </Link>
                        <Button type="submit" className="custom-btn">
                            Login
                        </Button>
                    </div>
                </>
            </Form>
        </div>
    );
}

export default LoginForm;