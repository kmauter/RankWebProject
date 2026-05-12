import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { UserProvider } from '../contexts/UserContext';
import LoginForm from './LoginForm';
import axios from 'axios';

// Mock axios
jest.mock('axios');

// Mock useNavigate
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
    ...jest.requireActual('react-router-dom'),
    useNavigate: () => mockNavigate,
}));

function renderLoginForm() {
    return render(
        <UserProvider>
            <MemoryRouter>
                <LoginForm />
            </MemoryRouter>
        </UserProvider>
    );
}

describe('LoginForm', () => {
    beforeEach(() => {
        jest.clearAllMocks();
        localStorage.clear();
    });

    test('renders username and password fields', () => {
        renderLoginForm();
        expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    });

    test('renders login button', () => {
        renderLoginForm();
        expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
    });

    test('successful login stores token and navigates to dashboard', async () => {
        const fakeToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjk5OTk5OTk5OTl9.fake';
        axios.post.mockResolvedValueOnce({
            data: { token: fakeToken, message: 'Login successful!' }
        });

        renderLoginForm();

        fireEvent.change(screen.getByLabelText(/username/i), { target: { value: 'testuser' } });
        fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'password123' } });
        fireEvent.click(screen.getByRole('button', { name: /login/i }));

        await waitFor(() => {
            expect(axios.post).toHaveBeenCalledWith('/api/login', {
                username: 'testuser',
                password: 'password123',
            });
        });

        await waitFor(() => {
            expect(localStorage.getItem('authToken')).toBe(fakeToken);
        });

        await waitFor(() => {
            expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
        });
    });

    test('failed login shows error message', async () => {
        axios.post.mockRejectedValueOnce({
            response: { status: 401, data: { message: 'Invalid username or password' } }
        });

        renderLoginForm();

        fireEvent.change(screen.getByLabelText(/username/i), { target: { value: 'baduser' } });
        fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'wrongpass' } });
        fireEvent.click(screen.getByRole('button', { name: /login/i }));

        await waitFor(() => {
            expect(screen.getByText(/invalid username or password/i)).toBeInTheDocument();
        });
    });

    test('has link to register page', () => {
        renderLoginForm();
        const registerLink = screen.getByRole('link', { name: /register/i });
        expect(registerLink).toBeInTheDocument();
        expect(registerLink).toHaveAttribute('href', '/register');
    });
});
