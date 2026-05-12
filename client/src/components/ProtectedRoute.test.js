import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { UserContext } from '../contexts/UserContext';
import ProtectedRoute from './ProtectedRoute';

function renderWithAuth(user, route = '/dashboard') {
    return render(
        <UserContext.Provider value={{ user, setUser: jest.fn(), logout: jest.fn() }}>
            <MemoryRouter initialEntries={[route]}>
                <Routes>
                    <Route path="/" element={<div>Login Page</div>} />
                    <Route path="/dashboard" element={
                        <ProtectedRoute>
                            <div>Dashboard Content</div>
                        </ProtectedRoute>
                    } />
                </Routes>
            </MemoryRouter>
        </UserContext.Provider>
    );
}

describe('ProtectedRoute', () => {
    beforeEach(() => {
        localStorage.clear();
    });

    test('redirects to login when no user and no token', () => {
        renderWithAuth(null);
        expect(screen.getByText('Login Page')).toBeInTheDocument();
        expect(screen.queryByText('Dashboard Content')).not.toBeInTheDocument();
    });

    test('redirects to login when user exists but no token in storage', () => {
        renderWithAuth({ user_id: 1 }); // user in context but no localStorage token
        expect(screen.getByText('Login Page')).toBeInTheDocument();
    });

    test('renders children when user and token exist', () => {
        localStorage.setItem('authToken', 'valid-token');
        renderWithAuth({ user_id: 1 });
        expect(screen.getByText('Dashboard Content')).toBeInTheDocument();
    });
});
