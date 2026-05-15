import React, { useState, useContext, useEffect } from 'react';
import Header from './Header';
import Footer from './Footer';
import GamePreview from './GamePreview';
import CreateRankPopup from './CreateRankPopup';
import JoinRankPopup from './JoinRankPopup';
import GameDetails from './GameDetails';
import { UserContext } from '../contexts/UserContext';
import GameSettings from './GameSettings';
import SettingsPopup from './SettingsPopup';
import ConfirmDialog from './ConfirmDialog';

function Dashboard() {
    const [isUserMenuVisible, setUserMenuVisible] = useState(false);
    const [isSettingsPopupVisible, setSettingsPopupVisible] = useState(false);
    const [selectedGame, setSelectedGame] = useState(null);
    const [isJoinRankPopupVisible, setJoinRankPopupVisible] = useState(false);
    const [isCreateRankPopupVisible, setCreateRankPopupVisible] = useState(false);
    const [createdGameCode, setCreatedGameCode] = useState(null); // State to hold the created game code
    const [gamePreviews, setGamePreviews] = useState([]); // State to hold game previews
    const [showGameSettings, setShowGameSettings] = useState(false); // State to control game settings visibility
    const [songs, setSongs] = useState([]); // State to hold songs for the selected game
    const [players, setPlayers] = useState([]); // State to hold players for the selected game
    const [submissionDueDate, setSubmissionDueDate] = useState('');
    const [rankDueDate, setRankDueDate] = useState('');
    const [userSongs, setUserSongs] = useState([]);
    const [userRanking, setUserRanking] = useState([]);
    const [notification, setNotification] = useState(null); // { message, type: 'error' | 'success' }
    const [confirmDialog, setConfirmDialog] = useState(null); // { message, onConfirm }

    const { user, logout } = useContext(UserContext);

    const showNotification = (message, type = 'error') => {
        setNotification({ message, type });
        setTimeout(() => setNotification(null), 4000);
    };

    const handleUserIconClick = () => {
        console.log('User:', user); // Log user info for debugging
        setUserMenuVisible(!isUserMenuVisible);
    };

    const handleSettingsClick = () => {
        setSettingsPopupVisible(!isSettingsPopupVisible);
    };

    const handleGameClick = (game) => {
        fetchSongs(game.gameCode);
        setSelectedGame(game);
    };

    const handleLogout = () => {
        setConfirmDialog({
            message: 'Are you sure you want to log out?',
            onConfirm: () => {
                setConfirmDialog(null);
                logout();
                window.location.href = '/';
            }
        });
    };

    const handleJoinClick = () => {
        setJoinRankPopupVisible(!isJoinRankPopupVisible);
    };

    const handleCreateClick = () => {
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
                console.log('Fetched games:', data); // Log the fetched games for debugging
                setGamePreviews(data); // Update the state with the fetched games
            } else {
                window.location.href = '/';
            }
        } catch (error) {
        }
    };

    const fetchUserSongs = async (gameCode) => {
        try {
            const token = localStorage.getItem('authToken');
            const response = await fetch(`/api/my-game-songs?game_code=${encodeURIComponent(gameCode)}`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });
            if (response.ok) {
                const data = await response.json();
                setUserSongs(data);
            } else {
                setUserSongs([]);
            }
        } catch (error) {
            setUserSongs([]);
        }
    };

    const fetchGameDetails = async (gameCode) => {
        try {
            const token = localStorage.getItem('authToken'); // Get the JWT token from localStorage
            const response = await fetch(`/api/game/${encodeURIComponent(gameCode)}`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`, // Include the token in the Authorization header
                    'Content-Type': 'application/json',
                },
            });

            if (response.ok) {
                const data = await response.json();
                console.log('Fetched game details:', data); // Log the fetched game details for debugging
                setSelectedGame(data); // Update the state with the fetched game details
                setSubmissionDueDate(data.submissionDueDate);
                setRankDueDate(data.rankDueDate);
            } else {
                setSelectedGame(null); // Reset selected game if fetching fails
            }
        } catch (error) {
            setSelectedGame(null); // Reset selected game if fetching fails
        }
    };

    const fetchSongs = async (gameCode) => {
        try {
            const token = localStorage.getItem('authToken'); // Get the JWT token from localStorage
            const response = await fetch(`/api/game/${encodeURIComponent(gameCode)}/songs`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                },
            });

            if (response.ok) {
                const data = await response.json();
                setSongs(data); // Update the state with the fetched songs
            } else {
                setSongs([]); // Optionally clear songs on failure
            }
        } catch (error) {
            setSongs([]); // Optionally clear songs on error
        }
    };

    const fetchPlayers = async (gameCode) => {
        try {
            const token = localStorage.getItem('authToken');
            const response = await fetch(`/api/game/${encodeURIComponent(gameCode)}/players`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                },
            });

            if (response.ok) {
                const data = await response.json();
                setPlayers(data); // Update the state with the fetched players
            } else {
                setPlayers([]); // Optionally clear players on failure
            }
        } catch (error) {
            setPlayers([]); // Optionally clear players on error
        }
    };

    const fetchUserRanking = async (gameCode) => {
        try {
            const token = localStorage.getItem('authToken');
            const response = await fetch(`/api/game/${gameCode}/rankings`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });
            if (response.ok) {
                const data = await response.json();
                setUserRanking(data.ranking || []);
            } else {
                setUserRanking([]);
            }
        } catch (error) {
            setUserRanking([]);
        }
    };
                            
    useEffect(() => {
        fetchGames();
    }, []); // Empty dependency array ensures this runs only once when the component mounts

    useEffect(() => {
        if (showGameSettings && selectedGame) {
            // Fetch songs, players, and due dates for the selected game
            fetchGameDetails(selectedGame.gameCode);
            fetchSongs(selectedGame.gameCode);
            fetchPlayers(selectedGame.gameCode);
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [showGameSettings]);

    useEffect(() => {
        if (selectedGame && !showGameSettings && user) {
            fetchUserSongs(selectedGame.gameCode);
            fetchSongs(selectedGame.gameCode);
        }
    }, [selectedGame, showGameSettings, user]);

    useEffect(() => {
        if (selectedGame && selectedGame.status === 'rankings') {
            fetchUserRanking(selectedGame.gameCode);
        }
    }, [selectedGame]);

    const handleCreateGame = async (theme, description, submissionDuedate, rankDuedate, maxSubmissionsPerUser) => {
        try {
            const token = localStorage.getItem('authToken'); // Get the JWT token from localStorage
            const response = await fetch('/api/games', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`, // Include the token in the Authorization header
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    theme,
                    description,
                    submissionDuedate,
                    rankDuedate,
                    maxSubmissionsPerUser
                }),
            });
    
            if (response.ok) {
                const data = await response.json();
                setCreatedGameCode(data.game_code);
                fetchGames(); // Refresh the game previews after creating a new game
            } else {
                const data = await response.json();
                showNotification(data.error || 'Failed to create game');
            }
        } catch (error) {
            showNotification('Error creating game. Please try again.');
        }
    };

    const handleJoinGame = async (gameCode) => {
        try {
            const token = localStorage.getItem('authToken'); // Get the JWT token from localStorage
            const response = await fetch('/api/join-game', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`, // Include the token in the Authorization header
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    game_code: gameCode,
                }),
            });
    
            if (response.ok) {
                fetchGames(); // Refresh the game previews after joining a new game
            } else {
                const data = await response.json();
                showNotification(data.error || 'Failed to join game');
            }
        } catch (error) {
            showNotification('Error joining game. Please try again.');
        }
    }

    const handleSongSubmission = async (songName, songArtist, songComment) => {
        try {
            const token = localStorage.getItem('authToken')
            const response = await fetch('/api/submit-song', {
                method: 'POST',
                headers: {
                    "Authorization": `Bearer ${token}`,
                    "Content-Type": 'application/json',
                },
                body: JSON.stringify({
                    game_code: selectedGame.gameCode,
                    song_name: songName,
                    artist: songArtist,
                    comment: songComment,
                }),
            });
            if (response.ok) {
                // refresh the songs list after submission
                fetchSongs(selectedGame.gameCode);
                fetchUserSongs(selectedGame.gameCode);
            } else {
                const data = await response.json();
                showNotification(data.error || 'Failed to submit song');
            }
        } catch (error) {
            showNotification('Error submitting song. Please try again.');
        }
    }

    const handleDeleteSong = (songId) => {
        setConfirmDialog({
            message: 'Delete this song?',
            onConfirm: () => {
                setConfirmDialog(null);
                performDeleteSong(songId);
            }
        });
    };

    const performDeleteSong = async (songId) => {
        try {
            const token = localStorage.getItem('authToken');
            const response = await fetch(`/api/song/${songId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                },
            });

            if (response.ok) {
                fetchSongs(selectedGame.gameCode);
                fetchUserSongs(selectedGame.gameCode);
            } else {
                const data = await response.json().catch(() => ({}));
                showNotification(data.error || 'Failed to delete song');
            }
        } catch (error) {
            showNotification('Error deleting song. Please try again.');
        }
    }

    const handleRemovePlayer = (gameCode, playerId) => {
        setConfirmDialog({
            message: 'Remove this player from the game?',
            onConfirm: () => {
                setConfirmDialog(null);
                performRemovePlayer(gameCode, playerId);
            }
        });
    };

    const performRemovePlayer = async (gameCode, playerId) => {
        try {
            const token = localStorage.getItem('authToken');
            const response = await fetch(`/api/game/${encodeURIComponent(gameCode)}/player/${playerId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                },
            });

            if (response.ok) {
                fetchPlayers(selectedGame.gameCode);
            } else {
                const data = await response.json().catch(() => ({}));
                showNotification(data.error || 'Failed to remove player');
            }
        } catch (error) {
            showNotification('Error removing player. Please try again.');
        }
    }

    const handleSaveSubmissionDueDate = async (newDate) => {
        try {
            const token = localStorage.getItem('authToken');
            const response = await fetch(`/api/game/${selectedGame.gameCode}/update-game`, {
                method: 'PATCH',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ submissionDuedate: newDate }),
            });
            if (response.ok) {
                // Optionally refetch game details or show a success message
                fetchGameDetails(selectedGame.gameCode);
            } else {
            }
        } catch (error) {
        }
    };

    const handleSaveRankDueDate = async (newDate) => {
        try {
            const token = localStorage.getItem('authToken');
            const response = await fetch(`/api/game/${selectedGame.gameCode}/update-game`, {
                method: 'PATCH',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ rankDuedate: newDate }),
            });
            if (response.ok) {
                fetchGameDetails(selectedGame.gameCode);
            } else {
            }
        } catch (error) {
        }
    };

    const handleSaveRanking = async (ranking) => {
        if (!selectedGame || !user) {
            showNotification('No game or user selected.');
            return;
        }
        try {
            const token = localStorage.getItem('authToken');
            const response = await fetch(`/api/game/${selectedGame.gameCode}/rankings`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ ranking: ranking }),
            });
            if (response.ok) {
                showNotification('Ranking saved!', 'success');
            } else {
                const data = await response.json().catch(() => ({}));
                showNotification(data.error || 'Failed to save ranking');
            }
        } catch (error) {
            showNotification('Error saving ranking. Please try again.');
        }
    };

    const handleSpotifyConnect = async () => {
        if (!user || !user.user_id) {
            showNotification("You must be logged in to connect Spotify.");
            return;
        }
        try {
            const token = localStorage.getItem('authToken');
            const response = await fetch('/api/connect-spotify', {
                headers: { 'Authorization': `Bearer ${token}` },
            });
            if (response.ok) {
                const data = await response.json();
                window.open(data.auth_url, "_blank", "noopener,noreferrer");
            } else {
                showNotification("Failed to connect Spotify.");
            }
        } catch {
            showNotification("Error connecting to Spotify.");
        }
    };

    const handleYouTubeConnect = async () => {
        if (!user || !user.user_id) {
            showNotification("You must be logged in to connect YouTube.");
            return;
        }
        try {
            const token = localStorage.getItem('authToken');
            const response = await fetch('/api/connect-youtube', {
                headers: { 'Authorization': `Bearer ${token}` },
            });
            if (response.ok) {
                const data = await response.json();
                window.open(data.auth_url, "_blank", "noopener,noreferrer");
            } else {
                showNotification("Failed to connect YouTube.");
            }
        } catch {
            showNotification("Error connecting to YouTube.");
        }
    };

    return (
        <div className="dashboard">
            {notification && (
                <div className={`notification-banner ${notification.type}`}>
                    {notification.message}
                </div>
            )}
            {confirmDialog && (
                <ConfirmDialog
                    message={confirmDialog.message}
                    onConfirm={confirmDialog.onConfirm}
                    onCancel={() => setConfirmDialog(null)}
                />
            )}
            <Header onUserIconClick={() => handleUserIconClick()} />
            {isUserMenuVisible && (
                    <div className="user-menu">
                        <p className="logout-text" onClick={() => handleLogout()}>Log Out</p>
                        <p className="settings-text" onClick={() => handleSettingsClick()}>Settings</p>
                    </div>
                )}
            {isSettingsPopupVisible && (
                <SettingsPopup
                    onClose={handleSettingsClick}
                    onSpotifyConnect={handleSpotifyConnect}
                    onYouTubeConnect={handleYouTubeConnect}
                />
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
                    {selectedGame ? (
                        <div className="game-details-container">
                            {showGameSettings ? (
                                <GameSettings
                                    game={selectedGame}
                                    onGameSettingsClose={() => {
                                        setSelectedGame(null);
                                        setShowGameSettings(false);
                                    }}
                                    onBack={() => setShowGameSettings(false)}
                                    submissionDueDate={submissionDueDate}
                                    rankDueDate={rankDueDate}
                                    onSubmissionDueDateChange={setSubmissionDueDate}
                                    onRankDueDateChange={setRankDueDate}
                                    onSaveSubmissionDueDate={handleSaveSubmissionDueDate}
                                    onSaveRankDueDate={handleSaveRankDueDate}
                                    songs={songs}
                                    onDeleteSong={handleDeleteSong}
                                    players={players}
                                    onRemovePlayer={handleRemovePlayer}
                                    ownerId={selectedGame.ownerId}
                                />
                            ) : (
                                <GameDetails
                                    game={selectedGame}
                                    songs={songs}
                                    userRanking={userRanking}
                                    onBack={() => setSelectedGame(null)}
                                    currentUser={user}
                                    onSongSubmit={handleSongSubmission}
                                    onNextPage={() => setShowGameSettings(true)}
                                    userSongs={userSongs}
                                    onDeleteSong={handleDeleteSong}
                                    onSaveRanking={handleSaveRanking}
                                />
                            )}
                        </div>
                    ) : isCreateRankPopupVisible ? (
                        <div className="game-details-container">
                            <CreateRankPopup
                                onClose={() => {
                                    setCreateRankPopupVisible(false);
                                    setCreatedGameCode(null);
                                }}
                                onCreate={handleCreateGame}
                                createdGameCode={createdGameCode}
                            />
                        </div>
                    ) : isJoinRankPopupVisible ? (
                        <div className="game-details-container">
                            <JoinRankPopup
                                onClose={() => {
                                    setJoinRankPopupVisible(false);
                                }}
                                onJoin={handleJoinGame} // Pass the join function to the popup
                            />
                        </div>
                    ) : (
                        <div className='game-previews-grid'>
                            {gamePreviews.map((game, index) => (
                                <GamePreview
                                    key={index}
                                    title={game.title}
                                    status={game.status}
                                    image={game.image}
                                    submissionDueDate={game.submissionDueDate}
                                    rankDueDate={game.rankDueDate}
                                    onClick={() => handleGameClick(game)}
                                />
                            ))}
                        </div>
                    )}
                </div>
            </main>
            {/* {isJoinRankPopupVisible && (
                <JoinRankPopup
                    onClose={() => {
                        setJoinRankPopupVisible(false);
                    }}
                    onJoin={handleJoinGame} // Pass the join function to the popup
                />
            )} */}
            {/* {isCreateRankPopupVisible && (
                <CreateRankPopup
                    onClose={() => {
                        setCreateRankPopupVisible(false);
                        setCreatedGameCode(null);
                    }}
                    onCreate={handleCreateGame}
                    createdGameCode={createdGameCode}
                />
            )} */}
            <Footer
                onJoinClick={() => handleJoinClick()}
                onCreateClick={() => handleCreateClick()}
            />
        </div>
    );
}

export default Dashboard;