# 🧠 AI Mental Awareness

An AI-powered mental health awareness and support platform that uses machine learning to detect emotions, track mood patterns, and provide personalized mental health recommendations.

## 🌟 Features

- **Mood Tracking**: Log and visualize your mood over time with trend analytics
- **AI Chatbot**: Conversational mental health support powered by NLP
- **Emotion Detection**: Detect emotional state from text and media inputs
- **Sentiment Analysis**: Analyze sentiment in journal entries and messages
- **Stress Detection**: Real-time stress level monitoring
- **Personalized Recommendations**: AI-driven mental health resources and coping strategies

## 🏗️ Architecture

```
Frontend (React + Vite)  →  Backend (FastAPI)  →  ML Models (Python/TensorFlow)
                                    ↓
                              Database (SQLite/PostgreSQL)
```

## 📁 Project Structure

```
AI_mental_awareness/
├── backend/          # FastAPI backend
│   ├── app/
│   │   ├── api/      # API routes (auth, mood, chatbot, detection, recommendations)
│   │   ├── core/     # Config, security, constants
│   │   ├── models/   # SQLAlchemy DB models
│   │   ├── schemas/  # Pydantic validation schemas
│   │   ├── services/ # Business logic layer
│   │   ├── db/       # Database config
│   │   └── main.py   # FastAPI entry point
│   └── tests/
├── ml/               # Machine learning models
│   ├── data/         # Raw and processed datasets
│   ├── models/       # Trained model files
│   ├── notebooks/    # Jupyter notebooks for experimentation
│   ├── pipelines/    # Preprocessing, training, evaluation
│   └── inference/    # Prediction module (used by backend)
├── frontend/         # React frontend
│   └── src/
│       ├── components/   # Chatbot, MoodChart, InputBox
│       ├── pages/        # Dashboard, Chat
│       └── services/     # API client
├── data/             # Global shared data (logs, exports)
├── docs/             # Documentation
├── scripts/          # Utility scripts
├── docker-compose.yml
└── .env
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker (optional)

### Option 1: Manual Setup

```bash
# 1. Clone the repository
git clone https://github.com/your-username/AI_mental_awareness.git
cd AI_mental_awareness

# 2. Setup backend
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
cd ..

# 3. Setup ML environment
cd ml
pip install -r requirements.txt
cd ..

# 4. Setup frontend
cd frontend
npm install
cd ..

# 5. Start backend
cd backend
uvicorn app.main:app --reload --port 8000

# 6. Start frontend (new terminal)
cd frontend
npm run dev
```

### Option 2: Docker

```bash
docker-compose up --build
```

## 🔗 API Endpoints

| Method | Endpoint                     | Description                    |
|--------|------------------------------|--------------------------------|
| POST   | `/api/v1/auth/register`      | Register a new user            |
| POST   | `/api/v1/auth/login`         | Login and get JWT token        |
| POST   | `/api/v1/mood/log`           | Log a mood entry               |
| GET    | `/api/v1/mood/history`       | Get mood history               |
| GET    | `/api/v1/mood/analytics`     | Get mood analytics             |
| POST   | `/api/v1/chat/message`       | Chat with AI assistant         |
| POST   | `/api/v1/detect/text`        | Detect emotion from text       |
| POST   | `/api/v1/detect/media`       | Detect emotion from media      |
| GET    | `/api/v1/recommendations/`   | Get personalized recommendations |

📖 Full API docs available at `http://localhost:8000/docs` (Swagger UI)

## 🛠️ Tech Stack

| Layer      | Technology                          |
|------------|-------------------------------------|
| Frontend   | React 18, Vite, React Router        |
| Backend    | FastAPI, SQLAlchemy, Pydantic       |
| ML/AI      | scikit-learn, TensorFlow, Transformers |
| Database   | SQLite (dev) / PostgreSQL (prod)    |
| Deployment | Docker, Docker Compose              |

## 📊 ML Models

| Model             | Task                       | Format |
|--------------------|---------------------------|--------|
| Sentiment Model    | Text sentiment analysis    | `.pkl` |
| Stress Model       | Stress level detection     | `.pkl` |
| Emotion Model      | Multi-class emotion detection | `.h5` |

## 📄 Documentation

- [Architecture Overview](docs/architecture.md)
- [API Documentation](docs/api_docs.md)
- [ML Model Details](docs/model_details.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.
