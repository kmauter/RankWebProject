import { render, screen } from '@testing-library/react';
import GameDetails from './GameDetails';
import React from 'react';

describe('GameDetails', () => {
  const baseProps = {
    game: {
      title: 'Test Game',
      gameCode: 'ABC123',
      status: 'submissions',
      owner: { id: 1, username: 'owner' },
      submissionDueDate: '2025-07-01',
      rankDueDate: '2025-07-10',
      description: 'A test game',
    },
    songs: [],
    userRanking: [],
    onBack: jest.fn(),
    currentUser: { user_id: 1 },
    onSongSubmit: jest.fn(),
    onNextPage: jest.fn(),
    userSongs: [],
    onDeleteSong: jest.fn(),
    onSaveRanking: jest.fn(),
  };

  it('renders game title and due date', () => {
    render(<GameDetails {...baseProps} />);
    expect(screen.getByText(/Test Game/i)).toBeInTheDocument();
    expect(screen.getByText(/Due 2025-07-01/i)).toBeInTheDocument();
  });
});
