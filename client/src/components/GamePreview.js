import React from 'react';
import '../styles/GamePreview.css';

const GamePreview = ({ title, status, dueDate, onClick }) => {
    const statusImage = () => {
        switch (status) {
            case 'submissions':
                return require('../assets/SubmitIcon.png');
            case 'rankings':
                return require('../assets/RankTimeIcon.png');
            case 'results':
                return require('../assets/ResultsIcon.png');
            default:
                return require('../assets/SubmitIcon.png');
        }
    };

    const dueDateFormatted = dueDate ? `Due ${dueDate}` : 'Completed';

    return (
        <div className="game-preview" onClick={onClick}>
            {/* Corner images */}
            <img 
                src={require('../assets/Corner1.png')} 
                alt="Header TLeft" 
                className="corner-image top-left"
            />
            <img 
                src={require('../assets/Corner8.png')} 
                alt="Header TRight" 
                className="corner-image top-right"
            />
            <img 
                src={require('../assets/Corner2.png')} 
                alt="Header BLeft" 
                className="corner-image bottom-left"
            />
            <img 
                src={require('../assets/Corner3.png')} 
                alt="Header BRight" 
                className="corner-image bottom-right"
            />
            {/* Game Status Icon */}
            <img 
                src={statusImage()} 
                alt={`${status} icon`} 
                className="game-status-icon"
            />
            {/* Game Theme */}
            <h2 className='game-title'>{title}</h2>
            <p className='due-date'>{dueDateFormatted}</p>
        </div>
    );
};

export default GamePreview;