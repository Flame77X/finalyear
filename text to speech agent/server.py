from fastapi import FastAPI, UploadFile, Body, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import io
import os
from tts_wrapper import PiperTTSEngine

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PIPER_EXE = os.path.join(BASE_DIR, "piper", "piper.exe")
MODEL_PATH = os.path.join(BASE_DIR, "models", "en_US-lessac-medium.onnx")

# Initialize Engine
if not os.path.exists(PIPER_EXE) or not os.path.exists(MODEL_PATH):
    raise RuntimeError("Piper or Model not found! Check paths.")

tts_engine = PiperTTSEngine(PIPER_EXE, MODEL_PATH)

app = FastAPI(title="Local Piper TTS Agent")

# Enable CORS for React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define Request Model
class TTSRequest(BaseModel):
    text: str

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open(os.path.join(BASE_DIR, "templates", "index.html"), "r") as f:
        return f.read()

@app.post("/tts")
async def synthesize(request: TTSRequest):
    """
    Synthesizes text and streams back WAV audio.
    """
    text = request.text
    if not text:
        return {"error": "No text provided"}
    
    print(f"Synthesizing: {text}")
    
    # Generate audio bytes
    audio_data = tts_engine.synthesize(text)
    
    if not audio_data:
        return {"error": "Synthesis failed"}
    
    # Stream response
    return StreamingResponse(
        io.BytesIO(audio_data), 
        media_type="audio/wav"
    )

if __name__ == "__main__":
    import uvicorn
    # Listen on all interfaces so other devices on local network can usage it
    uvicorn.run(app, host="0.0.0.0", port=8000)
