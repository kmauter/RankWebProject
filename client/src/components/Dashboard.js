import React, { useState, useContext, useEffect } from 'react';
import Header from './Header';
import Footer from './Footer';
import GamePreview from './GamePreview';
import { UserContext } from '../contexts/UserContext';

function Dashboard() {
    const [isUserMenuVisible, setUserMenuVisible] = useState(false);
    const [isSettingsPopupVisible, setSettingsPopupVisible] = useState(false);
    const [isGamePopupVisible, setGamePopupVisible] = useState(false);
    const [selectedGame, setSelectedGame] = useState(null);
    const [isJoinRankPopupVisible, setJoinRankPopupVisible] = useState(false);
    const [isCreateRankPopupVisible, setCreateRankPopupVisible] = useState(false);
    const [createdGameCode, setCreatedGameCode] = useState(null); // State to hold the created game code
    const [gamePreviews, setGamePreviews] = useState([]); // State to hold game previews

    const { user, logout } = useContext(UserContext); // Assuming you have a UserContext to get user info

    // const gamePreviews = [
    //     { title: 'Songs About Capitalism', status: 'submissions' , dueDate: 'May 5' },
    //     { title: 'Songs Under 2 Mins', status: 'rankings', dueDate: 'May 7' },
    //     { title: 'Songs For Mothers Day', status: 'rankings', dueDate: 'May 8' },
    //     { title: 'Babytron Songs', status: 'results' }
    // ];

    const handleUserIconClick = () => {
        console.log('User icon clicked!');
        console.log('User:', user); // Log user info for debugging
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
        logout();
        window.location.href = '/';
    };

    const handleJoinClick = () => {
        console.log('Join a rank clicked!');
        setJoinRankPopupVisible(!isJoinRankPopupVisible);
    };

    const handleCreateClick = () => {
        console.log('Create a rank clicked!');
        setCreateRankPopupVisible(!isCreateRankPopupVisible);
    };

    const fetchGames = async () => {
        try {
            const token = localStorage.getItem('authToken'); // Get the JWT token from localStorage
            const response = await fetch('/api/user-games', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`, // Include the token in the Authorization header
                    'Content-Type': 'application/json',
                },
            });

            console.log('Response:', response); // Log the response for debugging

            if (response.ok) {
                const data = await response.json();
                setGamePreviews(data); // Update the state with the fetched games
            } else {
                console.error('Failed to fetch games');
            }
        } catch (error) {
            console.error('Error fetching games:', error);
        }
    };

    useEffect(() => {
        fetchGames();
    }, []); // Empty dependency array ensures this runs only once when the component mounts

    const handleCreateGame = async (theme, submissionDuedate, rankDuedate) => {
        try {
            const response = await fetch('/api/games', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    theme,
                    submissionDuedate,
                    rankDuedate,
                }),
            });
    
            if (response.ok) {
                const data = await response.json();
                console.log('Game created successfully:', data);
                setCreatedGameCode(data.game_code);
                // setCreateRankPopupVisible(false);
                fetchGames(); // Refresh the game previews after creating a new game
            } else {
                console.error('Failed to create game');
            }
        } catch (error) {
            console.error('Error creating game:', error);
        }
    };

    return (
        <div className="dashboard">
            <Header onUserIconClick={() => handleUserIconClick()} />
            {isUserMenuVisible && (
                    <div className="user-menu">
                        <p className="logout-text" onClick={() => handleLogout()}>Log Out</p>
                        <p className="settings-text" onClick={() => handleSettingsClick()}>Settings</p>
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
                <div className="main-popup">
                    <h2>{selectedGame.title}</h2>
                    <p>Status: {selectedGame.status}</p>
                    <p>Due Date: {selectedGame.dueDate}</p>
                    <p className='close-popup' onClick={closeGamePopup}>
                        Close
                    </p>
                </div>
            )}
            {isJoinRankPopupVisible && (
                <div className="main-popup">
                    <h2>Join a Rank</h2>
                    <p>Oops! This isn't ready yet.</p>
                    <p className='close-popup' onClick={() => setJoinRankPopupVisible(false)}>
                        Close
                    </p>
                </div>
            )}
            {isCreateRankPopupVisible && (
                <div className="main-popup">
                    <h1
                        className='close-button'
                        onClick={() => {
                            setCreateRankPopupVisible(false);
                            setCreatedGameCode(null); 
                        }}
                    >X</h1>
                    <h2>Create a Rank</h2>
                    <form
                        className="create-rank-form"
                        onSubmit={(e) => {
                            e.preventDefault();
                            const theme = e.target.theme.value;
                            const submissionDuedate = e.target.submissionDuedate.value;
                            const rankDuedate = e.target.rankDuedate.value;
                            handleCreateGame(theme, submissionDuedate, rankDuedate);
                        }}
                    >
                        <label>
                            Theme:  
                            <input type="text" name="theme" required />
                        </label>
                        <label>
                            Submission Due Date:  
                            <input type="date" name="submissionDuedate" required />
                        </label>
                        <label>
                            Rank Due Date:  
                            <input type="date" name="rankDuedate" required />
                        </label>
                        <button type="submit">Create Game</button>
                    </form>
                    {createdGameCode && (
                        <p>
                            Game created successfully! Your game code is: {createdGameCode}
                        </p>
                    )}
                </div>
            )}
            <Footer
                onJoinClick={() => handleJoinClick()}
                onCreateClick={() => handleCreateClick()}
            />
        </div>
    );
}

export default Dashboard;