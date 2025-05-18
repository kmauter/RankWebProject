import React from "react";

function CreateRankPopup({ onClose, onCreate, createdGameCode}) {
    return (
        <div className="main-popup">
            <h1
                className='close-button'
                onClick={() => {
                    onClose();
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
                    onCreate(theme, submissionDuedate, rankDuedate);
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
    );
}

export default CreateRankPopup;