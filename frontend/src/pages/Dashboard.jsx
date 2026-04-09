import React, { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';

// Mock data for demo
const stressData = {
  currentScore: 78,
  previousScore: 76,
  riskLevel: 'high',
  trendData: [55, 62, 58, 71, 76, 74, 78],
  dayLabels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
  behaviors: {
    typingSpeed: { value: 'Slower', change: '↓ 12%' },
    screenTime: '9 hrs/day',
  },
  emotions: {
    face: 'Fatigue detected',
    voice: 'Low energy tone',
  },
  context: {
    role: 'Student',
    workload: 'High',
    age: 20,
  },
  riskFactors: [
    { label: 'Low sleep', value: '5 hrs', icon: '😴' },
    { label: 'High screen time', value: '9 hrs/day', icon: '📱' },
    { label: 'Increased workload', value: '+40% this week', icon: '📊' },
  ],
  recommendations: [
    'Take a 30-min break within next hour',
    'Reduce screen exposure tonight',
    'Reschedule 1 task to next week',
  ],
  peakStressTime: '10:00 PM',
  interventionTime: '9:30 PM',
  burnoutRisk: 'HIGH',
  burnoutDays: 3,
};

const getRiskColor = (score) => {
  if (score < 40) return 'low';
  if (score < 60) return 'medium';
  return 'high';
};

const getRiskIcon = (risk) => {
  if (risk === 'low') return '●';
  if (risk === 'medium') return '◐';
  return '◉';
};

function TrendChart() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const context = canvas.getContext('2d');
    const dpr = window.devicePixelRatio || 1;
    const { width, height } = canvas.getBoundingClientRect();

    canvas.width = width * dpr;
    canvas.height = height * dpr;
    context.scale(dpr, dpr);
    context.clearRect(0, 0, width, height);

    const data = stressData.trendData;
    const padding = 60;
    const innerWidth = width - padding * 2;
    const innerHeight = height - padding * 2 - 30;
    const min = Math.min(...data);
    const max = Math.max(...data);
    const range = Math.max(max - min, 1);

    // Grid lines
    context.strokeStyle = 'rgba(107, 114, 128, 0.1)';
    context.lineWidth = 1;
    for (let i = 0; i <= 3; i++) {
      const y = padding + (innerHeight / 3) * i;
      context.beginPath();
      context.moveTo(padding, y);
      context.lineTo(width - padding, y);
      context.stroke();
    }

    // Line chart
    const points = data.map((value, index) => ({
      x: padding + (innerWidth / (data.length - 1)) * index,
      y: padding + innerHeight - ((value - min) / range) * innerHeight,
      value: value,
    }));

    const gradient = context.createLinearGradient(0, padding, 0, height - padding);
    gradient.addColorStop(0, 'rgba(239, 68, 68, 0.8)');
    gradient.addColorStop(1, 'rgba(245, 158, 11, 0.8)');

    context.strokeStyle = gradient;
    context.lineWidth = 3;
    context.lineJoin = 'round';
    context.lineCap = 'round';
    context.beginPath();
    points.forEach((point, index) => {
      if (index === 0) context.moveTo(point.x, point.y);
      else context.lineTo(point.x, point.y);
    });
    context.stroke();

    // Fill area
    const areaGradient = context.createLinearGradient(0, padding, 0, height - padding);
    areaGradient.addColorStop(0, 'rgba(239, 68, 68, 0.2)');
    areaGradient.addColorStop(1, 'rgba(239, 68, 68, 0.02)');
    context.fillStyle = areaGradient;
    context.lineTo(points[points.length - 1].x, height - padding - 30);
    context.lineTo(points[0].x, height - padding - 30);
    context.closePath();
    context.fill();

    // Data points with values
    points.forEach((point, index) => {
      // Point circle
      context.beginPath();
      context.arc(point.x, point.y, 5, 0, Math.PI * 2);
      context.fillStyle = index === points.length - 1 ? '#ef4444' : '#ffffff';
      context.fill();
      context.strokeStyle = gradient;
      context.lineWidth = 2;
      context.stroke();

      // Value label
      context.fillStyle = '#e4e9f1';
      context.font = 'bold 12px Inter, system-ui';
      context.textAlign = 'center';
      context.fillText(point.value.toString(), point.x, point.y - 15);
    });

    // Day labels
    points.forEach((point, index) => {
      context.fillStyle = 'rgba(168, 179, 193, 0.7)';
      context.font = '12px Inter, system-ui';
      context.textAlign = 'center';
      const dayLabel = stressData.dayLabels[index];
      context.fillText(dayLabel, point.x, height - padding + 15);
    });
  }, []);

  return <canvas ref={canvasRef} className="trend-chart" aria-label="7-day stress trend chart" />;
}

