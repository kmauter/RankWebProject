import React, { useRef } from "react";

function CreateRankPopup({ onClose, onCreate, createdGameCode}) {
    // Use refs to ensure test compatibility
    const themeRef = useRef();
    const submissionDuedateRef = useRef();
    const rankDuedateRef = useRef();
    return (
        <>
            <div className="game-title-row">
                <h2>Create a Rank</h2>
                <button onClick={onClose} className="close-button-details">X</button>
            </div>
            <form
                className="create-rank-form"
                onSubmit={(e) => {
                    e.preventDefault();
                    const theme = themeRef.current.value;
                    const submissionDuedate = submissionDuedateRef.current.value;
                    const rankDuedate = rankDuedateRef.current.value;
                    onCreate(theme, submissionDuedate, rankDuedate);
                }}
            >
                <label>
                    Theme:  
                    <input ref={themeRef} className='input-form' type="text" name="theme" required />
                </label>
                <label>
                    Submission Due Date:  
                    <input ref={submissionDuedateRef} className='input-form' type="date" name="submissionDuedate" required />
                </label>
                <label>
                    Rank Due Date:  
                    <input ref={rankDuedateRef} className='input-form' type="date" name="rankDuedate" required />
                </label>
                <button type="submit">Create Game</button>
            </form>
            {createdGameCode && (
                <p>
                    Game created successfully! Your game code is: {createdGameCode}
                </p>
            )}
        </>
    );
}

export default CreateRankPopup;