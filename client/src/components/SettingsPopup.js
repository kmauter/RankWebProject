import React from 'react';

const SettingsPopup = ({ onClose, onSpotifyConnect, onYouTubeConnect }) => {
    return (
        <div className="settings-popup">
            <h2>Settings</h2>
            <button className="oauth-btn spotify-btn" onClick={onSpotifyConnect}>
                Connect Spotify
            </button>
            <button className="oauth-btn youtube-btn" onClick={onYouTubeConnect}>
                Connect YouTube
            </button>
            <p className='close-popup' onClick={onClose}>
                Close
            </p>
        </div>
    );
};

export default SettingsPopup;
