import asyncio
import json
import base64
import time
import cv2
import numpy as np
import os
import io
import soundfile as sf
import logging
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv

# ===== LOAD ENVIRONMENT =====
load_dotenv()

# ===== LOGGING =====
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== IMPORTS =====
# Import Lazy Loader (created in agents/lazy_loader.py)
from agents.lazy_loader import (
    lazy_deepface,
    lazy_librosa,
    lazy_keybert,
)

# Project Imports
from brain_agent.orchestrator import BrainAgent
from verbal_agent.verbal_analyzer import VerbalAnalyzer
from scoring_agent.engine import ScoringEngine as ScoreAgent
from non_verbal_agent.video_analyzer import NonVerbalAgent
from vocal_agent.vocal_analyzer import VocalAnalyzer
from scoring_agent.keyword_scorer import KeywordScorer
from report_generator import generate_pdf_report
from email_service import send_email_with_report
from store import InterviewStore
from resume_parser import ResumeParser

# ===== GLOBAL STATE =====
store = None
ml_executor = None

# ===== LIFESPAN MANAGER =====
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages application startup and shutdown lifecycle.
    Ensures Database and Executors are properly initialized/cleaned up.
    """
    global store, ml_executor
    
    logger.info("🚀 Starting Interview Coaching System...")
    
    # 1. Initialize Thread Pool
    ml_executor = ThreadPoolExecutor(max_workers=3, thread_name_prefix="ml_worker_")
    
    # 2. Initialize Database
    try:
        logger.info("📦 Connecting to Database...")
        store = InterviewStore()
        # Simple check if DB is online (InterviewStore handles timeouts internally)
        if store.db is not None:
             logger.info("✅ Database Online")
        else:
             logger.warning("⚠️ Database Offline (Running in detached mode)")
    except Exception as e:
        logger.error(f"❌ Database Initialization Failed: {e}")
    
    yield # Server is running
    
    # 3. Shutdown
    logger.info("🛑 Shutting down...")
    if ml_executor:
        ml_executor.shutdown(wait=True)
    logger.info("👋 Goodbye!")

# ===== APP INITIALIZATION =====
app = FastAPI(title="Interview Coaching System", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for dev; restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== LAZY AGENT INSTANCES & SESSION STATE =====

# Global Singletons for Stateless Agents
_non_verbal_agent = None
_vocal_analyzer = None
_keyword_scorer = None
_verbal_analyzer = None

def get_non_verbal_agent() -> NonVerbalAgent:
    """Lazy-initialized non-verbal agent"""
    global _non_verbal_agent
    if _non_verbal_agent is None:
        _non_verbal_agent = NonVerbalAgent()
    return _non_verbal_agent

def get_vocal_analyzer() -> VocalAnalyzer:
    """Lazy-initialized vocal analyzer"""
    global _vocal_analyzer
    if _vocal_analyzer is None:
        _vocal_analyzer = VocalAnalyzer()
    return _vocal_analyzer

def get_keyword_scorer() -> KeywordScorer:
    """Lazy-initialized keyword scorer"""
    global _keyword_scorer
    if _keyword_scorer is None:
        _keyword_scorer = KeywordScorer()
    return _keyword_scorer

def get_verbal_analyzer() -> VerbalAnalyzer:
    global _verbal_analyzer
    if _verbal_analyzer is None:
        _verbal_analyzer = VerbalAnalyzer()
    return _verbal_analyzer

# ===== WEBSOCKET CONNECTION MANAGER =====

class ConnectionManager:
    """Manage active WebSocket connections"""
    def __init__(self):
        self.active_connections: dict = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client {client_id} connected")
    
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        logger.info(f"Client {client_id} disconnected")
    
    async def send_personal_message(self, message: str, client_id: str):
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(message)
            except Exception as e:
                logger.error(f"Error sending message: {e}")

manager = ConnectionManager()

# ===== REST ENDPOINTS =====

@app.post("/register_candidate")
async def register_candidate(
    name: str = Form(...),
    email: str = Form(...),
    branch: str = Form(...),
    resume: UploadFile = File(None)
):
    print(f"Registering candidate: {name}, {email}, {branch}")
    resume_text = ""
    if resume:
        try:
            content = await resume.read()
            resume_text = ResumeParser.extract_text(content, resume.filename)
            print(f"Resume text extracted: {len(resume_text)} chars")
        except Exception as e:
            print(f"Resume parsing failed: {e}")
            
    candidate_data = {
        "name": name, 
        "email": email, 
        "branch": branch,
        "resume_text": resume_text
    }
    candidate_id = await store.save_candidate(candidate_data)
    
    return {"message": "Registration Successful", "candidate_id": candidate_id}

@app.post("/start_session")
async def start_session(candidate_id: str = None):
    # This endpoint now explicitly creates a BrainAgent session
    print(f"Start Session requested for {candidate_id}")
    return {"status": "started"}

@app.post("/process_audio")
async def process_audio(file: UploadFile = File(...)):
    # Legacy endpoint support
    temp_filename = f"temp_{file.filename}"
    try:
        content = await file.read()
        await asyncio.get_running_loop().run_in_executor(None, lambda: open(temp_filename, "wb").write(content))
        
        agent = get_verbal_analyzer()
        user_text = agent.transcribe(temp_filename)
        return {"text": user_text, "status": "success"}
    except Exception as e:
        return {"response": "Error processing audio", "error": str(e)}
    finally:
        if os.path.exists(temp_filename):
            try: os.remove(temp_filename)
            except: pass

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    current_workers = ml_executor._max_workers if ml_executor else 0
    return {
        "status": "healthy",
        "ml_executor_workers": current_workers,
        "active_connections": len(manager.active_connections)
    }

# ===== WEBSOCKET ENDPOINT =====

@app.websocket("/ws/interview")
async def websocket_endpoint(websocket: WebSocket):
    """
    Main WebSocket endpoint for real-time interview processing
    Handles video frames, audio chunks, and interview events
    """
    client_id = f"client_{id(websocket)}"
    await manager.connect(websocket, client_id)
    
    # Brain Agent is stateful, need new instance per user
    brain_agent = BrainAgent(resume_text="") 
    
    # Aggregation Buffers
    transcript_buffer = []
    non_verbal_scores = []
    vocal_scores = []
    keyword_results = []
    
    # Audio Buffer for Transcription
    # Changed SILENCE_LIMIT to 3 (Approx 1.5s latency) for more natural pausing
    audio_buffer_np = np.array([], dtype=np.float32)
    silence_chunks = 0
    IS_SPEAKING_THRESHOLD = -40.0 # dB
    SILENCE_LIMIT = 3 
    
    # Initial Greeting
    try:
        initial_msg = brain_agent.get_response("start")
        await websocket.send_json({"type": "text", "ai_text": initial_msg})
    except Exception as e:
        logger.error(f"Brain init error: {e}")

    try:
        while True:
            try:
                raw_data = await websocket.receive_text()
                data = json.loads(raw_data)
            except json.JSONDecodeError:
                # Robust error handling for bad JSON
                logger.warning(f"Client {client_id}: Invalid JSON received")
                continue
            except WebSocketDisconnect:
                logger.info(f"Client {client_id} disconnected normally.")
                break
            except Exception as e:
                logger.error(f"Socket Receive Error: {e}")
                break
                
            data_type = data.get("type", "text")
            
            # ===== VIDEO FRAME PROCESSING =====
            if data_type == "video_frame":
                frame_base64 = data.get("frame")
                if frame_base64:
                    try:
                        # Decode base64 frame
                        frame_bytes = base64.b64decode(frame_base64)
                        frame_array = np.frombuffer(frame_bytes, dtype=np.uint8)
                        frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
                        
                        # ✅ RUN NON-VERBAL ANALYSIS IN THREAD POOL
                        loop = asyncio.get_event_loop()
                        nv_result = await loop.run_in_executor(
                            ml_executor,
                            get_non_verbal_agent().analyze_frame,
                            frame
                        )
                        
                        if nv_result.get('success'):
                            # Ensure we append a float, not a dict
                            score = nv_result.get('confidence_score', 0)
                            if score is not None:
                                non_verbal_scores.append(float(score))
                        
                        # Send results back to client
                        await websocket.send_json({
                            "type": "non_verbal_analysis",
                            "confidence_score": nv_result.get('confidence_score', 0),
                            "emotions": nv_result.get('emotions', {}),
                            "facial_expression": nv_result.get('facial_expression', ''),
                            "eye_contact": round(nv_result.get('eye_contact', 0), 2),
                            "posture_score": round(nv_result.get('posture_score', 0), 2),
                            "aggregate_score": round(nv_result.get('aggregate_score', 0), 2),
                            "success": nv_result.get('success', False)
                        })
                    
                    except Exception as e:
                        logger.error(f"Video frame processing error: {str(e)}")
            
            # ===== AUDIO CHUNK PROCESSING =====
            elif data_type == "audio_chunk":
                audio_base64 = data.get("audio")
                if audio_base64:
                    try:
                        # Decode audio
                        audio_bytes = base64.b64decode(audio_base64)
                        
                        # 1. Run vocal analysis in thread pool
                        loop = asyncio.get_event_loop()
                        v_result = await loop.run_in_executor(
                            ml_executor,
                            get_vocal_analyzer().analyze_audio,
                            audio_bytes
                        )
                        
                        if v_result.get('success'):
                            score = v_result.get('confidence_score', 0)
                            if score is not None:
                                vocal_scores.append(float(score))
                        
                        # Send Vocal results
                        await websocket.send_json({
                            "type": "audio_analysis",
                            "pitch_hz": v_result.get('pitch_hz', 0),
                            "confidence_score": round(v_result.get('confidence_score', 0), 2),
                            "loudness_db": v_result.get('loudness_db', 0),
                            "speech_rate": v_result.get('speech_rate', 0),
                            "success": v_result.get('success', False)
                        })

                        # 2. Accumulate Audio for Transcription
                        try:
                            # Read raw samples using soundfile (robust to webm chunks)
                            y_chunk, sr_chunk = sf.read(io.BytesIO(audio_bytes))
                            if len(y_chunk) > 0:
                                audio_buffer_np = np.append(audio_buffer_np, y_chunk)
                                
                                # Silence Detection Logic
                                loudness = v_result.get('loudness_db', -80.0)
                                if loudness > IS_SPEAKING_THRESHOLD:
                                    silence_chunks = 0 # Reset silence
                                else:
                                    silence_chunks += 1
                                
                                # TRIGGER TRANSCRIPTION if silence persists and we have enough audio
                                if silence_chunks >= SILENCE_LIMIT and len(audio_buffer_np) > 0:
                                    
                                    # Save buffer to temp file
                                    temp_filename = f"temp_transcribe_{client_id}.wav"
                                    sf.write(temp_filename, audio_buffer_np, samplerate=sr_chunk)
                                    
                                    # Clear buffer immediately to avoid double processing
                                    audio_buffer_np = np.array([], dtype=np.float32)
                                    silence_chunks = 0

                                    # Transcribe
                                    transcribed_text = await loop.run_in_executor(
                                        ml_executor,
                                        get_verbal_analyzer().transcribe,
                                        temp_filename
                                    )
                                    
                                    # Cleanup temp file
                                    try: os.remove(temp_filename)
                                    except: pass
                                    
                                    if transcribed_text and len(transcribed_text.strip()) > 1:
                                        print(f"User Said: {transcribed_text}")
                                        
                                        # Send Transcript Update to UI
                                        await websocket.send_json({
                                            "type": "transcript",
                                            "text": transcribed_text,
                                            "sender": "user"
                                        })
                                        
                                        # 3. GET BRAIN RESPONSE
                                        # Wrapped in Try-Except for Safety
                                        try:
                                            ai_text = brain_agent.get_response(transcribed_text)
                                            # Send AI Response to UI
                                            await websocket.send_json({
                                                "type": "text", 
                                                "ai_text": ai_text
                                            })
                                        except Exception as e:
                                            logger.error(f"Brain Agent Error: {e}")
                                            await websocket.send_json({
                                                "type": "text", 
                                                "ai_text": f"Error thinking: {str(e)}"
                                            })

                        except Exception as inner_e:
                            logger.error(f"Buffering/Transcription error: {inner_e}")

                    except Exception as e:
                        logger.error(f"Audio processing error: {str(e)}")

            # ===== TRANSCRIPT / TEXT PROCESSING =====
            elif "text" in data or data_type == "transcript":
                user_text = data.get("text", "")
                if user_text:
                    transcript_buffer.append(user_text)
                    
                    # 1. Get Brain Response
                    try:
                        ai_text = brain_agent.get_response(user_text)
                        await websocket.send_json({"type": "text", "ai_text": ai_text})
                    except Exception as e:
                        logger.error(f"Brain Text Error: {e}")
                    
                    # 2. Keyword Analysis (Async) - Only if length sufficient
                    full_transcript = " ".join(transcript_buffer)
                    if len(full_transcript) > 50:
                        try:
                            loop = asyncio.get_event_loop()
                            kw_result = await loop.run_in_executor(
                                ml_executor,
                                get_keyword_scorer().extract_and_score,
                                full_transcript,
                                "cse" 
                            )
                            
                            keyword_results.append(kw_result)
                            
                            await websocket.send_json({
                                "type": "keyword_analysis",
                                "keyword_score": kw_result.get('keyword_score', 0),
                                "top_keywords": kw_result.get('matched_keywords', []),
                                "success": kw_result.get('success', False)
                            })
                        except Exception as e:
                            logger.error(f"Keyword extraction error: {e}")

            # ===== INTERVIEW EVENT HANDLING =====
            elif data_type == "interview_event":
                event = data.get("event")
                
                if event == "interview_started":
                    logger.info(f"Interview started for {client_id}")
                    await websocket.send_json({"type": "status", "message": "Interview Started"})
                
                elif event == "interview_ended":
                    logger.info(f"Interview ended for {client_id}")
                    
                    # Aggregate Final Scores
                    mean_nv = np.mean(non_verbal_scores) if non_verbal_scores else 0.0
                    if mean_nv <= 1.0: mean_nv *= 100 # Adjust scale if needed
                    
                    mean_vocal = np.mean(vocal_scores) if vocal_scores else 0.0
                    
                    mean_keyword = 0.0
                    if keyword_results:
                        mean_keyword = keyword_results[-1].get('keyword_score', 0)
                    
                    final_score = (mean_nv + mean_vocal + mean_keyword) / 3

                    # Send Final Score
                    await websocket.send_json({
                        "type": "final_score",
                        "scores": {
                            "non_verbal_score": round(mean_nv, 1), 
                            "vocal_score": round(mean_vocal, 1),
                            "keyword_score": round(mean_keyword, 1),
                            "final_score": round(final_score, 1) 
                        }
                    })

    except WebSocketDisconnect:
        manager.disconnect(client_id)
    
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")

# ===== MAIN EXECUTION =====
if __name__ == "__main__":
    import uvicorn
    # Use lifespan instead of on_event
    uvicorn.run(app, host="0.0.0.0", port=8000)
