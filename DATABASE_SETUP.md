# Database Setup Guide

## Overview

This guide explains how the database is configured for the AI Mental Awareness application to store and track stress levels, emotions, and chat history.

## Database Configuration

### Database Engine
- **Type**: SQLite (file-based database)
- **Location**: `backend/app.db`
- **Type Support**: Automatically created on first application startup

### Database Models

#### 1. Users Table
Stores user account information.

**Columns:**
- `id` (Integer): Primary key
- `email` (String): Unique email address
- `username` (String): Unique username
- `hashed_password` (String): Encrypted password
- `created_at` (DateTime): Account creation timestamp
- `updated_at` (DateTime): Last update timestamp

**Relationships:**
- Many-to-one with ChatSessions (one user has many chat sessions)
- Many-to-one with MoodEntries (one user has many mood entries)

#### 2. ChatSessions Table
Stores individual chat conversation sessions.

**Columns:**
- `id` (Integer): Primary key
- `user_id` (Integer): Foreign key to Users
- `title` (String): Optional session title
- `created_at` (DateTime): Session creation timestamp
- `updated_at` (DateTime): Last update timestamp

**Relationships:**
- One-to-many with ChatMessages (one session has multiple messages)

#### 3. ChatMessages Table
Stores individual chat messages with stress and emotion tracking.

**Columns:**
- `id` (Integer): Primary key
- `session_id` (Integer): Foreign key to ChatSessions
- `role` (String): Message role - "user" or "assistant"
- `content` (Text): Message content
- `detected_emotion` (String): Emotion detected by ML model (e.g., "happy", "sad", "anxious")
- `confidence` (Float): Confidence score for emotion detection (0.0-1.0)
- `stress_score` (Float): Stress level score (0-100)
- `stress_level` (String): Stress level category - "low", "moderate", or "high"
- `created_at` (DateTime): Message creation timestamp

**Relationships:**
- Many-to-one with ChatSessions

#### 4. MoodEntries Table
Stores user self-reported mood entries with stress tracking.

**Columns:**
- `id` (Integer): Primary key
- `user_id` (Integer): Foreign key to Users
- `mood` (String): Mood (e.g., "happy", "sad", "anxious", "calm")
- `intensity` (Float): Mood intensity (0.0-1.0 scale)
- `notes` (String): Optional notes
- `detected_sentiment` (String): Sentiment detected from notes
- `confidence_score` (Float): Confidence in sentiment detection
- `stress_level` (String): Stress level - "low", "moderate", or "high"
- `stress_score` (Float): Stress score (0-100)
- `created_at` (DateTime): Entry creation timestamp

**Relationships:**
- Many-to-one with Users

## Automatic Database Initialization

The database is **automatically created** when the FastAPI application starts:

```python
# In backend/app/main.py
from app.db.base import Base
from app.db.session import engine

# Create all database tables
Base.metadata.create_all(bind=engine)
```

All tables are created on first run if they don't exist.

## API Endpoints for Database Operations

### Chat Management Endpoints

#### Send a Chat Message
```
POST /api/v1/chat/message
```

**Request (JSON):**
```json
{
  "message": "I'm feeling stressed",
  "user_id": 1,
  "session_id": 1
}
```

**Response:**
```json
{
  "response": "I understand you're feeling stressed...",
  "session_id": 1,
  "message_id": 5,
  "detected_emotion": "anxious",
  "confidence": 0.92,
  "stress_score": 75,
  "stress_level": "high"
}
```

**Features:**
- Creates new session if `session_id` is not provided
- Saves both user and assistant messages with emotion/stress data
- Displays stress score and level in response

#### Get Chat History
```
GET /api/v1/chat/history?session_id=1
```

**Response:**
```json
{
  "session_id": 1,
  "title": "Chat Session",
  "created_at": "2026-04-09T10:00:00",
  "updated_at": "2026-04-09T10:30:00",
  "messages": [
    {
      "id": 1,
      "role": "user",
      "content": "I'm feeling stressed",
      "detected_emotion": "anxious",
      "confidence": 0.92,
      "stress_score": 75,
      "stress_level": "high",
      "created_at": "2026-04-09T10:00:00"
    },
    {
      "id": 2,
      "role": "assistant",
      "content": "I hear that you're under pressure...",
      "detected_emotion": "empathetic",
      "confidence": 0.88,
      "stress_score": 75,
      "stress_level": "high",
      "created_at": "2026-04-09T10:00:05"
    }
  ]
}
```

#### List User Chat Sessions
```
GET /api/v1/chat/sessions?user_id=1
```

**Response:**
```json
{
  "user_id": 1,
  "sessions": [
    {
      "id": 1,
      "title": "Chat Session",
      "created_at": "2026-04-09T10:00:00",
      "updated_at": "2026-04-09T10:30:00",
      "message_count": 10
    }
  ]
}
```

