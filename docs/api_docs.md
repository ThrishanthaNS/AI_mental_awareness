# API Documentation

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication

### POST `/auth/register`
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "securepassword"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "created_at": "2024-01-01T00:00:00"
}
```

### POST `/auth/login`
Authenticate and receive a JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

---

## Mood Tracking

### POST `/mood/log`
Log a new mood entry.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "mood": "happy",
  "intensity": 0.8,
  "notes": "Had a great day at work"
}
```

### GET `/mood/history`
Get mood history for the authenticated user.

**Headers:** `Authorization: Bearer <token>`

### GET `/mood/analytics`
Get mood analytics and trends.

**Headers:** `Authorization: Bearer <token>`

---

## Chatbot

### POST `/chat/message`
Send a message to the AI chatbot.

**Request Body:**
```json
{
  "message": "I've been feeling anxious lately",
  "session_id": null
}
```

**Response:**
```json
{
  "response": "I hear you. Anxiety can be really challenging...",
  "session_id": 1,
  "detected_emotion": "anxious",
  "confidence": 0.87
}
```

---

## Detection

### POST `/detect/text`
Detect emotional state from text input.

### POST `/detect/media`
Detect emotional state from uploaded media (image/audio).

---

## Recommendations

### GET `/recommendations/`
Get personalized recommendations.

### GET `/recommendations/resources`
Get curated mental health resources.
