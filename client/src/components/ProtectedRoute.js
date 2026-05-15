import React, { useContext } from 'react';
import { Navigate } from 'react-router-dom';
import { UserContext } from '../contexts/UserContext';
import { jwtDecode } from 'jwt-decode';

/**
 * Wraps a route that requires authentication.
 * Checks token directly from localStorage to avoid race condition
 * with UserContext's async useEffect on page refresh.
 */
function ProtectedRoute({ children }) {
    const { user } = useContext(UserContext);
    const token = localStorage.getItem('authToken');

    // If there's no token at all, redirect immediately
    if (!token) {
        return <Navigate to="/" replace />;
    }

    // If token exists, verify it's not expired
    try {
        const decoded = jwtDecode(token);
        if (decoded.exp * 1000 < Date.now()) {
            localStorage.removeItem('authToken');
            return <Navigate to="/" replace />;
        }
    } catch {
        localStorage.removeItem('authToken');
        return <Navigate to="/" replace />;
    }

    // Token is valid — render the protected content
    // (user context will catch up on the next render cycle)
    return children;
}

export default ProtectedRoute;
