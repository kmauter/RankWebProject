import React, { createContext, useState, useEffect } from 'react';
import { jwtDecode } from 'jwt-decode';

export const UserContext = createContext();

export const UserProvider = ({ children }) => {
    const [user, setUser] = useState(null);

    useEffect(() => {
        const token = localStorage.getItem('authToken');
        if (token) {
            const decodedUser = jwtDecode(token);
            setUser(decodedUser); // Set the user from the decoded token
        }
    }, []);

    const logout = () => {
        localStorage.removeItem('authToken'); // Remove the token
        setUser(null); // Clear the user state
    };

    return (
        <UserContext.Provider value={{ user, setUser, logout }}>
            {children}
        </UserContext.Provider>
    );
};