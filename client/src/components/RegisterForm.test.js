import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { UserProvider } from '../contexts/UserContext';
import RegisterForm from './RegisterForm';
import axios from 'axios';

// Mock axios
jest.mock('axios');

// Mock useNavigate
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
    ...jest.requireActual('react-router-dom'),
    useNavigate: () => mockNavigate,
}));

function renderRegisterForm() {
    return render(
        <UserProvider>
            <MemoryRouter>
                <RegisterForm />
            </MemoryRouter>
        </UserProvider>
    );
}

describe('RegisterForm', () => {
    beforeEach(() => {
        jest.clearAllMocks();
    });

    test('renders all 4 fields', () => {
        renderRegisterForm();
        expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/^password$/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument();
    });

    test('renders register button', () => {
        renderRegisterForm();
        expect(screen.getByRole('button', { name: /register/i })).toBeInTheDocument();
    });

    test('successful register navigates to login', async () => {
        axios.post.mockResolvedValueOnce({
            data: { message: 'User registered successfully' }
        });

        renderRegisterForm();

        fireEvent.change(screen.getByLabelText(/username/i), { target: { value: 'newuser' } });
        fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'new@test.com' } });
        fireEvent.change(screen.getByLabelText(/^password$/i), { target: { value: 'password123' } });
        fireEvent.change(screen.getByLabelText(/confirm password/i), { target: { value: 'password123' } });
        fireEvent.click(screen.getByRole('button', { name: /register/i }));

        await waitFor(() => {
            expect(axios.post).toHaveBeenCalledWith('/api/register', {
                username: 'newuser',
                email: 'new@test.com',
                password: 'password123',
                password2: 'password123',
            });
        });

        await waitFor(() => {
            expect(mockNavigate).toHaveBeenCalledWith('/');
        });
    });

    test('has link to login page', () => {
        renderRegisterForm();
        const loginLink = screen.getByRole('link', { name: /login/i });
        expect(loginLink).toBeInTheDocument();
        expect(loginLink).toHaveAttribute('href', '/');
    });
});
