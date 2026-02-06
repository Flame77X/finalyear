# AI Interview Coaching System

A comprehensive AI-powered interview coaching platform that conducts mock interviews, analyzes candidate performance in real-time using multi-modal AI agents, and generates detailed feedback reports.

## 🚀 Project Overview

The **AI Interview Coaching System** is designed to simulate realistic technical interviews. It interacts with candidates through voice and video, assesses their performance across multiple dimensions (verbal, non-verbal, vocal, and content), and provides actionable feedback to help them improve.

### Key Features
-   **Interactive AI Interviewer**: An AI avatar (or voice) that asks relevant technical questions based on the candidate's branch (CSE, ECE, Mechanical, etc.) or resume.
-   **Multi-Modal Analysis**:
    -   **Verbal**: Analyzes the content of the answers for correctness and relevance.
    -   **Non-Verbal**: Tracks facial expressions and emotions via video (e.g., confidence, happiness vs. nervousness).
    -   **Vocal**: Analyzes speech patterns (confidence, pitch, tone) via audio signal processing.
-   **Real-time Scoring**: Orchestrates scores from all agents to produce a final holistic interview score.
-   **Automated Reporting**: Generates a PDF performance report and emails it to the candidate.
-   **Admin Dashboard**: Allows administrators to view sessions, manage candidates, and system settings.

## 🛠️ Tech Stack

