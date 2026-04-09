# Architecture Overview

## System Architecture

The AI Mental Awareness platform follows a **three-tier architecture**:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Frontend      │────▶│    Backend       │────▶│    ML Models     │
│  (React + Vite)  │◀────│   (FastAPI)      │◀────│  (Python/TF)     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                              │
                              ▼
                        ┌─────────────┐
                        │  Database    │
                        │  (SQLite)    │
                        └─────────────┘
```

## Components

### 1. Frontend (React)
- **Dashboard**: Mood visualization, analytics, and recommendations
- **Chat**: AI-powered conversational mental health support
- **Components**: Reusable UI components (Chatbot, MoodChart, InputBox)

### 2. Backend (FastAPI)
- **Auth**: JWT-based authentication (register, login, refresh)
- **Mood**: Mood logging, history retrieval, and analytics
- **Chatbot**: Conversational AI endpoint
- **Detection**: Emotion/stress detection from text and media
- **Recommendations**: Personalized mental health recommendations

### 3. ML Models
- **Sentiment Model**: Text sentiment analysis (positive/negative/neutral)
- **Stress Model**: Stress level detection from text
- **Emotion Model**: Multi-class emotion detection (anger, fear, happiness, etc.)

## Data Flow

1. User interacts with the **Frontend**
2. Frontend sends API requests to the **Backend**
3. Backend processes requests, calls **ML inference** when needed
4. ML models return predictions to the Backend
5. Backend stores data in the **Database** and returns responses
6. Frontend displays results to the user

## Tech Stack

| Layer      | Technology           |
|------------|---------------------|
| Frontend   | React, Vite, React Router |
| Backend    | FastAPI, SQLAlchemy, Pydantic |
| ML         | scikit-learn, TensorFlow, Transformers |
| Database   | SQLite (dev) / PostgreSQL (prod) |
| Deployment | Docker, Docker Compose |
