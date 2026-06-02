import React, { useState } from 'react';
import { Form, Button } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import axios from 'axios';

import FormField from './FormField';
import { routes } from './Routes';
import 'bootstrap/dist/css/bootstrap.min.css';
import '../styles/CustomButton.css';
import '../styles/index.css';

function ForgotPassword() {
    const [identifier, setIdentifier] = useState('');
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setMessage('');
        setError('');
        setLoading(true);

        try {
            const response = await axios.post('/api/forgot-password', { identifier });
            setMessage(response.data.message);
        } catch (err) {
            const data = err.response?.data;
            setError(data?.error || 'Something went wrong. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="home-bg">
            <img src={require('../assets/RankWebLogo.png')} alt="RankWeb Logo" className="home-logo" />
            <div className="centered-container">
                <Form onSubmit={handleSubmit} className="form-container">
                    <>
                        {error && <p className="error-message">{error}</p>}
                        {message && <p className="success-message">{message}</p>}
                        <FormField
                            id="identifier"
                            label="Username or Email"
                            type="text"
                            value={identifier}
                            onChange={(e) => setIdentifier(e.target.value)}
                        />
                        <div className='form-footer'>
                            <Link to={routes.login} className="link" style={{ marginRight: '1.5rem' }}>
                                Back to Login
                            </Link>
                            <Button type="submit" className="custom-btn" disabled={loading}>
                                {loading ? 'Sending...' : 'Send New Password'}
                            </Button>
                        </div>
                    </>
                </Form>
            </div>
        </div>
    );
}

export default ForgotPassword;