import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Link } from 'react-router-dom';

const moodOptions = [
  'Calm',
  'Focused',
  'Gentle',
  'Wavy',
  'Stressed',
];

const stats = [
  { icon: '◎', value: '12', label: 'Consistency streak' },
  { icon: '✦', value: '34', label: 'Reflections count' },
  { icon: '◌', value: '18', label: 'Insights gained' },
];

const weeklyPatterns = [
  { day: 'Mon', emotion: 'Stressed', className: 'emotion-stressed' },
  { day: 'Tue', emotion: 'Calm', className: 'emotion-calm' },
  { day: 'Wed', emotion: 'Neutral', className: 'emotion-neutral' },
  { day: 'Thu', emotion: 'Positive', className: 'emotion-positive' },
  { day: 'Fri', emotion: 'Calm', className: 'emotion-calm' },
  { day: 'Sat', emotion: 'Positive', className: 'emotion-positive' },
  { day: 'Sun', emotion: 'Neutral', className: 'emotion-neutral' },
];

const trendSeries = [
  { label: 'Mon', value: 32 },
  { label: 'Tue', value: 44 },
  { label: 'Wed', value: 39 },
  { label: 'Thu', value: 57 },
  { label: 'Fri', value: 64 },
  { label: 'Sat', value: 70 },
  { label: 'Sun', value: 63 },
  { label: 'Mon', value: 72 },
  { label: 'Tue', value: 80 },
  { label: 'Wed', value: 76 },
  { label: 'Thu', value: 84 },
  { label: 'Fri', value: 88 },
];

const palette = {
  positive: [
    [167, 243, 208],
    [125, 211, 252],
    [191, 219, 254],
  ],
  neutral: [
    [196, 181, 253],
    [167, 139, 250],
    [219, 234, 254],
  ],
  stress: [
    [251, 207, 232],
    [253, 186, 116],
    [252, 231, 243],
  ],
};

const toRgba = ([red, green, blue], alpha = 1) => `rgba(${red}, ${green}, ${blue}, ${alpha})`;

