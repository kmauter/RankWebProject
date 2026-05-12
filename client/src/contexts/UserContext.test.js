import React, { useContext } from 'react';
import { render, screen, act } from '@testing-library/react';
import { UserContext, UserProvider } from './UserContext';

// Helper component to access context values
function TestConsumer() {
    const { user, logout } = useContext(UserContext);
    return (
        <div>
            <span data-testid="user">{user ? JSON.stringify(user) : 'null'}</span>
            <button onClick={logout}>Logout</button>
        </div>
    );
}

describe('UserContext', () => {
    beforeEach(() => {
        localStorage.clear();
    });

    test('loads user from valid stored token on mount', () => {
        // Create a token that expires far in the future (exp: 9999999999)
        const payload = btoa(JSON.stringify({ user_id: 42, exp: 9999999999 }));
        const fakeToken = `eyJhbGciOiJIUzI1NiJ9.${payload}.fake-signature`;
        localStorage.setItem('authToken', fakeToken);

        render(
            <UserProvider>
                <TestConsumer />
            </UserProvider>
        );

        const userText = screen.getByTestId('user').textContent;
        expect(userText).toContain('42');
    });

    test('does not set user when token is expired', () => {
        // Create a token that expired in the past (exp: 1000000000 = 2001)
        const payload = btoa(JSON.stringify({ user_id: 42, exp: 1000000000 }));
        const fakeToken = `eyJhbGciOiJIUzI1NiJ9.${payload}.fake-signature`;
        localStorage.setItem('authToken', fakeToken);

        render(
            <UserProvider>
                <TestConsumer />
            </UserProvider>
        );

        expect(screen.getByTestId('user').textContent).toBe('null');
        expect(localStorage.getItem('authToken')).toBeNull();
    });

    test('logout clears token and user', () => {
        const payload = btoa(JSON.stringify({ user_id: 42, exp: 9999999999 }));
        const fakeToken = `eyJhbGciOiJIUzI1NiJ9.${payload}.fake-signature`;
        localStorage.setItem('authToken', fakeToken);

        render(
            <UserProvider>
                <TestConsumer />
            </UserProvider>
        );

        // User should be set initially
        expect(screen.getByTestId('user').textContent).toContain('42');

        // Click logout
        act(() => {
            screen.getByRole('button', { name: /logout/i }).click();
        });

        expect(screen.getByTestId('user').textContent).toBe('null');
        expect(localStorage.getItem('authToken')).toBeNull();
    });

    test('no token means no user', () => {
        render(
            <UserProvider>
                <TestConsumer />
            </UserProvider>
        );

        expect(screen.getByTestId('user').textContent).toBe('null');
    });
});
