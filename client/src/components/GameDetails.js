import React, { useState } from "react";

function GameDetails({ game, onBack, currentUser, onSongSubmit, onNextPage, userSongs, onDeleteSong }) {
    const [songName, setSongName] = useState('');
    const [songArtist, setSongArtist] = useState('');
    const [songComment, setSongComment] = useState('');
    
    const isOwner = game.owner.id === currentUser.user_id;
    const dueDate =
    game.status === 'submissions'
        ? game.submissionDueDate
        : game.rankDueDate;

    return (
        <div className="game-details">
            <button onClick={onBack} className="close-button-details">X</button>

            <div className="game-title-row">
                <h2>{game.title}</h2>
                <span className='game-code'>{game.gameCode}</span>
            </div>

            <p className='popup-due-date'>Due {dueDate}</p>
            
            <div className="form-section">
                <form
                    className='submit-song-form'
                    onSubmit={async (e) => {
                        e.preventDefault();
                        await onSongSubmit(songName, songArtist, songComment);
                        setSongName('');
                        setSongArtist('');
                        setSongComment('');
                    }}
                >
                    <div className="form-item">
                        <label>
                            Song Name:
                            <input 
                                className='input-form' 
                                type="text" 
                                name="songName" 
                                required
                                value={songName}
                                onChange={(e) => setSongName(e.target.value)}
                            />
                        </label>
                    </div>
                    <div className="form-item">
                        <label>
                            Artist:
                            <input 
                                className='input-form' 
                                type="text" 
                                name="songArtist" 
                                required 
                                value={songArtist}
                                onChange={e => setSongArtist(e.target.value)}
                            />
                        </label>
                    </div>
                    <div className="form-item">
                        <label htmlFor='songComment'>Comments:</label>
                        <textarea
                            id="songComment"
                            name="songComment"
                            rows={2}
                            style={{ width: '100%', resize: 'vertical' }}
                            value={songComment}
                            onChange={(e) => setSongComment(e.target.value)}
                        />
                    </div>
                    <button type="submit">Submit Song</button>
                </form>
            </div>

            <div className="user-songs-section" style={{ marginTop: '2em', width: '100%' }}>
                {userSongs.length === 0 ? (
                    <p style={{ textAlign: 'center' }}>No songs submitted yet.</p>
                ) : (
                    <>
                        <h3 style={{ textAlign: 'center' }}>Your Submitted Songs</h3>
                        <ul style={{ listStyle: 'none', padding: 0 }}>
                            {userSongs.map((song, idx) => (
                                <li key={song.id || idx} style={{ textAlign: 'center' }}>
                                    <strong>{song.song_name}</strong> - {song.artist}
                                    <button onClick={() => onDeleteSong(song.id)}>(X)</button>
                                </li>
                            ))}
                        </ul>
                    </>
                )}
            </div>

            {isOwner && (
                <button onClick={onNextPage} className="owner-next-button">{'>>'}</button>
            )}
        </div>
    );
}

export default GameDetails;