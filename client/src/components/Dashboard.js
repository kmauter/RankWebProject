import React, { useState } from 'react';
import GamePreview from './GamePreview';

function Dashboard() {
    const [isUserMenuVisible, setUserMenuVisible] = useState(false);
    const [isSettingsPopupVisible, setSettingsPopupVisible] = useState(false);
    const [isGamePopupVisible, setGamePopupVisible] = useState(false);
    const [selectedGame, setSelectedGame] = useState(null);

    const gamePreviews = [
        { title: 'Songs About Capitalism', status: 'submissions' , dueDate: 'May 5' },
        { title: 'Songs Under 2 Mins', status: 'rankings', dueDate: 'May 7' },
        { title: 'Songs For Mothers Day', status: 'rankings', dueDate: 'May 8' },
        { title: 'Babytron Songs', status: 'results' }
    ];

    const handleUserIconClick = () => {
        console.log('User icon clicked!');
        setUserMenuVisible(!isUserMenuVisible);
    };

    const handleSettingsClick = () => {
        console.log('Settings clicked!');
        setSettingsPopupVisible(!isSettingsPopupVisible);
    };

    const handleGameClick = (game) => {
        console.log('Game clicked:', game);
        setSelectedGame(game);
        setGamePopupVisible(true);
    };

    const closeGamePopup = () => {
        console.log('Game popup closed!');
        setGamePopupVisible(false);
        setSelectedGame(null);
    };

    const handleLogout = () => {
        console.log('User logged out!');
        // Add your logout logic here
    };

    return (
        <div className="dashboard">
            <header className="dashboard-header">
                {/* Top-left corner image */}
                <img 
                    src={require('../assets/Corner1.png')} 
                    alt="Header TLeft" 
                    className="corner-image top-left" 
                />
                {/* Top-right corner image */}
                <img 
                    src={require('../assets/Corner8.png')} 
                    alt="Header TRight" 
                    className="corner-image top-right" 
                />
                {/* Bottom-left corner image */}
                <img 
                    src={require('../assets/Corner2.png')} 
                    alt="Header BLeft" 
                    className="corner-image bottom-left" 
                />
                {/* Bottom-right corner image */}
                <img 
                    src={require('../assets/Corner3.png')} 
                    alt="Header BRight" 
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
                    onClick={handleUserIconClick}
                />
            </header>
            {isUserMenuVisible && (
                    <div className="user-menu">
                        <div className='logout-container'>
                            <p className="logout-text" onClick={handleLogout}>
                                Log Out
                            </p>
                        </div>
                        <div className='settings-container'>
                            <p className='settings-text' onClick={handleSettingsClick}>
                                Settings
                            </p>
                        </div>
                    </div>
                )}
            {isSettingsPopupVisible && (
                <div className="settings-popup">
                    <h2>Settings</h2>
                    <p>Oops! This isn't ready yet.</p>
                    <p className='close-popup' onClick={handleSettingsClick}>
                        Close
                    </p>
                </div>
            )}
            <main className="dashboard-main">
                <img
                    src={require('../assets/Corner6.png')} 
                    alt="Main TLeft" 
                    className="corner-image top-left"
                />
                <img
                    src={require('../assets/Corner4.png')} 
                    alt="Main TRight" 
                    className="corner-image top-right"
                />
                <img
                    src={require('../assets/Corner2.png')} 
                    alt="Main BLeft" 
                    className="corner-image bottom-left"
                />
                <img
                    src={require('../assets/Corner3.png')} 
                    alt="Main BRight" 
                    className="corner-image bottom-right"
                />
                <div className="main-content">
                    { /* Render game previews */ }
                    {gamePreviews.map((game, index) => (
                        <GamePreview
                            key={index}
                            title={game.title}
                            status={game.status}
                            image={game.image}
                            dueDate={game.dueDate}
                            onClick={() => handleGameClick(game)}
                        />
                    ))}
                </div>
            </main>
            {isGamePopupVisible && selectedGame && (
                <div className="game-popup">
                    <h2>{selectedGame.title}</h2>
                    <p>Status: {selectedGame.status}</p>
                    <p>Due Date: {selectedGame.dueDate}</p>
                    <p className='close-popup' onClick={closeGamePopup}>
                        Close
                    </p>
                </div>
            )}
            <footer className="dashboard-footer">
                <img
                    src={require('../assets/Corner5.png')} 
                    alt="Footer BLeft" 
                    className="corner-image bottom-left"
                />
                <img
                    src={require('../assets/Corner7.png')} 
                    alt="Footer BRight" 
                    className="corner-image bottom-right"
                />
                <img
                    src={require('../assets/Corner4.png')} 
                    alt="Footer TCenter" 
                    className="corner-image top-right"
                />
                <img
                    src={require('../assets/Corner6.png')} 
                    alt="Footer TCenter" 
                    className="corner-image top-left"
                />
                <div className="footer-container">
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
                <div className='footer-container'>
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
                    <div className="footer-text-box">
                        <p>CREATE A RANK</p>
                    </div>
                </div>
            </footer>
        </div>
    );
}

export default Dashboard;