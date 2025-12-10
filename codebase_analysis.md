# AI Interviewer System - Codebase Analysis

Here is the complete source code for the 6 core components of the system.

---

## 1. Backend Server (`server.py`)
**Role**: Central Controller. Manages API, Agents, and Audio Processing.
```python
import os
import shutil
import uuid
import logging
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Import Agents
from tts_agent.tts_engine import TTSEngine
from verbal_agent.verbal_analyzer import VerbalAnalyzer
from brain_agent.orchestrator import BrainAgent
try:
    from vocal_agent.vocal_analyzer import VocalAnalyzer
    VOCAL_AGENT_AVAILABLE = True
except ImportError:
    VOCAL_AGENT_AVAILABLE = False
    logger.warning("VocalAnalyzer not available (Librosa installing?). Skipping.")

# --- Configuration ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_AUDIO_DIR = os.path.join(BASE_DIR, "temp_audio")
os.makedirs(TEMP_AUDIO_DIR, exist_ok=True)

# --- Initialize Agents ---
logger.info("Initializing Agents...")
try:
    tts_agent = TTSEngine()
    verbal_agent = VerbalAnalyzer(model_size="base.en")
    brain_agent = BrainAgent()
    if VOCAL_AGENT_AVAILABLE:
        vocal_agent = VocalAnalyzer()
    
    logger.info(f"Agents initialized. Vocal Support: {VOCAL_AGENT_AVAILABLE}")
except Exception as e:
    logger.error(f"Failed to initialize agents: {e}")
    raise RuntimeError("Agent initialization failed.")

# --- FastAPI App ---
app = FastAPI(title="AI Interviewer Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/process_audio")
async def process_audio(file: UploadFile = File(...)):
    session_id = str(uuid.uuid4())
    user_audio_path = os.path.join(TEMP_AUDIO_DIR, f"user_{session_id}.wav")
    
    try:
        with open(user_audio_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 1. Transcribe
        transcript = verbal_agent.transcribe(user_audio_path)
        logger.info(f"User Transcribed: {transcript}")

        # 2. Analyze Tone
        vocal_metrics = None
        if VOCAL_AGENT_AVAILABLE:
            vocal_metrics = vocal_agent.analyze(user_audio_path)
            logger.info(f"Vocal Metrics: {vocal_metrics}")
        
        # 3. Generate Response
        ai_text = brain_agent.get_response(transcript)
        logger.info(f"AI Response: {ai_text}")
            
        # 4. Generate Audio
        ai_audio_abs_path = tts_agent.speak(ai_text)
        if not ai_audio_abs_path:
            raise HTTPException(status_code=500, detail="TTS Generation failed")

        ai_audio_filename = os.path.basename(ai_audio_abs_path)
            
        return {
            "transcript": transcript,
            "ai_response_text": ai_text,
            "ai_audio_filename": ai_audio_filename,
            "vocal_metrics": vocal_metrics
        }

    except Exception as e:
        logger.error(f"Processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(user_audio_path):
            os.remove(user_audio_path)

@app.get("/audio/{filename}")
async def get_audio(filename: str):
    file_path = os.path.join(TEMP_AUDIO_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="audio/wav")
    raise HTTPException(status_code=404, detail="Audio file not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## 2. Brain Agent (`brain_agent/orchestrator.py`)
**Role**: Logic & Reasoning. Tracks interview state and determines responses.
```python
import random
import re

class BrainAgent:
    def __init__(self):
        self.interview_state = "intro"
        self.questions = [
            "Could you tell me about a challenging project you worked on?",
            "How do you handle conflict in a team environment?",
            "What are your greatest strengths as an engineer?",
            "Where do you see yourself in five years?",
            "Do you have any questions for us?"
        ]
        self.question_index = 0
        self.candidate_answers = {} 

    def _clean_text(self, text):
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        return set(text.split())

    def get_response(self, user_text: str) -> str:
        words = self._clean_text(user_text)
        
        if self.interview_state == "intro":
            if any(w in words for w in ["hello", "hi", "hey", "greetings"]):
                return "Hello! I am ready to begin your interview. Please introduce yourself."
            
            if any(w in words for w in ["name", "am", "im", "engineer", "student", "developer", "ready"]):
                self.interview_state = "questions"
                self.question_index = 0
                return f"It is nice to meet you. Let's dive in. {self.questions[0]}"
            
            return "Could you please tell me a bit about yourself? I'd love to know your background."

        elif self.interview_state == "questions":
            current_q = self.questions[self.question_index]
            self.candidate_answers[current_q] = user_text
            self.question_index += 1
            
            if self.question_index < len(self.questions):
                next_q = self.questions[self.question_index]
                acknowledgements = ["I see.", "That sounds impressive.", "Interesting approach.", "Good to know."]
                return f"{random.choice(acknowledgements)} {next_q}"
            else:
                self.interview_state = "finished"
                return "Thank you. That concludes the technical portion. Do you have any final words?"

        elif self.interview_state == "finished":
            return "Thank you very much. We will be in touch shortly. Have a great day."

        return "I'm not sure I understood. Could you rephrase?"
