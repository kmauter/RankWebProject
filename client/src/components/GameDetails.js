import React, { useState, useEffect } from "react";
import { DndContext, MouseSensor, TouchSensor, useSensor, useSensors } from '@dnd-kit/core';

import Draggable from './Draggable';
import Droppable from './Droppable';

function GameDetails({ 
    game, 
    songs, 
    userRanking = [],
    onBack, 
    currentUser, 
    onSongSubmit, 
    onNextPage,
    userSongs, 
    onDeleteSong,
    onSaveRanking
}) {
    const [songName, setSongName] = useState('');
    const [songArtist, setSongArtist] = useState('');
    const [songComment, setSongComment] = useState('');
    
    // --- Move these hooks to the top level, outside any conditionals ---
    // For rankings drag-and-drop
    const initialRanking = Array(songs.length).fill(null);
    const [ranking, setRanking] = useState(initialRanking);
    const [pool, setPool] = useState(songs.map(s => s.id));

    const mouseSensor = useSensor(MouseSensor, { activationConstraint: { distance: 5 } });
    const touchSensor = useSensor(TouchSensor, { activationConstraint: { delay: 150, tolerance: 5 } });
    const sensors = useSensors(mouseSensor, touchSensor);


    useEffect(() => {
        const slotCount = songs.length;
        const rankingArr = Array(slotCount).fill(null);

        console.log("Loaded User Ranking: ", userRanking);

        userRanking.forEach((id, idx) => {
            if (idx < slotCount) rankingArr[idx] = id;
        });

        setRanking(rankingArr);

        const poolArr = songs.map(s => s.id).filter(id => !rankingArr.includes(id));
        setPool(poolArr);
    }, [songs, userRanking]);

    // For comment expand/collapse
    const [expandedComments, setExpandedComments] = useState({});
    const toggleComment = (songId) => {
        setExpandedComments(prev => ({
            ...prev,
            [songId]: !prev[songId]
        }));
    };

    const isOwner = game.owner.id === currentUser.user_id;
    const status = game.status;
    const dueDate =
    game.status === 'submissions'
        ? game.submissionDueDate
        : game.rankDueDate;

    
    // function getSpotifyPlaylistId(url) {
    //     const match = url.match(/playlist\/([a-zA-Z0-9]+)(\?|$)/);
    //     return match ? match[1] : null;
    // }

    const spotifyPlaylistUrl = game.spotifyPlaylistUrl;
    // const spotifyEmbedUrl = spotifyPlaylistId 
    //     ? `https://open.spotify.com/embed/playlist/${spotifyPlaylistId}` 
    //     : null;
    
    // function getYoutubePlaylistId(url) {
    //     const match = url.match(/[?&]list=([a-zA-Z0-9_-]+)/);
    //     return match ? match[1] : null;
    // }

    const youtubePlaylistUrl = game.youtubePlaylistUrl
    // const youtubeEmbedUrl = youtubePlaylistId 
    //     ? `https://www.youtube.com/embed/videoseries?list=${youtubePlaylistId}` 
    //     : null;

    let content;
    const [showDescription, setShowDescription] = useState(false);
    if (status === 'submissions') {
        content = (
            <>
                <div className="game-title-row">
                    {game.description && (
                        <button
                            onClick={() => setShowDescription(v => !v)}
                            aria-label={showDescription ? 'Hide description' : 'Show description'}
                            className="comment-toggle-btn"
                        >
                            {showDescription ? '-' : '+'}
                        </button>
                    )}
                    <h2 style={{ margin: 0 }}>{game.title}</h2>
                    <span className='game-code'>{game.gameCode}</span>
                </div>
                <p className='popup-due-date'>Due {dueDate}</p>
                {showDescription && game.description && (
                    <div className="song-pool-item-comment">
                        {game.description}
                    </div>
                )}
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
            </>
        );
    } else if (status === 'rankings') {
        // Two-column drag-and-drop ranking UI
        function handleDragEnd(event) {
            const {active, over} = event;
            if (!over) return;
            // Dropping onto a ranking slot
            if (over.id.startsWith('slot-')) {
                const slotIdx = parseInt(over.id.replace('slot-', ''));
                setRanking(r => {
                    const newR = [...r];
                    const prevIdx = r.findIndex(id => id === active.id);
                    const destSong = newR[slotIdx];
                    // If dragging from pool
                    if (prevIdx === -1) {
                        newR[slotIdx] = active.id;
                    } else {
                        // Swapping between slots
                        newR[slotIdx] = active.id;
                        newR[prevIdx] = destSong;
                    }
                    return newR;
                });
                setPool(p => {
                    let newP = p.filter(id => id !== active.id);
                    const destSong = ranking[slotIdx];
                    const prevIdx = ranking.findIndex(id => id === active.id);
                    // If dragging from pool, and slot was occupied, put previous song in pool
                    if (prevIdx === -1 && destSong && !newP.includes(destSong)) {
                        newP = [...newP, destSong];
                    }
                    // If swapping between slots, no pool update needed
                    return newP;
                });
            }
            // Dropping from ranking slot back to pool
            if (over.id === 'pool') {
                const slotIdx = ranking.findIndex(id => id === active.id);
                if (slotIdx !== -1) {
                    setRanking(r => {
                        const newR = [...r];
                        newR[slotIdx] = null;
                        return newR;
                    });
                    setPool(p => [...p, active.id]);
                }
            }
        }

        content = (
            <>
                <div className="game-title-row">
                    <h2>{game.title}</h2>
                    <span className='game-code'>{game.gameCode}</span>
                </div>
                <p className='popup-due-date'>Due {dueDate}</p>
                <DndContext sensors={sensors} onDragEnd={handleDragEnd}>
                    <div className="rank-drag-area">
                        <div className="playlist-links">
                            <h2>Playlist Links</h2>
                            {spotifyPlaylistUrl && (
                                <a
                                    href={spotifyPlaylistUrl}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="playlist-btn"
                                >
                                    Open Spotify Playlist
                                    <img src={require('../assets/Corner1.png')} alt="Top Left Corner" className="corner-image top-left" />
                                    <img src={require('../assets/Corner8.png')} alt="Top Right Corner" className="corner-image top-right" />
                                    <img src={require('../assets/Corner2.png')} alt="Bottom Left Corner" className="corner-image bottom-left" />
                                    <img src={require('../assets/Corner7.png')} alt="Bottom Right Corner" className="corner-image bottom-right" />
                                </a>
                            )}
                            {youtubePlaylistUrl && (
                                <a
                                    href={youtubePlaylistUrl}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="playlist-btn"
                                >
                                    Open YouTube Playlist
                                    <img src={require('../assets/Corner1.png')} alt="Top Left Corner" className="corner-image top-left" />
                                    <img src={require('../assets/Corner8.png')} alt="Top Right Corner" className="corner-image top-right" />
                                    <img src={require('../assets/Corner2.png')} alt="Bottom Left Corner" className="corner-image bottom-left" />
                                    <img src={require('../assets/Corner7.png')} alt="Bottom Right Corner" className="corner-image bottom-right" />
                                </a>
                            )}
                        </div>
                        {/* Pool column */}
                        <Droppable id="pool">
                            <h2>Song Pool</h2>
                            <div className="song-pool-main">
                                {/*Corners*/}
                                <img src={require('../assets/Corner5.png')} alt="Bottom Left Corner" className="corner-image bottom-left" />
                                <img src={require('../assets/Corner7.png')} alt="Bottom Right Corner" className="corner-image bottom-right" />
                                <img src={require('../assets/Corner4.png')} alt="Top Right Corner" className="corner-image top-right" />
                                <img src={require('../assets/Corner6.png')} alt="Top Left Corner" className="corner-image top-left" />
                                {pool.length === 0 ? <div>No songs left</div> :
                                    pool.map(id => {
                                        const song = songs.find(s => s.id === id);
                                        if (!song) return null;
                                        const hasComment = song.comment && song.comment.trim() !== '';
                                        return (
                                            <div key={id} className='song-pool-item'>
                                                <div className='song-pool-item-content'>
                                                    {hasComment && (
                                                        <button
                                                            onClick={() => toggleComment(id)}
                                                            className="comment-toggle-btn"
                                                            aria-label={expandedComments[id] ? 'Hide comment' : 'Show comment'}
                                                        >
                                                            {expandedComments[id] ? '-' : '+'}
                                                        </button>
                                                    )}
                                                    <Draggable id={id}>
                                                        {song.song_name || song.title} - {song.artist}
                                                    </Draggable>
                                                </div>
                                                {hasComment && expandedComments[id] && (
                                                    <div className="song-pool-item-comment">
                                                        {song.comment}
                                                    </div>
                                                )}
                                            </div>
                                        );
                                    })
                                }
                            </div>
                        </Droppable>
                        {/* Ranking column */}
                        <div className="rank-area-outer">
                            <h2>Your Ranking</h2>
                            <div className="rank-area">
                                <img src={require('../assets/Corner1.png')} alt="Top Left Corner" className="corner-image top-left" />
                                <img src={require('../assets/Corner8.png')} alt="Top Right Corner" className="corner-image top-right" />
                                <img src={require('../assets/Corner2.png')} alt="Bottom Left Corner" className="corner-image bottom-left" />
                                <img src={require('../assets/Corner7.png')} alt="Bottom Right Corner" className="corner-image bottom-right" />
                                {ranking.map((id, idx) => (
                                    <Droppable key={idx} id={`slot-${idx}`}>
                                        <div className={
                                            "rank-area-item " + 
                                            (id ? "rank-area-item--filled" : "rank-area-item--empty")
                                            }
                                        >
                                            {id ? (
                                                (() => {
                                                    const song = songs.find(s => s.id === id);
                                                    if (!song) return <span style={{color:'#f00'}}>Unknown song</span>;
                                                    const hasComment = song.comment && song.comment.trim() !== '';
                                                    return (
                                                        <>
                                                        <div className="rank-area-item-content">
                                                            <strong className="rank-area-number">{idx + 1}.</strong>
                                                            {hasComment && (
                                                                <button
                                                                    onClick={() => toggleComment(id)}
                                                                    className="comment-toggle-btn"
                                                                    aria-label={expandedComments[id] ? 'Hide comment' : 'Show comment'}
                                                                >
                                                                    {expandedComments[id] ? '-' : '+'}
                                                                </button>
                                                            )}
                                                            <Draggable id={id}>
                                                                {song.song_name || song.title} - {song.artist}
                                                            </Draggable>
                                                        </div>
                                                        {/* Show comment if expanded */}
                                                        {hasComment && expandedComments[id] && (
                                                            <div className="rank-area-item-comment">
                                                                {song.comment}
                                                            </div>
                                                        )}
                                                        </>
                                                    );
                                                })()
                                            ) : (
                                                <div className="rank-area-item-content">
                                                    <strong className="rank-area-number">{idx + 1}.</strong>
                                                    <span>Drop song here</span>
                                                </div>
                                            )}
                                        </div>
                                    </Droppable>
                                ))}
                            </div>
                            <button
                                className="save-ranking-btn"
                                onClick={() => {
                                    console.log("Current Ranking: ", ranking);
                                    onSaveRanking(ranking);
                                }}
                            >
                                Save Ranking
                                <img src={require('../assets/Corner1.png')} alt="Top Left Corner" className="corner-image top-left" />
                                <img src={require('../assets/Corner8.png')} alt="Top Right Corner" className="corner-image top-right" />
                                <img src={require('../assets/Corner2.png')} alt="Bottom Left Corner" className="corner-image bottom-left" />
                                <img src={require('../assets/Corner7.png')} alt="Bottom Right Corner" className="corner-image bottom-right" />
                            </button>
                        </div>
                    </div>
                </DndContext>
                {isOwner && (
                    <button onClick={onNextPage} className="owner-next-button">{'>>'}</button>
                )}
            </>
        );
    } else if (status === 'results') {
        const sortedSongs = [...songs]
            .sort((a, b) => (a.finalRank || 999) - (b.finalRank || 999))
            .reverse();

        content = (
            <>
                <div className="game-title-row">
                    <h2>{game.title}</h2>
                    <span className='game-code'>{game.gameCode}</span>
                </div>
                <p className='popup-due-date'>Finished {dueDate}</p>
                <table className="results-table">
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Song</th>
                            <th>Artist</th>
                            <th>Submitted By</th>
                            <th>Avg</th>
                            <th>Range</th>
                            <th>Controversy</th>
                            {/* Add more columns as needed, e.g. Score, Avg Rank */}
                        </tr>
                    </thead>
                    <tbody>
                        {sortedSongs.map((song, idx) => (
                            <tr key={song.id}>
                                <td data-label="Rank">{song.finalRank || idx + 1}</td>
                                <td data-label="Song">{song.song_name || song.title}</td>
                                <td data-label="Artist">{song.artist}</td>
                                <td data-label="Submitted By">{song.user?.username || 'Unknown'}</td>
                                <td data-label="Avg">
                                    {song.avg_rank != null
                                    ? Number.isInteger(Number(song.avg_rank))
                                        ? Number(song.avg_rank)
                                        : Number(song.avg_rank).toFixed(2)
                                    : '-'}
                                </td>
                                <td data-label="Range">{song.rank_range != null ? song.rank_range : '-'}</td>
                                <td data-label="Controversy">
                                    {song.controversy != null
                                    ? Number.isInteger(Number(song.controversy))
                                        ? Number(song.controversy)
                                        : Number(song.controversy).toFixed(2)
                                    : '-'}
                                </td>
                                {/* Add more cells as needed */}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </>
        );
    }
    return (
        <div className="game-details">
            <button onClick={onBack} className="close-button-details">X</button>
            {content}
        </div>
    );
}

export default GameDetails;