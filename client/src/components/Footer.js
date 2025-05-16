import React from 'react';

function Footer({ onJoinClick, onCreateClick }) {
    return (
        <footer className="dashboard-footer">
            <img src={require('../assets/Corner5.png')} alt="Bottom Left Corner" className="corner-image bottom-left" />
            <img src={require('../assets/Corner7.png')} alt="Bottom Right Corner" className="corner-image bottom-right" />
            <img src={require('../assets/Corner4.png')} alt="Top Right Corner" className="corner-image top-right" />
            <img src={require('../assets/Corner6.png')} alt="Top Left Corner" className="corner-image top-left" />
            <div className="footer-container">
                <img src={require('../assets/Corner1.png')} alt="Top Left Corner" className="corner-image top-left" />
                <img src={require('../assets/Corner8.png')} alt="Top Right Corner" className="corner-image top-right" />
                <img src={require('../assets/Corner2.png')} alt="Bottom Left Corner" className="corner-image bottom-left" />
                <img src={require('../assets/Corner3.png')} alt="Bottom Right Corner" className="corner-image bottom-right" />
                <div className="footer-text-box" onClick={onJoinClick}>
                    <p>JOIN A RANK</p>
                </div>
            </div>
            <div className="footer-container">
                <img src={require('../assets/Corner1.png')} alt="Top Left Corner" className="corner-image top-left" />
                <img src={require('../assets/Corner8.png')} alt="Top Right Corner" className="corner-image top-right" />
                <img src={require('../assets/Corner2.png')} alt="Bottom Left Corner" className="corner-image bottom-left" />
                <img src={require('../assets/Corner3.png')} alt="Bottom Right Corner" className="corner-image bottom-right" />
                <div className="footer-text-box" onClick={onCreateClick}>
                    <p>CREATE A RANK</p>
                </div>
            </div>
        </footer>
    );
}

export default Footer;