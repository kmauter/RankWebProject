import React, { useState } from 'react';
import axios from 'axios';

const SettingsPopup = ({ onClose, onSpotifyConnect, onYouTubeConnect }) => {
    const [oldPassword, setOldPassword] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [newPassword2, setNewPassword2] = useState('');
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');

    const handleChangePassword = async (e) => {
        e.preventDefault();
        setMessage('');
        setError('');

        try {
            const token = localStorage.getItem('authToken');
            const response = await axios.post('/api/change-password', {
                old_password: oldPassword,
                new_password: newPassword,
                new_password2: newPassword2
            }, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            setMessage(response.data.message);
            setOldPassword('');
            setNewPassword('');
            setNewPassword2('');
        } catch (err) {
            const data = err.response?.data;
            setError(data?.error || 'Something went wrong.');
        }
    };

    return (
        <div className="settings-popup">
            <h2>Settings</h2>
            <button className="oauth-btn spotify-btn" onClick={onSpotifyConnect}>
                Connect Spotify
            </button>
            <button className="oauth-btn youtube-btn" onClick={onYouTubeConnect}>
                Connect YouTube
            </button>

            <hr style={{ width: '80%', margin: '1.5rem auto' }} />

            <h3 style={{ fontSize: '1.8rem', marginBottom: '0.5rem' }}>Change Password</h3>
            {error && <p className="error-message" style={{color: 'rgb(64, 57, 43)'}}>{error}</p>}
            {message && <p className="success-message" style={{color: 'rgb(64, 57, 43)'}}>{message}</p>}
            <form onSubmit={handleChangePassword} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.8rem', width: '80%' }}>
                <input
                    type="password"
                    placeholder="Current password"
                    value={oldPassword}
                    onChange={e => setOldPassword(e.target.value)}
                    className="input-form"
                    style={{ width: '100%' }}
                    required
                />
                <input
                    type="password"
                    placeholder="New password"
                    value={newPassword}
                    onChange={e => setNewPassword(e.target.value)}
                    className="input-form"
                    style={{ width: '100%' }}
                    required
                />
                <input
                    type="password"
                    placeholder="Confirm new password"
                    value={newPassword2}
                    onChange={e => setNewPassword2(e.target.value)}
                    className="input-form"
                    style={{ width: '100%' }}
                    required
                />
                <button type="submit" className="general-button" style={{ fontSize: '1.5rem' }}>
                    Update Password
                </button>
            </form>

            <p className='close-popup' onClick={onClose} style={{ marginTop: '1.5rem' }}>
                Close
            </p>
        </div>
    );
};

export default SettingsPopup;