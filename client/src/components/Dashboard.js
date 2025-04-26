import React from 'react';

function Dashboard() {
    return (
        <div className="dashboard">
            <header className="dashboard-header">
                {/* Top-left corner image */}
                <img 
                    src={require('../assets/Corner1.png')} 
                    alt="Top Left Corner" 
                    className="corner-image top-left" 
                />
                {/* Top-right corner image */}
                <img 
                    src={require('../assets/Corner8.png')} 
                    alt="Top Right Corner" 
                    className="corner-image top-right" 
                />
                {/* Bottom-left corner image */}
                <img 
                    src={require('../assets/Corner2.png')} 
                    alt="Bottom Left Corner" 
                    className="corner-image bottom-left" 
                />
                {/* Bottom-right corner image */}
                <img 
                    src={require('../assets/Corner3.png')} 
                    alt="Bottom Right Corner" 
                    className="corner-image bottom-right" 
                />
                {/* Logo aligned left */}
                <img 
                    src={require('../assets/RanK.png')} 
                    alt="Logo" 
                    className="dashboard-logo" 
                />
                {/* User icon aligned right */}
                <img 
                    src={require('../assets/UserImg.png')} 
                    alt="User Icon" 
                    className="user-icon" 
                />
            </header>
            <footer className="dashboard-footer">
                <img
                    src={require('../assets/Corner5.png')} 
                    alt="Footer Left" 
                    className="corner-image bottom-left"
                />
                <img
                    src={require('../assets/Corner7.png')} 
                    alt="Footer Right" 
                    className="corner-image bottom-right"
                />
                <img
                    src={require('../assets/Corner4.png')} 
                    alt="Footer Center" 
                    className="corner-image top-right"
                />
                <img
                    src={require('../assets/Corner6.png')} 
                    alt="Footer Center" 
                    className="corner-image top-left"
                />
                <div className="footer-content">
                    {/* 4 additional corners */}
                    <img 
                        src={require('../assets/Corner1.png')} 
                        alt="Top Left Corner" 
                        className="corner-image top-left" 
                    />
                    <img 
                        src={require('../assets/Corner8.png')} 
                        alt="Top Right Corner" 
                        className="corner-image top-right" 
                    />
                    <img 
                        src={require('../assets/Corner2.png')} 
                        alt="Bottom Left Corner" 
                        className="corner-image bottom-left" 
                    />
                    <img 
                        src={require('../assets/Corner3.png')} 
                        alt="Bottom Right Corner" 
                        className="corner-image bottom-right" 
                    />
                    {/* Centered text box */}
                    <div className="footer-text-box">
                        <p>JOIN A RANK</p>
                    </div>
                </div>
            </footer>
        </div>
    );
}

export default Dashboard;