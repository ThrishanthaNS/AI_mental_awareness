import React, { useState, useRef } from 'react';
import Chatbot from '../components/Chatbot';
import { sendMessage } from '../services/api';
import { Link } from 'react-router-dom';

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const [videoActive, setVideoActive] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const videoStreamRef = useRef(null);
  const audioStreamRef = useRef(null);

  const pickAudioMimeType = () => {
    const options = ['audio/webm;codecs=opus', 'audio/webm', 'audio/ogg;codecs=opus', 'audio/ogg'];
    for (const candidate of options) {
      if (window.MediaRecorder && MediaRecorder.isTypeSupported(candidate)) {
        return candidate;
      }
    }
    return '';
  };

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
      if (mediaType === 'audio' && response?.transcription?.text) {
        setMessages((prev) => {
          if (!prev.length) return prev;
          const next = [...prev];
          const lastIndex = next.length - 1;
          if (next[lastIndex].role === 'user' && next[lastIndex].mediaType === 'audio') {
            next[lastIndex] = {
              ...next[lastIndex],
              content: response.transcription.text,
              transcription: response.transcription,
            };
          }
          return next;
        });
      }
      const botMessage = {
        role: 'assistant',
        content: response?.response || 'I am here with you. Try sharing a bit more about what you feel right now.',
        mediaType: 'text',
        videoAnalysis: response?.video_analysis || null,
        transcription: response?.transcription || null,
        audioDebug: response?.audio_debug || null,
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
      const mimeType = pickAudioMimeType();
      const mediaRecorder = mimeType ? new MediaRecorder(stream, { mimeType }) : new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const resolvedMimeType = mediaRecorder.mimeType || mimeType || 'audio/webm';
        const audioBlob = new Blob(audioChunksRef.current, { type: resolvedMimeType });
        if (!audioBlob.size) {
          setMessages((prev) => [
            ...prev,
            {
              role: 'assistant',
              content: '❌ Audio recording was empty. Please hold the mic button a bit longer and try again.',
              mediaType: 'text',
              timestamp: new Date().toISOString(),
            },
          ]);
          stream.getTracks().forEach((track) => track.stop());
          return;
        }
        await handleSendMessage('📎 Voice message', 'audio', audioBlob);
        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorder.start(250);
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

  const analyzeCurrentVideoFrame = async () => {
    if (!videoStreamRef.current) {
      return;
    }

    const track = videoStreamRef.current.getVideoTracks()[0];
    if (!track) {
      return;
    }

    const imageCaptureSupported = 'ImageCapture' in window;
    if (imageCaptureSupported) {
      try {
        const imageCapture = new window.ImageCapture(track);
        const bitmap = await imageCapture.grabFrame();
        const canvas = document.createElement('canvas');
        canvas.width = bitmap.width;
        canvas.height = bitmap.height;
        const ctx = canvas.getContext('2d');
        if (!ctx) return;
        ctx.drawImage(bitmap, 0, 0);
        const blob = await new Promise((resolve) => canvas.toBlob(resolve, 'image/jpeg', 0.9));
        if (blob) {
          await handleSendMessage('Analyze my current expression', 'video', blob);
          return;
        }
      } catch (error) {
        console.error('Error capturing frame with ImageCapture:', error);
      }
    }

    // Fallback: draw from a temporary video element bound to the stream.
    const video = document.createElement('video');
    video.srcObject = videoStreamRef.current;
    video.muted = true;
    video.playsInline = true;
    await video.play();

    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    const context = canvas.getContext('2d');
    if (!context) {
      video.pause();
      return;
    }
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const blob = await new Promise((resolve) => canvas.toBlob(resolve, 'image/jpeg', 0.9));
    video.pause();

    if (blob) {
      await handleSendMessage('Analyze my current expression', 'video', blob);
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
        onAnalyzeVideo={analyzeCurrentVideoFrame}
        videoActive={videoActive}
        videoStream={videoStreamRef.current}
      />
    </div>
  );
};

export default Chat;