function Dashboard() {
  const riskClass = getRiskColor(stressData.currentScore);
  const [completedRecs, setCompletedRecs] = useState([]);
  const [expandedSignals, setExpandedSignals] = useState({
    behavioral: false,
    emotional: false,
    context: false,
  });

  const toggleSignal = (type) => {
    setExpandedSignals((prev) => ({
      ...prev,
      [type]: !prev[type],
    }));
  };

  const toggleRecommendation = (index) => {
    setCompletedRecs((prev) =>
      prev.includes(index) ? prev.filter((i) => i !== index) : [...prev, index]
    );
  };

  const dismissRecommendation = (index, e) => {
    e.stopPropagation();
    setCompletedRecs((prev) => [...prev, index]);
  };

  const visibleRecs = stressData.recommendations.filter(
    (_, index) => !completedRecs.includes(index)
  );

  const scoreChange = stressData.currentScore - stressData.previousScore;
  const changeDirection = scoreChange > 0 ? '↑' : scoreChange < 0 ? '↓' : '→';
  const changeColor = scoreChange > 0 ? '#ef4444' : scoreChange < 0 ? '#10b981' : '#a8b3c1';

  return (
    <div className="dashboard-page">
      {/* Navbar */}
      <nav className="navbar">
        <div className="brand-block">
          <div className="brand-mark">M</div>
          <h1 className="brand-copy">MindGuard</h1>
        </div>
        <div className="navbar-right">
          <span className="role-badge">👤 {stressData.context.role}</span>
          <div className="user-icon">U</div>
        </div>
      </nav>

      {/* Main content */}
      <main className="dashboard-shell">
        {/* Hero Card */}
        <div className="hero-card">
          <div className="stress-score">
            <div className={`stress-number ${riskClass}`}>{stressData.currentScore}</div>
            <div className="stress-label">/ 100 Stress Score</div>
            <div style={{ fontSize: '0.85rem', marginTop: '8px', color: changeColor }}>
              {changeDirection} {Math.abs(scoreChange)} vs yesterday
            </div>
          </div>
          <div className="stress-meta">
            <div className={`risk-badge ${riskClass}`}>
              {getRiskIcon(riskClass)} {riskClass.toUpperCase()}
            </div>
            <div className="risk-description">Stress level elevated</div>
            <div
              style={{
                fontSize: '0.8rem',
                color: 'var(--ink-soft)',
                marginTop: '8px',
                paddingTop: '8px',
                borderTop: '1px solid rgba(148, 163, 184, 0.1)',
              }}
            >
              ⚡ Immediate attention needed
            </div>
          </div>
        </div>

        {/* Trend Section */}
        <div className="card">
          <h2 className="card-title">📊 Stress Trend (Last 7 Days)</h2>
          <TrendChart />
          <div className="trend-meta">
            <span>Mon → Sun</span>
            <span className="trend-increase">↑ 35% increase this week</span>
          </div>
          <div className="trend-comparison">
            Peak on Sunday (78 pts) • Lowest on Monday (55 pts) • Avg this week: 67 pts
          </div>
        </div>

        {/* Multi-Modal Signals */}
        <div className="card" id="patterns">
          <h2 className="card-title">🧩 Multi-Modal Signals</h2>
          <div className="signals-grid">
            {/* Behavioral */}
            <div className={`signal-card behavioral ${expandedSignals.behavioral ? 'expanded' : ''}`}>
              <button
                className="signal-title expandable-toggle"
                onClick={() => toggleSignal('behavioral')}
                aria-expanded={expandedSignals.behavioral}
              >
                <span>🟦 Behavioral</span>
                <span className={`expandable-icon ${expandedSignals.behavioral ? 'open' : ''}`}>▼</span>
              </button>
              {expandedSignals.behavioral && (
                <div className="signal-details">
                  <div className="signal-item">
                    <span className="signal-label">Typing Speed</span>
                    <span className="signal-value">{stressData.behaviors.typingSpeed.change}</span>
                  </div>
                  <div className="signal-item">
                    <span className="signal-label">Screen Time</span>
                    <span className="signal-value">{stressData.behaviors.screenTime}</span>
                  </div>
                </div>
              )}
              {!expandedSignals.behavioral && (
                <div className="signal-item">
                  <span className="signal-label">Activity</span>
                  <span className="signal-value">2 signals detected</span>
                </div>
              )}
            </div>

            {/* Emotional */}
            <div className={`signal-card emotional ${expandedSignals.emotional ? 'expanded' : ''}`}>
              <button
                className="signal-title expandable-toggle"
                onClick={() => toggleSignal('emotional')}
                aria-expanded={expandedSignals.emotional}
              >
                <span>🟪 Emotional</span>
                <span className={`expandable-icon ${expandedSignals.emotional ? 'open' : ''}`}>▼</span>
              </button>
              {expandedSignals.emotional && (
                <div className="signal-details">
                  <div className="signal-item">
                    <span className="signal-label">Face</span>
                    <span className="signal-value">{stressData.emotions.face}</span>
                  </div>
                  <div className="signal-item">
                    <span className="signal-label">Voice</span>
                    <span className="signal-value">{stressData.emotions.voice}</span>
                  </div>
                </div>
              )}
              {!expandedSignals.emotional && (
                <div className="signal-item">
                  <span className="signal-label">Status</span>
                  <span className="signal-value">2 indicators</span>
                </div>
              )}
            </div>

            {/* Contextual */}
            <div className={`signal-card context ${expandedSignals.context ? 'expanded' : ''}`}>
              <button
                className="signal-title expandable-toggle"
                onClick={() => toggleSignal('context')}
                aria-expanded={expandedSignals.context}
              >
                <span>🟩 Contextual</span>
                <span className={`expandable-icon ${expandedSignals.context ? 'open' : ''}`}>▼</span>
              </button>
              {expandedSignals.context && (
                <div className="signal-details">
                  <div className="signal-item">
                    <span className="signal-label">Role</span>
                    <span className="signal-value">{stressData.context.role}</span>
                  </div>
                  <div className="signal-item">
                    <span className="signal-label">Workload</span>
                    <span className="signal-value">{stressData.context.workload}</span>
                  </div>
                  <div className="signal-item">
                    <span className="signal-label">Age</span>
                    <span className="signal-value">{stressData.context.age}</span>
                  </div>
                </div>
              )}
              {!expandedSignals.context && (
                <div className="signal-item">
                  <span className="signal-label">Context</span>
                  <span className="signal-value">3 factors</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Risk & Recommendations (2-column) */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px' }}>
          {/* Risk Factors */}
          <div className="card">
            <h2 className="card-title">⚠️ Why are you stressed?</h2>
            <div className="risk-factors">
              {stressData.riskFactors.map((factor) => (
                <div key={factor.label} className="risk-item">
                  <span className="risk-indicator">{factor.icon}</span>
                  <div className="risk-text">
                    <strong>{factor.label}</strong>
                    <div>{factor.value}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Recommendations */}
          <div className="card">
            <h2 className="card-title">⚡ Recommended Actions</h2>
            <div className="recommendations">
              {visibleRecs.map((rec, index) => (
                <div
                  key={index}
                  className={`recommendation-item ${completedRecs.includes(index) ? 'done' : ''}`}
                  onClick={() => toggleRecommendation(index)}
                  role="button"
                  tabIndex="0"
                  aria-pressed={completedRecs.includes(index)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') toggleRecommendation(index);
                  }}
                >
                  <span className="recommendation-icon">✓</span>
                  <div className="recommendation-text">{rec}</div>
                  <button
                    className="recommendation-close"
                    onClick={(e) => dismissRecommendation(index, e)}
                    aria-label="Dismiss recommendation"
                    title="Dismiss"
                  >
                    ✕
                  </button>
                </div>
              ))}
              {visibleRecs.length === 0 && (
                <div style={{ padding: '12px', color: 'var(--ink-soft)', fontSize: '0.9rem' }}>
                  ✨ All recommendations marked! Great job!
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Intervention Timing */}
        <div className="intervention-card">
          <div className="intervention-title">⏱️ Intervention Timing</div>
          <div>
            <div className="intervention-time">{stressData.interventionTime}</div>
            <div className="intervention-meta">
              Peak stress expected at {stressData.peakStressTime} | Recommended action window: 15 min before
            </div>
          </div>
        </div>

        {/* Burnout Prediction */}
        <div className="burnout-card">
          <div className="burnout-status">
            <div className="burnout-indicator" />
            <div className="burnout-risk-text">Burnout Risk: 🔴 {stressData.burnoutRisk}</div>
          </div>
          <div className="burnout-description">
            Burnout likely in{' '}
            <strong>
              {stressData.burnoutDays} day{stressData.burnoutDays !== 1 ? 's' : ''}
            </strong>{' '}
            if pattern continues. Consider intervention or lifestyle changes.
          </div>
        </div>

        {/* CTA */}
        <div className="card" style={{ textAlign: 'center', padding: '32px' }}>
          <h2 className="card-title">Get Personal Support</h2>
          <p style={{ margin: '8px 0 16px', color: 'var(--ink-soft)' }}>
            Chat with our AI wellness assistant for immediate guidance
          </p>
          <Link to="/chat" style={{ display: 'inline-block' }}>
            <button className="cta-button">
              Open Chat
            </button>
          </Link>
        </div>
      </main>
    </div>
  );
}

export default Dashboard;
