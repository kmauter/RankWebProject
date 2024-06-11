import React from 'react';

import { Link } from 'react-router-dom';

function HomePage() {
    return (
        <div className="bg-green-500 text-white p-4">
            <h1>Home Page</h1>
            <p>This is the home page</p>
                <nav>
                    <ul>
                        <li><Link to="/login" className="btn btn-primary">Login</Link></li>
                        <li><Link to="/register" className="btn btn-primary">Register</Link></li>
                    </ul>
                </nav>
        </div>
    );
}

export default HomePage;