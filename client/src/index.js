import React from 'react';

import ReactDOM from 'react-dom/client';

import App from './App';
import reportWebVitals from './reportWebVitals';
import './styles/index.css';
import { UserProvider } from './contexts/UserContext';
import { installGlobal401Handler } from './utils/api';

// Intercept all fetch calls — redirect to login on 401
installGlobal401Handler();

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <UserProvider>
      <App />
    </UserProvider>
  </React.StrictMode>
);