#### Create New Chat Session
```
POST /api/v1/chat/sessions
```

**Request (JSON):**
```json
{
  "user_id": 1,
  "title": "Monday Check-in"
}
```

#### Delete Chat Session
```
DELETE /api/v1/chat/sessions/1
```

### Mood Tracking Endpoints

#### Log Mood Entry
```
POST /api/v1/mood/log
```

**Request (JSON):**
```json
{
  "user_id": 1,
  "mood": "anxious",
  "intensity": 0.7,
  "stress_level": "moderate",
  "stress_score": 55,
  "notes": "Had a stressful meeting"
}
```

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "mood": "anxious",
  "intensity": 0.7,
  "notes": "Had a stressful meeting",
  "stress_level": "moderate",
  "stress_score": 55,
  "created_at": "2026-04-09T10:00:00"
}
```

#### Get Mood History
```
GET /api/v1/mood/history?user_id=1&limit=50
```

**Response:**
```json
{
  "user_id": 1,
  "entries": [
    {
      "id": 1,
      "mood": "anxious",
      "intensity": 0.7,
      "notes": "Had a stressful meeting",
      "stress_level": "moderate",
      "stress_score": 55,
      "created_at": "2026-04-09T10:00:00"
    }
  ]
}
```

#### Get Mood Analytics
```
GET /api/v1/mood/analytics?user_id=1&days=30
```

**Response:**
```json
{
  "user_id": 1,
  "total_entries": 15,
  "period_days": 30,
  "most_frequent_mood": "anxious",
  "average_intensity": 0.62,
  "average_stress_score": 62.0,
  "mood_distribution": {
    "anxious": 8,
    "calm": 5,
    "happy": 2
  },
  "stress_levels_distribution": {
    "high": 6,
    "moderate": 7,
    "low": 2
  }
}
```

#### Get Mood Trends
```
GET /api/v1/mood/trends?user_id=1&days=30
```

**Response:**
```json
{
  "user_id": 1,
  "period_days": 30,
  "daily_data": {
    "2026-04-09": {
      "entries": [
        {
          "mood": "anxious",
          "intensity": 0.7,
          "stress_score": 75,
          "stress_level": "high"
        }
      ],
      "avg_intensity": 0.7,
      "avg_stress": 75.0
    }
  }
}
```

## Data Flow

### Chat Message Flow
```
User Input
    ↓
Frontend sends POST /api/v1/chat/message
    ↓
Backend saves USER message to ChatMessages table
    ↓
ML models detect emotion and stress
    ↓
Chatbot service generates response
    ↓
Backend saves ASSISTANT message with emotion/stress data
    ↓
Response returned to frontend with stress metadata
```

### Mood Entry Flow
```
User logs mood manually
    ↓
Frontend sends POST /api/v1/mood/log
    ↓
Backend stores entry in MoodEntries table with stress data
    ↓
Response confirms entry saved
    ↓
User can query history/analytics via GET endpoints
```

## Stress Score Mapping

**Stress Levels:**
- `low`: Stress score 0-40 (relaxed, calm)
- `moderate`: Stress score 40-70 (some tension, manageable)
- `high`: Stress score 70-100 (significant tension, needs attention)

## Accessing the Database

### Direct SQLite Access

To inspect the database file directly:

```bash
# Windows PowerShell
sqlite3 backend/app.db

# List tables
.tables

# View table schema
.schema chat_messages

# Query data
SELECT * FROM chat_messages LIMIT 10;
```

### Programmatic Access

The database is fully integrated with FastAPI and SQLAlchemy. All operations go through the API endpoints, which handle:
- Connection pooling
- Transaction management
- Data validation
- Error handling

## Database Persistence

- **Location**: `backend/app.db` (SQLite file)
- **Persistence**: Data persists between application restarts
- **Backup**: Copy `backend/app.db` to back up all data
- **Reset**: Delete `backend/app.db` to start with a clean database

## Scaling Considerations

For production use, consider migrating to:
- **PostgreSQL**: For multi-user concurrent access
- **MySQL**: For cloud deployment
- **MongoDB**: For flexible schema and large-scale mood data

Update `SQLALCHEMY_DATABASE_URL` in `backend/app/db/session.py` accordingly.

## Troubleshooting

### Database locked errors
- Ensure only one application instance is running
- Close any open SQLite connections
- Restart the application

### Missing stress fields
- Verify models have been updated with stress_score and stress_level columns
- Delete old database and let it be recreated: `rm backend/app.db`

### Chat history not saving
- Verify database initialization succeeded (check logs at startup)
- Confirm session_id is being returned and used in subsequent requests
- Check database file permissions

## Summary

The database system automatically tracks:
✅ All chat messages with emotion and stress detection
✅ User mood entries with intensity and stress levels
✅ Session-based conversation history
✅ Timestamps for all entries
✅ User-specific data isolation

All data persists between sessions and can be queried via REST API endpoints.
