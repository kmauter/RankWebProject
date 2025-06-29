import { render, screen } from '@testing-library/react';
import App from './App';
import { UserProvider } from './contexts/UserContext';

test('renders login form', () => {
  render(
    <UserProvider>
      <App />
    </UserProvider>
  );
  // Check for login form elements
  expect(screen.getByLabelText(/Username/i)).toBeInTheDocument();
  expect(screen.getByLabelText(/Password/i)).toBeInTheDocument();
  expect(screen.getByRole('button', { name: /Login/i })).toBeInTheDocument();
});
