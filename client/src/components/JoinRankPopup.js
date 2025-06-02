import React from "react";

function JoinRankPopup({ onClose, onJoin }) {
    return (
        <div className="main-popup">
            <h1
                className='close-button'
                onClick={() => {
                    onClose();
                }}
            >X</h1>
            <h2>Join a Rank</h2>
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
                <button type="submit">Join</button>
            </form>
        </div>
    );
}

export default JoinRankPopup;