function MoodTrendChart() {
  const canvasRef = useRef(null);
  const [hoveredIndex, setHoveredIndex] = useState(0);

  const drawChart = () => {
    const canvas = canvasRef.current;

    if (!canvas) {
      return [];
    }

    const context = canvas.getContext('2d');
    const dpr = window.devicePixelRatio || 1;
    const { width, height } = canvas.getBoundingClientRect();
    const displayWidth = Math.max(width, 320);
    const displayHeight = Math.max(height, 220);

    canvas.width = displayWidth * dpr;
    canvas.height = displayHeight * dpr;
    context.setTransform(dpr, 0, 0, dpr, 0, 0);
    context.clearRect(0, 0, displayWidth, displayHeight);

    const paddingX = 28;
    const paddingY = 24;
    const innerWidth = displayWidth - paddingX * 2;
    const innerHeight = displayHeight - paddingY * 2;
    const min = Math.min(...trendSeries.map((point) => point.value)) - 8;
    const max = Math.max(...trendSeries.map((point) => point.value)) + 8;
    const chartPoints = trendSeries.map((point, index) => ({
      ...point,
      x: paddingX + (innerWidth / (trendSeries.length - 1)) * index,
      y: paddingY + innerHeight - ((point.value - min) / (max - min)) * innerHeight,
    }));

    const gradient = context.createLinearGradient(0, 0, displayWidth, displayHeight);
    gradient.addColorStop(0, 'rgba(125, 211, 252, 0.92)');
    gradient.addColorStop(0.5, 'rgba(167, 139, 250, 0.92)');
    gradient.addColorStop(1, 'rgba(134, 239, 172, 0.9)');

    context.strokeStyle = 'rgba(120, 138, 164, 0.12)';
    context.lineWidth = 1;
    for (let index = 0; index < 4; index += 1) {
      const y = paddingY + (innerHeight / 3) * index;
      context.beginPath();
      context.moveTo(paddingX, y);
      context.lineTo(displayWidth - paddingX, y);
      context.stroke();
    }

    const linePath = new Path2D();
    chartPoints.forEach((point, index) => {
      if (index === 0) {
        linePath.moveTo(point.x, point.y);
      } else {
        linePath.lineTo(point.x, point.y);
      }
    });

    context.strokeStyle = gradient;
    context.lineWidth = 4;
    context.lineJoin = 'round';
    context.lineCap = 'round';
    context.stroke(linePath);

    const areaPath = new Path2D(linePath);
    areaPath.lineTo(chartPoints[chartPoints.length - 1].x, displayHeight - paddingY);
    areaPath.lineTo(chartPoints[0].x, displayHeight - paddingY);
    areaPath.closePath();

    const areaGradient = context.createLinearGradient(0, paddingY, 0, displayHeight - paddingY);
    areaGradient.addColorStop(0, 'rgba(167, 139, 250, 0.24)');
    areaGradient.addColorStop(1, 'rgba(255, 255, 255, 0.04)');
    context.fillStyle = areaGradient;
    context.fill(areaPath);

    chartPoints.forEach((point, index) => {
      context.beginPath();
      context.arc(point.x, point.y, index === hoveredIndex ? 8 : 6, 0, Math.PI * 2);
      context.fillStyle = '#ffffff';
      context.fill();
      context.lineWidth = 4;
      context.strokeStyle = gradient;
      context.stroke();
    });

    return chartPoints;
  };

  const chartPointsRef = useRef([]);

  useEffect(() => {
    const render = () => {
      chartPointsRef.current = drawChart();
    };

    render();

    const handleResize = () => render();
    window.addEventListener('resize', handleResize);

    return () => window.removeEventListener('resize', handleResize);
  }, [hoveredIndex]);

  const handlePointerMove = (event) => {
    const canvas = canvasRef.current;

    if (!canvas || chartPointsRef.current.length === 0) {
      return;
    }

    const rect = canvas.getBoundingClientRect();
    const cursorX = event.clientX - rect.left;
    const cursorY = event.clientY - rect.top;

    let nearestIndex = 0;
    let nearestDistance = Number.POSITIVE_INFINITY;

    chartPointsRef.current.forEach((point, index) => {
      const distance = Math.hypot(point.x - cursorX, point.y - cursorY);
      if (distance < nearestDistance) {
        nearestDistance = distance;
        nearestIndex = index;
      }
    });

    if (nearestDistance < 44) {
      setHoveredIndex(nearestIndex);
    }
  };

  const hoveredPoint = chartPointsRef.current[hoveredIndex];

  return (
    <div className="trend-chart-shell">
      <canvas
        ref={canvasRef}
        aria-label="Mood trend line chart"
        onMouseMove={handlePointerMove}
        onFocus={() => setHoveredIndex(hoveredIndex)}
      />
      {hoveredPoint && (
        <div className="trend-tooltip" style={{ left: `calc(${hoveredPoint.x}px + 6px)`, top: `calc(${hoveredPoint.y}px - 12px)` }}>
          <strong>{hoveredPoint.label}</strong>
          <span>{hoveredPoint.value}% mood energy</span>
        </div>
      )}
    </div>
  );
}

