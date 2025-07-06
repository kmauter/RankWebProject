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
        fetchSongs(game.gameCode);
        setSelectedGame(game);
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
                console.log('Fetched games:', data); // Log the fetched games for debugging
                setGamePreviews(data); // Update the state with the fetched games
            } else {
                console.error('Failed to fetch games');
                window.location.href = '/';
            }
        } catch (error) {
            console.error('Error fetching games:', error);
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
            console.error('Error fetching user songs:', error);
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
                console.error('Failed to fetch game details');
                setSelectedGame(null); // Reset selected game if fetching fails
            }
        } catch (error) {
            console.error('Error fetching game details:', error);
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
                console.error('Failed to fetch songs');
                setSongs([]); // Optionally clear songs on failure
            }
        } catch (error) {
            console.error('Error fetching songs:', error);
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
                console.error('Failed to fetch players');
                setPlayers([]); // Optionally clear players on failure
            }
        } catch (error) {
            console.error('Error fetching players:', error);
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
                console.log('Successfully joined the game');
                fetchGames(); // Refresh the game previews after joining a new game
            } else {
                console.error('Failed to join game');
            }
        } catch (error) {
            console.error('Error joining game:', error);
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
                console.log('Song submitted successfully');
                // refresh the songs list after submission
                fetchSongs(selectedGame.gameCode);
                fetchUserSongs(selectedGame.gameCode);
            } else {
                console.error('Failed to submit song');
            }
        } catch (error) {
            console.error('Error submitting song:', error);
        }
    }

    const handleDeleteSong = async (songId) => {
        try {
            const token = localStorage.getItem('authToken'); // Get the JWT token from localStorage
            const response = await fetch(`/api/song/${songId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`, // Include the token in the Authorization header
                    'Content-Type': 'application/json',
                },
            });

            if (response.ok) {
                console.log('Song deleted successfully');
                // Optionally, refresh the songs list after deletion
                fetchSongs(selectedGame.gameCode);
                fetchUserSongs(selectedGame.gameCode);
            } else {
                console.error('Failed to delete song');
            }
        } catch (error) {
            console.error('Error deleting song:', error);
        }
    }

    const handleRemovePlayer = async (gameCode, playerId) => {
        try {
            const token = localStorage.getItem('authToken'); // Get the JWT token from localStorage
            const response = await fetch(`/api/game/${encodeURIComponent(gameCode)}/player/${playerId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`, // Include the token in the Authorization header
                    'Content-Type': 'application/json',
                },
            });

            if (response.ok) {
                console.log('Player removed successfully');
                // Optionally, refresh the players list after removal
                fetchPlayers(selectedGame.gameCode);
            } else {
                console.error('Failed to remove player');
            }
        } catch (error) {
            console.error('Error removing player:', error);
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
                console.error('Failed to update submission due date');
            }
        } catch (error) {
            console.error('Error updating submission due date:', error);
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
                console.error('Failed to update rank due date');
            }
        } catch (error) {
            console.error('Error updating rank due date:', error);
        }
    };

    const handleSaveRanking = async (ranking) => {
        if (!selectedGame || !user) {
            alert('No game or user selected.');
            return;
        }
        try {
            const token = localStorage.getItem('authToken');
            // Only send non-null song IDs in order
            // const filteredRanking = ranking.filter(id => id !== null);
            const response = await fetch(`/api/game/${selectedGame.gameCode}/rankings`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ ranking: ranking }),
            });
            if (response.ok) {
                const data = await response.json();
                console.log('Ranking saved:', data);
                // alert('Ranking saved!');
            } else {
                const errorText = await response.text();
                console.error('Failed to save ranking:', errorText);
                // alert('Failed to save ranking.');
            }
        } catch (error) {
            console.error('Error saving ranking:', error);
            // alert('Error saving ranking.');
        }
    };

    const handleSpotifyConnect = () => {
        if (!user || !user.user_id) {
            alert("You must be logged in to connect Spotify.");
            return;
        }
        window.open(`http://127.0.0.1:5000/api/connect-spotify?user_id=${user.user_id}`, "_blank", "noopener,noreferrer");
    };

    const handleYouTubeConnect = () => {
        if (!user || !user.user_id) {
            alert("You must be logged in to connect YouTube.");
            return;
        }
        window.open(`http://127.0.0.1:5000/api/connect-youtube?user_id=${user.user_id}`, "_blank", "noopener,noreferrer");
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