### Frontend (User & Admin Clients)
-   **Framework**: [React](https://react.dev/) (v18)
-   **Build Tool**: [Vite](https://vitejs.dev/)
-   **Styling**: [Tailwind CSS](https://tailwindcss.com/)
-   **Icons**: [Lucide React](https://lucide.dev/)
-   **Animation**: [Framer Motion](https://www.framer.com/motion/)
-   **State Management**: React Hooks

### Backend (Server & API)
-   **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python)
-   **Concurrency**: AsyncIO for handling real-time WebSocket connections (video/audio streaming).
-   **Database**: MongoDB (via [Motor](https://motor.readthedocs.io/) async driver).

### AI & Machine Learning Agents
The backend is composed of specialized agents:

1.  **Brain Agent (Orchestrator)**
    -   **Tech**: [LangChain](https://www.langchain.com/), [Groq API](https://groq.com/) (Llama-3-70b).
    -   **Role**: Manages the interview flow (Intro → Branch Selection → Q&A). Generates dynamic questions if not found in the static dataset.

2.  **Verbal Agent (Content Analysis)**
    -   **Tech**: `SpeechRecognition` (Google Web Speech API) for transcription, `LangChain` + `Groq` for semantic similarity scoring.
    -   **Role**: Transcribes user audio to text and evaluates the accuracy of the answer against an "ideal" response.

3.  **Keyword Scorer (Content Analysis)**
    -   **Tech**: `LangChain` + `Groq`.
    -   **Role**: Extracts technical keywords from the user's transcript and compares them against expected domain terminologies (e.g., "algorithm", "database" for CSE).

4.  **Non-Verbal Agent (Video Analysis)**
    -   **Tech**: [DeepFace](https://github.com/serengil/deepface), `OpenCV`.
    -   **Role**: Analyzes video frames for facial emotions (Happy, Neutral, Fearful, etc.) to compute a "confidence" score based on facial cues.

5.  **Vocal Agent (Audio Analysis)**
    -   **Tech**: [Librosa](https://librosa.org/), `SoundFile`.
    -   **Role**: Analyzes audio signals for pitch, tone, and steadiness to determine vocal confidence.

6.  **Report Generator**
    -   **Tech**: `ReportLab` or similar PDF generation libraries.
    -   **Role**: Compiles all scores and insights into a downloadable PDF.

## 📂 Project Structure

```
finalyear/
├── admin_client/          # React Admin Dashboard
│   ├── src/
│   │   ├── pages/         # Dashboard, Sessions, Settings
│   │   └── layouts/       # Application shells
├── web_client/            # React Candidate Interface
│   ├── src/
│   │   ├── pages/         # Landing, Login, Interview Room
│   │   └── styles/        # Specific component styles
├── backend/               # Main FastAPI Server & Agents
│   ├── agents/            # Utility for lazy loading ML models
│   ├── brain_agent/       # Conversation logic (LLM)
│   ├── verbal_agent/      # Transcription & Semantic Score
│   ├── scoring_agent/     # Scoring Engine & Aggregation
│   ├── non_verbal_agent/  # Video emotion analysis
│   ├── vocal_agent/       # Audio signal analysis
│   ├── tts_agent/         # Text-To-Speech generation
│   ├── server.py          # FastAPI entry point
│   ├── store.py           # Database interactions (MongoDB)
│   ├── requirements.txt   # Python dependencies
│   └── questions.json     # Static question bank
```

## 📊 Marking & Scoring System

The system calculates a **Final Score (out of 100)** based on a weighted algorithm:

### 1. Accuracy & Content Score (55% weight)
Measures *what* the candidate said.
-   **Semantic Accuracy (65%)**: How well the meaning of the user's answer matches the ideal answer (LLM-based).
-   **Keyword Coverage (35%)**: Presence of required technical terms for the specific job role/branch.
    -   *(Calculated by `keyword_scorer.py`)*

### 2. Presentation & Confidence Score (45% weight)
Measures *how* the candidate said it.
-   **Vocal Confidence (55%)**: Based on voice steadiness, volume consistency, and lack of hesitation.
-   **Non-Verbal Confidence (45%)**: Based on facial expressions (e.g., maintaining a neutral/happy expression vs. fearful/sad).

*(Source: `backend/scoring_agent/engine.py`)*

## 🔄 User Workflow

1.  **Landing & Login**: User visits the web client, logs in, and optionally uploads a resume.
2.  **Introduction**: User enters the interview room. The AI greets the user.
3.  **Branch Selection**: User selects their domain (CSE, ECE, Civil, etc.) or the system detects it from the resume (future scope).
4.  **Interview Phase**:
    -   AI asks a question (TTS generates voice).
    -   User answers (Video & Audio recorded).
    -   **Real-time Processing**:
        -   Audio -> Transcribed -> Keyword/Semantic analysis.
        -   Video -> Emotion analysis.
5.  **Conclusion**: After a set number of questions, the interview ends.
6.  **Report**: The system calculates the final score, generates a PDF, and emails it to the user. Analysis is also saved to the Admin Dashboard.

## ⚙️ Installation & Setup

### Prerequisites
-   Python 3.9+
-   Node.js 16+
-   MongoDB (Running locally or Atlas URI)
-   Visual C++ Build Tools (required for some Python ML libraries)

### 1. Backend Setup
```bash
cd backend
python -m venv venv
# Activate venv: venv\Scripts\activate (Windows) or source venv/bin/activate (Mac/Linux)
pip install -r requirements.txt

# Create a .env file containing:
# MONGO_URI=mongodb://localhost:27017/
# GROQ_API_KEY=your_groq_api_key_here
# EMAIL_USER=your_email@gmail.com
# EMAIL_PASSWORD=your_app_password

python server.py
# Server starts at http://localhost:8000
```

### 2. Frontend Setup (Web Client)
```bash
cd web_client
npm install
npm run dev
# App starts at http://localhost:5173
```

### 3. Admin Panel Setup (Optional)
```bash
cd admin_client
npm install
npm run dev
# App starts at http://localhost:5174 (typically)
```

## 🧩 Libraries & Their Uses

| Library | Component | Purpose |
| :--- | :--- | :--- |
| **FastAPI** | Backend | High-performance API server. |
| **LangChain** | Backend | Framework for LLM interactions (Brain & Scoring). |
| **DeepFace** | Non-Verbal | Facial attribute analysis (Emotion detection). |
| **Librosa** | Vocal | Audio analysis for music and speech. |
| **Opencv-python** | Vision | Image processing for video frames. |
| **SpeechRecognition** | Verbal | Wrapper for Google's Speech-to-Text API. |
| **TailwindCSS** | Frontend | Utility-first CSS framework for rapid UI development. |
| **Framer Motion** | Frontend | Animation library for smooth UI transitions. |
| **Motor** | Database | Asynchronous MongoDB driver for Python. |
