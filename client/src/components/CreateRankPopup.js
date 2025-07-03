import React, { useRef } from "react";

function CreateRankPopup({ onClose, onCreate, createdGameCode}) {
    // Use refs to ensure test compatibility
    const themeRef = useRef();
    const submissionDuedateRef = useRef();
    const rankDuedateRef = useRef();
    const descriptionRef = useRef();
    const submissionLimitRef = useRef();
    return (
        <div className="create-rank-popup">
            <div className="create-join-header">
                <h2>Create a Rank</h2>
                <button onClick={onClose} className="close-button-details">X</button>
            </div>
            <form
                className="create-rank-form"
                onSubmit={(e) => {
                    e.preventDefault();
                    const theme = themeRef.current.value;
                    const description = descriptionRef.current.value;
                    const submissionDuedate = submissionDuedateRef.current.value;
                    const rankDuedate = rankDuedateRef.current.value;
                    const submissionLimit = submissionLimitRef.current.value;
                    onCreate(theme, description, submissionDuedate, rankDuedate, submissionLimit);
                }}
            >
                <label>
                    Theme:  
                    <input ref={themeRef} className='input-form' type="text" name="theme" required />
                </label>
                <label>
                    Description:
                    <textarea ref={descriptionRef} className='input-form' name="description" rows="2" maxLength="200" placeholder="Describe your rank (optional)" />
                </label>
                <label>
                    Submission Due Date:  
                    <input ref={submissionDuedateRef} className='input-form' type="date" name="submissionDuedate" required />
                </label>
                <label>
                    Rank Due Date:  
                    <input ref={rankDuedateRef} className='input-form' type="date" name="rankDuedate" required />
                </label>
                <label>
                    Submission Limit:
                    <input ref={submissionLimitRef} className='input-form' type="number" name="submissionLimit" min="1" max="50" placeholder="2" />
                </label>
                <button type="submit" className="general-button">Create Game</button>
            </form>
            {createdGameCode && (
                <p className="created-game-code">
                    Game created successfully! Your game code is: {createdGameCode}
                </p>
            )}
        </div>
    );
}

export default CreateRankPopup;