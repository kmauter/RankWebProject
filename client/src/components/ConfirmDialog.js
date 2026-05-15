import React from 'react';
import '../styles/index.css';

function ConfirmDialog({ message, onConfirm, onCancel }) {
    return (
        <div className="confirm-overlay" onClick={onCancel}>
            <div className="confirm-dialog" onClick={(e) => e.stopPropagation()}>
                <p className="confirm-message">{message}</p>
                <div className="confirm-buttons">
                    <button className="confirm-btn cancel" onClick={onCancel}>Cancel</button>
                    <button className="confirm-btn confirm" onClick={onConfirm}>Confirm</button>
                </div>
            </div>
        </div>
    );
}

export default ConfirmDialog;
