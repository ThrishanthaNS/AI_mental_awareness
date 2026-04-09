import React, { useState } from 'react';
import Chatbot from '../components/Chatbot';
import { sendMessage } from '../services/api';
import { Link } from 'react-router-dom';

const Chat = () => {
  const [messages, setMessages] = useState([]);

  const handleSendMessage = async (message) => {
    const userMessage = { role: 'user', content: message };
    setMessages((prev) => [...prev, userMessage]);

    try {
      const response = await sendMessage(message);
      const botMessage = { role: 'assistant', content: response.response };
      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  return (
    <div className="chat-page">
      <header>
        <Link className="back-link" to="/">← Back to Dashboard</Link>
        <h1>AI Mental Health Chat</h1>
      </header>
      <Chatbot messages={messages} onSendMessage={handleSendMessage} />
    </div>
  );
};

export default Chat;
