import React from "react";

function JoinRankPopup({ onClose, onJoin }) {
    return (
        <div className="join-rank-popup">
            <button onClick={onClose} className="close-button-details">X</button>
            <div className="create-join-header">
                <h2>Join a Rank</h2>
            </div>
            <form
                className='join-rank-form'
                onSubmit={(e) => {
                    e.preventDefault();
                    const gameCode = e.target.gameCode.value;
                    console.log('Game code:', gameCode);
                    onJoin(gameCode); // Call the join function with the game code
                }}
            >
                <label>
                    Game Code:  
                    <input className='input-form' type="text" name="gameCode" required />
                </label>
                <button type="submit" className="general-button">Join</button>
            </form>
        </div>
    );
}

export default JoinRankPopup;