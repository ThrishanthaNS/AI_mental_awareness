import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Chat from './pages/Chat';
import './App.css';

const navItems = [
  { label: 'Dashboard', to: '/' },
  { label: 'Chat', to: '/chat' },
  { label: 'Insights', to: '/#patterns' },
];

function BottomNav() {
  const location = useLocation();

  return (
    <nav className="bottom-nav" aria-label="Mobile navigation">
      {navItems.map((item) => {
        const isActive =
          item.to === '/'
            ? location.pathname === '/' && !location.hash
            : item.to === '/chat'
              ? location.pathname === '/chat'
              : location.hash === '#patterns';

        return (
          <Link key={item.label} to={item.to} className={`nav-button ${isActive ? 'active' : ''}`}>
            {item.label}
          </Link>
        );
      })}
    </nav>
  );
}

function App() {
  return (
    <Router>
      <div className="app-shell">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/chat" element={<Chat />} />
        </Routes>
        <BottomNav />
      </div>
    </Router>
  );
}

export default App;
