import React from 'react';
import MoodChart from '../components/MoodChart';
import { Link } from 'react-router-dom';

const Dashboard = () => {
  return (
    <div className="dashboard">
      <header>
        <h1>Mental Health Dashboard</h1>
        <nav>
          <Link to="/chat">Chat with AI</Link>
        </nav>
      </header>

      <main>
        <section className="mood-section">
          <h2>Your Mood Overview</h2>
          <MoodChart moodData={[]} />
        </section>

        <section className="recommendations-section">
          <h2>Personalized Recommendations</h2>
          <p>Recommendations will appear here based on your mood history.</p>
        </section>
      </main>
    </div>
  );
};

export default Dashboard;