function MoodVisualizer({ mode, moodTone }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;

    if (!canvas) {
      return undefined;
    }

    const context = canvas.getContext('2d');
    let animationFrameId;

    const render = (frame) => {
      const dpr = window.devicePixelRatio || 1;
      const { width, height } = canvas.getBoundingClientRect();
      const displayWidth = Math.max(width, 400);
      const displayHeight = Math.max(height, 400);

      canvas.width = displayWidth * dpr;
      canvas.height = displayHeight * dpr;
      context.setTransform(dpr, 0, 0, dpr, 0, 0);
      context.clearRect(0, 0, displayWidth, displayHeight);

      const time = frame / 60;
      const centerX = displayWidth / 2;
      const centerY = displayHeight / 2;
      const colors = palette[moodTone] || palette.neutral;

      const background = context.createRadialGradient(centerX, centerY, 20, centerX, centerY, Math.max(displayWidth, displayHeight));
      background.addColorStop(0, 'rgba(255, 255, 255, 0.68)');
      background.addColorStop(0.45, 'rgba(255, 255, 255, 0.16)');
      background.addColorStop(1, 'rgba(255, 255, 255, 0.04)');
      context.fillStyle = background;
      context.fillRect(0, 0, displayWidth, displayHeight);

      if (mode === 'mandala') {
        for (let ring = 0; ring < 6; ring += 1) {
          const radius = 52 + ring * 30 + Math.sin(time + ring * 0.5) * 8;
          context.beginPath();
          context.arc(centerX, centerY, radius, 0, Math.PI * 2);
          context.strokeStyle = toRgba(colors[ring % colors.length], 0.86);
          context.lineWidth = 8 - ring * 0.7;
          context.stroke();
        }
      } else if (mode === 'particles') {
        for (let particle = 0; particle < 54; particle += 1) {
          const angle = (particle / 54) * Math.PI * 2 + time * 0.18;
          const orbit = 68 + (particle % 7) * 10;
          const x = centerX + Math.cos(angle) * orbit + Math.sin(time + particle * 0.2) * 8;
          const y = centerY + Math.sin(angle) * orbit + Math.cos(time + particle * 0.3) * 8;
          const alpha = 0.3 + (particle % 6) * 0.08;
          context.beginPath();
          context.arc(x, y, 4 + (particle % 3), 0, Math.PI * 2);
          context.fillStyle = toRgba(colors[particle % colors.length], alpha);
          context.fill();
        }
      } else {
        for (let blob = 0; blob < 8; blob += 1) {
          const x = centerX + Math.cos(time * 0.85 + blob) * (54 + blob * 12);
          const y = centerY + Math.sin(time * 0.78 + blob * 1.15) * (42 + blob * 9);
          const size = 26 + blob * 10 + Math.sin(time + blob) * 7;
          const gradient = context.createRadialGradient(x, y, 8, x, y, size);
          gradient.addColorStop(0, toRgba(colors[blob % colors.length], 0.95));
          gradient.addColorStop(1, 'rgba(255, 255, 255, 0)');
          context.fillStyle = gradient;
          context.beginPath();
          context.arc(x, y, size, 0, Math.PI * 2);
          context.fill();
        }
      }

      animationFrameId = window.requestAnimationFrame(render);
    };

    animationFrameId = window.requestAnimationFrame(render);
    const handleResize = () => {
      window.cancelAnimationFrame(animationFrameId);
      animationFrameId = window.requestAnimationFrame(render);
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.cancelAnimationFrame(animationFrameId);
      window.removeEventListener('resize', handleResize);
    };
  }, [mode, moodTone]);

  return <canvas ref={canvasRef} aria-hidden="true" />;
}

function VoiceRecorder() {
  const [recording, setRecording] = useState(false);
  const [seconds, setSeconds] = useState(0);

  useEffect(() => {
    if (!recording) {
      return undefined;
    }

    const timerId = window.setInterval(() => {
      setSeconds((value) => value + 1);
    }, 1000);

    return () => window.clearInterval(timerId);
  }, [recording]);

  const toggleRecording = () => {
    if (recording) {
      setRecording(false);
      window.setTimeout(() => setSeconds(0), 400);
      return;
    }

    setSeconds(0);
    setRecording(true);
  };

  return (
    <section className="voice-panel panel fade-in delay-2">
      <div className="voice-cta">
        <h2 className="voice-title">Voice recording</h2>
        <button className={`mic-button ${recording ? 'recording' : ''}`} onClick={toggleRecording} aria-label="Toggle voice recording">
          {recording ? '◉' : '🎙'}
        </button>
        <p className="voice-note">Speak for 10-30 seconds about how you're feeling.</p>
      </div>

      {recording ? (
        <>
          <div className="waveform" aria-hidden="true">
            {Array.from({ length: 12 }).map((_, index) => (
              <span key={index} className="wave-bar" style={{ animationDelay: `${index * 90}ms`, height: `${18 + (index % 4) * 12}px` }} />
            ))}
          </div>
          <div className="voice-state">
            <span className="timer">Recording for {seconds} seconds</span>
            <button className="stop-button" onClick={toggleRecording}>
              Stop
            </button>
          </div>
          <div className="analysis-pill">
            <span className="spinner" aria-hidden="true" />
            Visual and voice analysis in progress
          </div>
        </>
      ) : (
        <div className="voice-state">
          <span className="timer">Ready to start recording</span>
          <button className="start-button" onClick={toggleRecording}>
            Start
          </button>
        </div>
      )}
    </section>
  );
}

