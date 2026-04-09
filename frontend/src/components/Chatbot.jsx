import React, { useState, useRef, useEffect } from 'react';

const Chatbot = ({
  onSendMessage,
  messages,
  onStartVoice,
  onStopVoice,
  isRecording,
  onStartVideo,
  onStopVideo,
  videoActive,
  videoStream,
}) => {
  const [input, setInput] = useState('');
  const videoRef = useRef(null);
  const [recordingTime, setRecordingTime] = useState(0);

  // Display video stream
  useEffect(() => {
    if (videoRef.current && videoStream) {
      videoRef.current.srcObject = videoStream;
    }
  }, [videoStream]);

  // Recording timer
  useEffect(() => {
    let interval;
    if (isRecording) {
      interval = setInterval(() => {
        setRecordingTime((prev) => prev + 1);
      }, 1000);
    } else {
      setRecordingTime(0);
    }
    return () => clearInterval(interval);
  }, [isRecording]);

  const handleSend = () => {
    if (input.trim()) {
      onSendMessage(input, 'text', null);
      setInput('');
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="chatbot-container">
      {/* Video Chat Section */}
      {videoActive && (
        <div className="video-chat-panel">
          <div className="video-feed">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="video-stream"
            />
            <div className="video-indicator">
              <span className="live-pulse">● LIVE</span>
            </div>
          </div>
          <button className="video-close-btn" onClick={onStopVideo} title="End video chat">
            ✕
          </button>
        </div>
      )}

      {/* Chat Messages */}
      <div className="chat-messages">
        {messages && messages.length === 0 && (
          <div className="chat-welcome">
            <div className="welcome-icon">💙</div>
            <h2>Welcome to Mental Health Chat</h2>
            <p>Share your feelings through text, voice, or video</p>
            <div className="quick-prompts">
              <button onClick={() => onSendMessage('I am feeling stressed')} className="prompt-btn">
                😰 I'm Stressed
              </button>
              <button onClick={() => onSendMessage('I need motivation')} className="prompt-btn">
                💪 I Need Motivation
              </button>
              <button onClick={() => onSendMessage('How can I relax?')} className="prompt-btn">
                🧘 How to Relax?
              </button>
            </div>
          </div>
        )}
        {messages &&
          messages.map((msg, index) => (
            <div key={index} className={`message ${msg.role}`}>
              {msg.mediaType === 'audio' && (
                <div className="media-message">
                  <span className="media-icon">🎤</span>
                  <span>Voice message</span>
                </div>
              )}
              {msg.mediaType === 'video' && (
                <div className="media-message">
                  <span className="media-icon">📹</span>
                  <span>Video message</span>
                </div>
              )}
              {(msg.mediaType === 'text' || !msg.mediaType) && <p>{msg.content}</p>}
            </div>
          ))}
      </div>

      {/* Chat Input Area */}
      <div className="chat-input-section">
        {/* Recording Indicator */}
        {isRecording && (
          <div className="recording-indicator">
            <div className="recording-pulse">
              <span className="pulse-dot"></span>
              <span className="pulse-text">Recording... {formatTime(recordingTime)}</span>
            </div>
          </div>
        )}

        {/* Input Controls */}
        <div className="chat-controls">
          <div className="input-group">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              placeholder={videoActive ? 'Share via video or type...' : 'How are you feeling today?'}
              className="chat-input"
              disabled={isRecording}
            />
            <button
              onClick={handleSend}
              className="send-btn"
              disabled={!input.trim() || isRecording}
              title="Send message"
            >
              ➤
            </button>
          </div>

          {/* Media Buttons */}
          <div className="media-buttons">
            {/* Voice Button */}
            <button
              onClick={isRecording ? onStopVoice : onStartVoice}
              className={`media-btn voice-btn ${isRecording ? 'recording' : ''}`}
              title={isRecording ? 'Stop recording' : 'Start voice recording'}
            >
              {isRecording ? '⏹ Stop' : '🎤'}
            </button>

            {/* Video Button */}
            <button
              onClick={videoActive ? onStopVideo : onStartVideo}
              className={`media-btn video-btn ${videoActive ? 'active' : ''}`}
              title={videoActive ? 'End video chat' : 'Start video chat'}
            >
              {videoActive ? '🎥 Active' : '📹'}
            </button>

            {/* Emoji/Mood Button */}
            <button
              onClick={() =>
                onSendMessage('😊 I am feeling good today! Thanks for checking in.', 'text', null)
              }
              className="media-btn mood-btn"
              title="Send quick mood"
            >
              😊
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chatbot;