```

---

## 3. Verbal Agent (`verbal_agent/verbal_analyzer.py`)
**Role**: The Ear. Transcribes Audio (STT).
```python
import os
import logging
from faster_whisper import WhisperModel
from sentence_transformers import SentenceTransformer, util

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VerbalAnalyzer:
    def __init__(self, model_size="base.en", embedding_model="all-MiniLM-L6-v2"):
        logger.info(f"Loading Whisper model: {model_size}...")
        try:
            self.stt_model = WhisperModel(model_size, device="cpu", compute_type="int8")
        except Exception as e:
            logger.error(f"Failed to load Whisper: {e}")
            raise

        try:
            self.embed_model = SentenceTransformer(embedding_model)
        except Exception as e:
            logger.error(f"Failed to load Embedding model: {e}")
            raise

    def transcribe(self, audio_path: str) -> str:
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        try:
            segments, info = self.stt_model.transcribe(audio_path, beam_size=5)
            return " ".join([segment.text for segment in segments]).strip()
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return ""

    def score_answer(self, user_text: str, correct_answer_concept: str) -> float:
        if not user_text or not correct_answer_concept: return 0.0
        try:
            e1 = self.embed_model.encode(user_text, convert_to_tensor=True)
            e2 = self.embed_model.encode(correct_answer_concept, convert_to_tensor=True)
            return max(0.0, min(100.0, float(util.cos_sim(e1, e2)[0][0]) * 100))
        except Exception as e:
            logger.error(f"Scoring failed: {e}")
            return 0.0
```

---

## 4. Vocal Agent (`vocal_agent/vocal_analyzer.py`)
**Role**: The Analyst. Detects Tone/Pitch/Confidence.
```python
import librosa
import numpy as np
import logging
import traceback

logger = logging.getLogger(__name__)

class VocalAnalyzer:
    def __init__(self):
        self.target_sr = 16000

    def analyze(self, audio_path: str) -> dict:
        try:
            y, sr = librosa.load(audio_path, sr=self.target_sr)
            if len(y) == 0: return self._get_empty_metrics()

            pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
            pitch_indices = magnitudes > np.median(magnitudes)
            selected_pitches = pitches[pitch_indices]
            avg_pitch = np.mean(selected_pitches) if len(selected_pitches) > 0 else 0
            
            rms = librosa.feature.rms(y=y)
            avg_energy = np.mean(rms)

            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr)
            avg_tempo = tempo[0] if len(tempo) > 0 else 0

            # Confidence Logic
            score = 50.0
            if avg_energy > 0.02: score += 10
            if avg_energy > 0.05: score += 10
            if 100 < avg_tempo < 160: score += 10
            if avg_pitch > 50: score += 10
            score = min(100.0, score)

            results = {
                "avg_pitch": float(avg_pitch),
                "avg_energy": float(avg_energy),
                "speech_rate": float(avg_tempo),
                "confidence_score": float(score)
            }
            
            # Debug Print
            print(f"\n[VOCAL ANALYSIS] 🎤 Pitch: {avg_pitch:.1f}Hz | Tempo: {avg_tempo:.1f}BPM | Energy: {avg_energy:.3f}")
            print(f"[VOCAL ANALYSIS] ⭐ Confidence Score: {score:.1f}%\n")
            
            logger.info(f"Vocal Analysis: {results}")
            return results

        except Exception as e:
            logger.error(f"Vocal Analysis failed: {e}")
            print("\n[VOCAL ERROR DEBUG]")
            traceback.print_exc()
            print("-------------------\n")
            return self._get_empty_metrics()

    def _get_empty_metrics(self):
        return {"avg_pitch": 0.0, "avg_energy": 0.0, "speech_rate": 0.0, "confidence_score": 0.0}
```

---

## 5. TTS Agent (`tts_agent/tts_engine.py`)
**Role**: The Voice. Speech Synthesis.
```python
import os
import wave
import uuid
import subprocess
import numpy as np

class TTSEngine:
    def __init__(self, piper_path=None, model_path=None):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.piper_path = piper_path or os.path.join(base_dir, "piper", "piper.exe")
        self.model_path = model_path or os.path.join(base_dir, "models", "en_US-lessac-medium.onnx")

    def speak(self, text: str) -> str:
        output_filename = f"speech_{uuid.uuid4()}.wav"
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "temp_audio", output_filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        raw_temp = output_path.replace(".wav", "_raw.wav")

        cmd = [self.piper_path, "--model", self.model_path, "--output_file", raw_temp]
        
        try:
            process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            process.communicate(input=text.encode('utf-8'))
            
            if os.path.exists(raw_temp):
                self._scale_volume(raw_temp, output_path, factor=0.2)
                if os.path.exists(raw_temp): os.remove(raw_temp)
                return os.path.abspath(output_path)
            return None
        except Exception as e:
            print(f"Error in TTS speak: {e}")
            return None

    def _scale_volume(self, input_path, output_path, factor=0.2):
        try:
            with wave.open(input_path, "rb") as wf:
                params = wf.getparams()
                frames = wf.readframes(wf.getnframes())
            
            audio_data = np.frombuffer(frames, dtype=np.int16)
            scaled_data = (audio_data * factor).astype(np.int16)
            
            with wave.open(output_path, "wb") as wf:
                wf.setparams(params)
                wf.writeframes(scaled_data.tobytes())
        except:
             if os.path.exists(input_path): os.rename(input_path, output_path)
```
