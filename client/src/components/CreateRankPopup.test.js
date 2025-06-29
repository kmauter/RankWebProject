import { render, screen, fireEvent } from '@testing-library/react';
import CreateRankPopup from './CreateRankPopup';
import React from 'react';

describe('CreateRankPopup', () => {
  it('renders form and submits with values', () => {
    const onCreate = jest.fn();
    render(
      <CreateRankPopup onClose={() => {}} onCreate={onCreate} createdGameCode={null} />
    );
    fireEvent.change(screen.getByLabelText(/Theme/i), { target: { value: 'Test Theme' } });
    fireEvent.change(screen.getByLabelText(/Submission Due Date/i), { target: { value: '2025-07-01' } });
    fireEvent.change(screen.getByLabelText(/Rank Due Date/i), { target: { value: '2025-07-10' } });
    fireEvent.click(screen.getByRole('button', { name: /Create Game/i }));
    expect(onCreate).toHaveBeenCalledWith('Test Theme', '2025-07-01', '2025-07-10');
  });

  it('renders close button', () => {
    const onClose = jest.fn();
    render(
      <CreateRankPopup onClose={onClose} onCreate={() => {}} createdGameCode={null} />
    );
    fireEvent.click(screen.getByRole('button', { name: /X/i }));
    expect(onClose).toHaveBeenCalled();
  });

  it('shows created game code if present', () => {
    render(
      <CreateRankPopup onClose={() => {}} onCreate={() => {}} createdGameCode="ABC123" />
    );
    expect(screen.getByText(/Game created successfully/i)).toBeInTheDocument();
    expect(screen.getByText(/ABC123/)).toBeInTheDocument();
  });
});
