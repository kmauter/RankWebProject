import React, { useContext } from 'react';
import { Navigate } from 'react-router-dom';
import { UserContext } from '../contexts/UserContext';

/**
 * Wraps a route that requires authentication.
 * Redirects to login if no valid user/token exists.
 */
function ProtectedRoute({ children }) {
    const { user } = useContext(UserContext);
    const token = localStorage.getItem('authToken');

    if (!user || !token) {
        return <Navigate to="/" replace />;
    }

    return children;
}

export default ProtectedRoute;
