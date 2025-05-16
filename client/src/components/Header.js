import React from 'react';

function Header({ onUserIconClick }) {
    return (
        <header className="dashboard-header">
            <img src={require('../assets/Corner1.png')} alt="Header TLeft" className="corner-image top-left" />
            <img src={require('../assets/Corner8.png')} alt="Header TRight" className="corner-image top-right" />
            <img src={require('../assets/Corner2.png')} alt="Header BLeft" className="corner-image bottom-left" />
            <img src={require('../assets/Corner3.png')} alt="Header BRight" className="corner-image bottom-right" />
            <img src={require('../assets/RanK.png')} alt="Logo" className="dashboard-logo" />
            <img src={require('../assets/UserImg.png')} alt="User Icon" className="user-icon" onClick={onUserIconClick} />
        </header>
    );
}

export default Header;