import React from "react";

function GameSettings({ 
    game, 
    onBack, 
    onGameSettingsClose,
    submissionDueDate,
    rankDueDate,
    onSubmissionDueDateChange,
    onRankDueDateChange,
    onSaveSubmissionDueDate,
    onSaveRankDueDate,
    songs,
    onDeleteSong,
    players,
    onRemovePlayer,
    ownerId
 }) {
    return (
        <div className="game-settings">
            <button onClick={onGameSettingsClose} className="close-button-details">X</button>
            <button onClick={onBack} className="back-button">{'<<'}</button>
            <h2 style={{ textAlign: "center" }}>Game settings</h2>
            {/*
            The user can do the following actions:
            1. Change the Submission Due Date
            2. Change the Rank Due Date
            3. See all songs submitted by users for this game
            3a. Delete a song submitted by a user
            4. See all players in the game
            4a. Remove a player from the game
            */}
            <div className="game-settings-columns">
                {/* Due Dates Section */}
                <div className="settings-column">
                    <h3>Submission Due Date</h3>
                    <input
                        type="date"
                        className='input-form'
                        value={submissionDueDate}
                        onChange={e => onSubmissionDueDateChange(e.target.value)}
                    />
                    <button onClick={() => onSaveSubmissionDueDate(submissionDueDate)}>(+)</button>
                    <h3>Rank Due Date</h3>
                    <input
                        type="date"
                        className='input-form'
                        value={rankDueDate}
                        onChange={e => onRankDueDateChange(e.target.value)}
                    />
                    <button onClick={() => onSaveRankDueDate(rankDueDate)}>(+)</button>
                </div>

                {/* Songs Section */}
                <div className="settings-column">
                    <h3>All Submitted Songs</h3>
                    <ul>
                        {songs.map(song => (
                            <li key={song.id}>
                                <strong>{song.song_name}</strong> by {song.artist}
                                <button onClick={() => onDeleteSong(song.id)}>(X)</button>
                            </li>
                        ))}
                    </ul>
                </div>

                {/* Players Section */}
                <div className="settings-column">
                    <h3>Players</h3>
                    <ul>
                        {players.map(player => (
                            <li key={player.id}>
                                {player.username}
                                {player.id !== ownerId && (
                                    <button onClick={() => onRemovePlayer(game.gameCode, player.id)}>(X)</button>
                                )}
                            </li>
                        ))}
                    </ul>
                </div>
            </div>
        </div>
    );
}

export default GameSettings;