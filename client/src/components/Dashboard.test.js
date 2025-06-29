import { render, screen } from '@testing-library/react';
import Dashboard from './Dashboard';
import React from 'react';
import { UserProvider } from '../contexts/UserContext';

describe('Dashboard', () => {
  it('renders without crashing and shows create/join buttons', () => {
    render(
      <UserProvider>
        <Dashboard />
      </UserProvider>
    );
    expect(screen.getByText(/Create a rank/i)).toBeInTheDocument();
    expect(screen.getByText(/Join a rank/i)).toBeInTheDocument();
  });
});
