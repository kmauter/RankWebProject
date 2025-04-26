import React from 'react';

import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';

import LoginForm from './components/LoginForm';
import RegisterForm from './components/RegisterForm';
import HomePage from './components/HomePage';
import Dashboard from './components/Dashboard';
import { routes } from './components/Routes';
import './styles/index.css';

function App() {
  return (
    <Router>
      <div>
        {/* Add Navigation here if needed */}
        <Routes>
          <Route exact path={routes.home} element={<HomePage />}/>
          <Route path={routes.login} element={<LoginForm />}/>
          <Route path={routes.register} element={<RegisterForm />}/>
          <Route path='/dashboard' element={<Dashboard />}/>
          {/* Add other routes as needed */}
        </Routes>
      </div>
    </Router>
  );
}

export default App;