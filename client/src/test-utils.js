import React from 'react';
import { render } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { UserProvider } from './contexts/UserContext';

/**
 * Custom render that wraps components with UserProvider and Router.
 * Use this instead of @testing-library/react's render for components
 * that need context or routing.
 */
export function renderWithProviders(ui, { route = '/', ...options } = {}) {
    return render(
        <UserProvider>
            <MemoryRouter initialEntries={[route]}>
                {ui}
            </MemoryRouter>
        </UserProvider>,
        options
    );
}

export * from '@testing-library/react';
export { renderWithProviders as render };
