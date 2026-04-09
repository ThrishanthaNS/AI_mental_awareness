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

const floatingEmojiItems = [
  { emoji: '😊', left: '8%', delay: '0s', duration: '11s', size: '1.3rem' },
  { emoji: '✨', left: '18%', delay: '2s', duration: '13s', size: '1.1rem' },
  { emoji: '🌈', left: '28%', delay: '1s', duration: '12s', size: '1.2rem' },
  { emoji: '💛', left: '41%', delay: '3s', duration: '14s', size: '1.25rem' },
  { emoji: '🦋', left: '54%', delay: '0.8s', duration: '12.5s', size: '1.15rem' },
  { emoji: '🌸', left: '66%', delay: '2.6s', duration: '13.5s', size: '1.2rem' },
  { emoji: '🎈', left: '76%', delay: '1.6s', duration: '12s', size: '1.3rem' },
  { emoji: '☀️', left: '88%', delay: '3.3s', duration: '14.2s', size: '1.2rem' },
];

function FloatingEmojis() {
  return (
    <div className="emoji-sky" aria-hidden="true">
      {floatingEmojiItems.map((item, index) => (
        <span
          key={`${item.emoji}-${index}`}
          className="floating-emoji"
          style={{
            left: item.left,
            animationDelay: item.delay,
            animationDuration: item.duration,
            fontSize: item.size,
          }}
        >
          {item.emoji}
        </span>
      ))}
    </div>
  );
}

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
        <FloatingEmojis />
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
