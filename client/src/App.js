import React from 'react';

import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';

import LoginForm from './components/LoginForm';
import RegisterForm from './components/RegisterForm';
import ForgotPassword from './components/ForgotPassword';
import HomePage from './components/HomePage';
import Dashboard from './components/Dashboard';
import ProtectedRoute from './components/ProtectedRoute';
import { routes } from './components/Routes';
import './styles/index.css';

function App() {
  return (
    <Router>
      <div>
        <Routes>
          <Route exact path={routes.home} element={<HomePage />}/>
          <Route path={routes.login} element={<LoginForm />}/>
          <Route path={routes.register} element={<RegisterForm />}/>
          <Route path={routes.forgotPassword} element={<ForgotPassword />}/>
          <Route path='/dashboard' element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }/>
        </Routes>
      </div>
    </Router>
  );
}

export default App;