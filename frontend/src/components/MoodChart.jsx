import React from 'react';

const MoodChart = ({ moodData }) => {
  return (
    <div className="mood-chart">
      <h3>Mood Trends</h3>
      <div className="chart-placeholder">
        {/* Integrate with a charting library like Chart.js or Recharts */}
        {moodData && moodData.length > 0 ? (
          <p>Chart visualization goes here</p>
        ) : (
          <p>No mood data available yet. Start logging your mood!</p>
        )}
      </div>
    </div>
  );
};

export default MoodChart;
