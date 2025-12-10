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
from scoring_agent.engine import ScoringEngine
from non_verbal_agent.video_analyzer import VideoAnalyzer
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
# --- Initialize Agents ---
logger.info("Initializing Agents...")

# 1. TTS Agent (Critical)
try:
    tts_agent = TTSEngine()
    logger.info("✅ TTS Agent initialized.")
except Exception as e:
    logger.error(f"❌ TTS Agent failed: {e}")
    # We allow startup but TTS will fail later
    tts_agent = None 

# 2. Verbal Agent (Critical)
try:
    verbal_agent = VerbalAnalyzer(model_size="base.en")
    logger.info("✅ Verbal Agent initialized.")
except Exception as e:
    logger.error(f"❌ Verbal Agent failed: {e}")
    verbal_agent = None

# 3. Brain Agent (Critical)
try:
    brain_agent = BrainAgent()
    logger.info("✅ Brain Agent initialized.")
except Exception as e:
    logger.error(f"❌ Brain Agent failed: {e}")
    brain_agent = None

# 4. Scoring Agent (Critical for Report)
try:
    scoring_agent = ScoringEngine()
    logger.info("✅ Scoring Engine initialized.")
except Exception as e:
    logger.error(f"❌ Scoring Engine failed: {e}")
    scoring_agent = None

# 5. Non-Verbal Agent (Video - Optional)
try:
    video_agent = VideoAnalyzer()
    logger.info("✅ Video Agent initialized.")
except Exception as e:
    logger.error(f"❌ Video Agent failed: {e}")
    video_agent = None

# 5. Vocal Agent (Optional)
vocal_agent = None
if VOCAL_AGENT_AVAILABLE:
    try:
        vocal_agent = VocalAnalyzer()
        logger.info("✅ Vocal Agent initialized.")
    except Exception as e:
        logger.warning(f"⚠️ Vocal Agent failed to init (Optional): {e}")
        VOCAL_AGENT_AVAILABLE = False
else:
    logger.warning("⚠️ Vocal Agent skipped (Librosa missing).")

# --- FastAPI App ---
app = FastAPI(title="AI Interviewer Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Models ---
class InterviewResponse(BaseModel):
    transcript: str
    ai_response_text: str
    ai_audio_path: str

# --- Endpoints ---

@app.get("/health")
def health_check():
    return {"status": "active", "tts": "online", "verbal": "online"}

@app.post("/process_audio")
async def process_audio(file: UploadFile = File(...)):
    """
    Main Interview Loop:
    1. Receive User Audio Blob
    2. Save to Temp
    3. Verbal Agent: Transcribe
    4. Brain Agent: Generate Response (Mocked for now)
    5. TTS Agent: Speak Response
    6. Return: Transcript + AI Text + Audio URL/Path
    """

    session_id = str(uuid.uuid4())
    print(f"\n🔴 REQUEST RECEIVED: Session {session_id}")
    user_audio_path = os.path.join(TEMP_AUDIO_DIR, f"user_{session_id}.wav")
    
    try:
        # 1. Save User Audio
        with open(user_audio_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 2. Transcribe (Verbal Agent)
        transcript = verbal_agent.transcribe(user_audio_path)
        logger.info(f"User Transcribed: {transcript}")

        # 2.5 Analyze Tone (Vocal Agent)
        vocal_metrics = {}
        if VOCAL_AGENT_AVAILABLE and vocal_agent:
            vocal_metrics = vocal_agent.analyze(user_audio_path)
            logger.info(f"Vocal Metrics: {vocal_metrics}")

        # 2.6 Analyze Video (Non-Verbal Agent)
        video_score = 0.0
        # TODO: Accept 'frame' in UploadFile or separate field
        # For now, we mock it or check if a file named 'frame.jpg' was uploaded
        # video_metrics = video_agent.analyze_frame(frame_path)
        
        # 2.7 Scoring Engine
        final_score = {}
        if scoring_agent:
            final_score = scoring_agent.calculate_score(
                verbal_score=75.0, # Dummy until verbal_agent.score() is active
                vocal_metrics=vocal_metrics,
                non_verbal_score=video_score
            )

        # 3. Generate AI Response (Brain Agent)
        ai_text = brain_agent.get_response(transcript)
        logger.info(f"AI Response: {ai_text}")
            
        # 4. Generate AI Audio (TTS Agent)
        ai_audio_abs_path = tts_agent.speak(ai_text)
        
        if not ai_audio_abs_path:
            raise HTTPException(status_code=500, detail="TTS Generation failed")

        ai_audio_filename = os.path.basename(ai_audio_abs_path)
            
        return {
            "transcript": transcript,
            "ai_response_text": ai_text,
            "ai_audio_filename": ai_audio_filename,
            "vocal_metrics": vocal_metrics,
            "interview_score": final_score
        }

    except Exception as e:
        logger.error(f"Processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Optional: Cleanup user input file
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
