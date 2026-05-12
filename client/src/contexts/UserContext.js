import React, { createContext, useState, useEffect, useCallback } from 'react';
import { jwtDecode } from 'jwt-decode';

export const UserContext = createContext();

/**
 * Check if a JWT token is expired.
 * Returns true if expired or invalid, false if still valid.
 */
function isTokenExpired(token) {
    try {
        const decoded = jwtDecode(token);
        if (!decoded.exp) return true;
        // exp is in seconds, Date.now() is in milliseconds
        return decoded.exp * 1000 < Date.now();
    } catch {
        return true;
    }
}

export const UserProvider = ({ children }) => {
    const [user, setUser] = useState(null);

    useEffect(() => {
        const token = localStorage.getItem('authToken');
        if (token) {
            if (isTokenExpired(token)) {
                // Token is expired — clear it and don't set user
                localStorage.removeItem('authToken');
                setUser(null);
            } else {
                const decodedUser = jwtDecode(token);
                setUser(decodedUser);
            }
        }
    }, []);

    const logout = useCallback(() => {
        localStorage.removeItem('authToken');
        setUser(null);
    }, []);

    return (
        <UserContext.Provider value={{ user, setUser, logout, isTokenExpired }}>
            {children}
        </UserContext.Provider>
    );
};
