import React from "react";

function GamePopup({ onClose, onSongSubmit, selectedGame, currentUserId, ownerId }) {
    const isOwner = ownerId === currentUserId;

    return (
        <div className="main-popup">
            <h1
                className='close-button'
                onClick={() => {
                    onClose();
                }}
            >X</h1>
            <div className="game-title-row">
                <h2>{selectedGame.title}</h2>
                <span className='game-code'>({selectedGame.gameCode})</span>
            </div>
            <p className='popup-due-date'>Due {selectedGame.dueDate}</p>
            <form
                className='submit-song-form'
                onSubmit={(e) => {
                    e.preventDefault();
                    const songName = e.target.songName.value;
                    const songArtist = e.target.songArtist.value;
                    const songComment = e.target.songComment.value;
                    onSongSubmit(songName, songArtist, songComment);
                }}
            >
                <label>
                    Song Name:
                    <input type="text" name="songName" required />
                </label>
                <label>
                    Artist: 
                    <input type="text" name="songArtist" required />
                </label>
                <label htmlFor='songComment'>Comments:</label>
                <textarea
                    id="songComment"
                    name="songComment"
                    rows={2}
                    style={{ width: '100%', resize: 'vertical' }}
                />
                <button type="submit">Submit Song</button>
            </form>
            {isOwner && (
                <h1 
                    className="next-page-arrow"
                    onClick={() => {
                        onClose();
                    }}
                >{'>'}</h1>
            )}
        </div>
    );
}

export default GamePopup;