const Dashboard = () => {
  const [mood, setMood] = useState('Calm');
  const [visualizerMode, setVisualizerMode] = useState('abstract');

  const moodTone = useMemo(() => {
    if (mood === 'Stressed') {
      return 'stress';
    }

    if (mood === 'Focused' || mood === 'Wavy') {
      return 'neutral';
    }

    return 'positive';
  }, [mood]);

  const message = mood === 'Stressed' ? 'You are moving through a demanding moment with care.' : "You're doing great today.";

  return (
    <main className="dashboard-page">
      <header className="dashboard-header fade-in">
        <div className="brand-block">
          <div className="brand-mark">M</div>
          <div className="brand-copy">
            <h1>MindFlow</h1>
            <p>Calm space for reflection and recovery</p>
          </div>
        </div>

        <div className="header-stats">
          <span className="status-pill">User status: steady</span>
          <span className="streak-pill">Streak 12 days</span>
          <button className="bell-button" aria-label="Notifications">
            ◌
          </button>
        </div>
      </header>

      <section className="dashboard-shell">
        <div className="section-intro fade-in delay-1">
          <p className="section-kicker">Daily check-in</p>
          <h2 className="section-title">A softer way to understand your day</h2>
        </div>

        <div className="dashboard-grid">
          <section className="mood-panel panel fade-in delay-1">
            <h3 className="panel-title">Mood</h3>
            <div className="mood-core">
              <div className="mood-ring">
                <div className="mood-circle">
                  <div>
                    <h3>{mood}</h3>
                    <p>{message}</p>
                  </div>
                </div>
              </div>

              <p className="mood-message">Tap a feeling to update the center state.</p>

              <div className="mood-selector" role="list" aria-label="Mood selector">
                {moodOptions.map((option) => (
                  <button
                    key={option}
                    className={`mood-chip ${mood === option ? 'active' : ''}`}
                    onClick={() => setMood(option)}
                    role="listitem"
                  >
                    {option}
                  </button>
                ))}
              </div>
            </div>
          </section>

          <section className="trend-panel panel fade-in delay-2">
            <h3 className="trend-title">Mood trends</h3>
            <MoodTrendChart />
            <div className="trend-meta">
              <span>Past 12 sessions</span>
              <span>Hover to inspect daily changes</span>
            </div>
          </section>

          <section className="stats-stack">
            {stats.map((item, index) => (
              <article key={item.label} className={`stats-card fade-in delay-${Math.min(index + 1, 3)}`}>
                <div className="stats-icon">{item.icon}</div>
                <p className="stats-value">{item.value}</p>
                <p className="stats-label">{item.label}</p>
              </article>
            ))}
          </section>

          <section className="visualizer-panel panel fade-in delay-2">
            <div className="insight-head">
              <h3 className="visualizer-title">Mood visualizer</h3>
              <span className="caption">No text overlays</span>
            </div>
            <div className="visualizer-stage">
              <MoodVisualizer mode={visualizerMode} moodTone={moodTone} />
            </div>
            <div className="visualizer-controls" aria-label="Visualization modes">
              <button className={`mode-button ${visualizerMode === 'abstract' ? 'active' : ''}`} onClick={() => setVisualizerMode('abstract')}>
                Abstract
              </button>
              <button className={`mode-button ${visualizerMode === 'mandala' ? 'active' : ''}`} onClick={() => setVisualizerMode('mandala')}>
                Mandala
              </button>
              <button className={`mode-button ${visualizerMode === 'particles' ? 'active' : ''}`} onClick={() => setVisualizerMode('particles')}>
                Particles
              </button>
            </div>
          </section>

          <VoiceRecorder />

          <section className="patterns-panel panel fade-in delay-3" id="patterns">
            <h3 className="patterns-title">Pattern recognition</h3>
            <article className="insight-card">
              <div className="insight-head">
                <div>
                  <div className="insight-icon">✦</div>
                  <strong>You tend to feel most stressed on Monday mornings.</strong>
                </div>
                <span className="caption">Weekly view</span>
              </div>

              <div className="progress-track" aria-hidden="true">
                <div className="progress-fill" style={{ width: '72%' }} />
              </div>

              <p className="insight-copy">Your recovery patterns improve after brief check-ins and lighter evening reflections.</p>
            </article>

            <div className="patterns-grid">
              <div className="pattern-week" aria-label="Weekly emotion patterns">
                {weeklyPatterns.map((day) => (
                  <div className="day-chip" key={day.day}>
                    <strong>{day.day}</strong>
                    <div className={`emotion-tag ${day.className}`} aria-hidden="true" />
                    <span>{day.emotion}</span>
                  </div>
                ))}
              </div>
            </div>
          </section>

          <section className="panel fade-in delay-3">
            <h3 className="patterns-title">Need a deeper check-in?</h3>
            <p className="support-note">Open the chat to reflect with the AI companion in a calmer, more guided flow.</p>
            <Link className="start-button" to="/chat">
              Open chat
            </Link>
          </section>
        </div>
      </section>
    </main>
  );
};

export default Dashboard;
