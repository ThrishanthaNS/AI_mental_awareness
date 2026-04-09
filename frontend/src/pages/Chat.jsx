import React, { useState, useRef } from 'react';
import Chatbot from '../components/Chatbot';
import { sendMessage } from '../services/api';
import { Link } from 'react-router-dom';

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const [videoActive, setVideoActive] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const videoStreamRef = useRef(null);
  const audioStreamRef = useRef(null);

  const handleSendMessage = async (message, mediaType = 'text', mediaData = null) => {
    const userMessage = {
      role: 'user',
      content: message,
      mediaType,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);

    try {
      const response = await sendMessage(message, mediaType, mediaData, sessionId);
      if (response?.session_id) {
        setSessionId(response.session_id);
      }
      const botMessage = {
        role: 'assistant',
        content: response?.response || 'I am here with you. Try sharing a bit more about what you feel right now.',
        mediaType: 'text',
        stressScore: response?.stress_score,
        stressLevel: response?.stress_level,
        detectedEmotion: response?.detected_emotion,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        role: 'assistant',
        content: '❌ Failed to send message. Please try again.',
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    }
  };

  const startVoiceRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioStreamRef.current = stream;
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        const audioUrl = URL.createObjectURL(audioBlob);
        await handleSendMessage('📎 Voice message', 'audio', audioBlob);
        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Error accessing microphone:', error);
      alert('Microphone access denied. Please allow microphone permissions.');
    }
  };

  const stopVoiceRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const startVideoChat = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 1280 }, height: { ideal: 720 } },
        audio: true,
      });
      videoStreamRef.current = stream;
      setVideoActive(true);
    } catch (error) {
      console.error('Error accessing camera:', error);
      alert('Camera access denied. Please allow camera and microphone permissions.');
    }
  };

  const stopVideoChat = () => {
    if (videoStreamRef.current) {
      videoStreamRef.current.getTracks().forEach((track) => track.stop());
      videoStreamRef.current = null;
      setVideoActive(false);
    }
  };

  return (
    <div className="chat-page">
      <header>
        <Link className="back-link" to="/">← Back to Dashboard</Link>
        <h1>🤖 AI Mental Health Chat</h1>
      </header>
      <Chatbot
        messages={messages}
        onSendMessage={handleSendMessage}
        onStartVoice={startVoiceRecording}
        onStopVoice={stopVoiceRecording}
        isRecording={isRecording}
        onStartVideo={startVideoChat}
        onStopVideo={stopVideoChat}
        videoActive={videoActive}
        videoStream={videoStreamRef.current}
      />
    </div>
  );
};

export default Chat;
