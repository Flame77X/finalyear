# AI Interviewer System - Architecture & Troubleshooting

## System Overview

This system is designed to simulate a job interview. It captures a candidate's spoken answer, transcribes it into text, analyzes the vocal tone for confidence, determines an intelligent follow-up response, and then speaks that response back to the candidate. It uses a **FastAPI** backend to coordinate four specialized "agents."

### 1. Backend Server (`server.py`)
**Role:** The Central Controller.
This file is the entry point. It sets up the web server, initializes all the AI agents, and defines the API endpoint that the frontend (your React app) talks to.

* **Initialization:**
    * It imports the agent classes (`TTSEngine`, `VerbalAnalyzer`, `BrainAgent`, `VocalAnalyzer`).
    * It creates instances of these agents (`tts_agent`, `verbal_agent`, etc.) when the server starts. This is efficient because loading AI models takes time, so we do it once at the beginning.
    * It checks if the Vocal Agent can be loaded (since `librosa` can sometimes be tricky to install) and sets a flag `VOCAL_AGENT_AVAILABLE` so the server doesn't crash if it's missing.

* **`@app.post("/process_audio")` Endpoint:**
    This is the main function that runs every time the user finishes speaking.
    1.  **Receive Audio:** It accepts an audio file (`UploadFile`) from the frontend.
    2.  **Save Temp File:** It saves this audio as a temporary file (e.g., `user_123.wav`) so the agents can read it.
    3.  **Step 1 (Verbal):** It passes the file to the `verbal_agent` to get a text transcript.
    4.  **Step 2 (Vocal):** It passes the file to the `vocal_agent` to get confidence metrics (pitch, energy, etc.).
    5.  **Step 3 (Brain):** It sends the *transcript* to the `brain_agent`. The brain decides what to say next (e.g., "That's great. Tell me about your strengths.").
    6.  **Step 4 (TTS):** It sends the *AI's response text* to the `tts_agent`. The TTS agent generates a new audio file of the AI speaking.
    7.  **Return:** It sends a JSON response back to the frontend containing the transcript, the AI's text, the filename of the AI's audio, and the vocal metrics.

---

### 2. Brain Agent (`brain_agent/orchestrator.py`)
**Role:** The Logic & Reasoning.
This agent acts like the interviewer's brain. It doesn't "hear" audio; it reads text and decides what to say.

* **State Management:** It remembers where we are in the interview using `self.interview_state` (e.g., "intro", "questions", "finished").
* **Question Bank:** It has a list of pre-set questions.
* **`get_response(user_text)`:**
    * **Text Cleaning:** It removes punctuation and makes everything lowercase so "Hello!" matches "hello".
    * **Intro Phase:** If the state is "intro", it looks for greetings ("hi", "hello") or introductions ("my name is..."). If it finds an introduction, it switches the state to "questions" and asks the first question.
    * **Questions Phase:** It stores the user's answer to the *previous* question, picks a random acknowledgement (e.g., "I see."), and then asks the *next* question in the list.
    * **Finished Phase:** Once all questions are asked, it says goodbye.

---

### 3. Verbal Agent (`verbal_agent/verbal_analyzer.py`)
**Role:** The Ear (Speech-to-Text).
This agent's job is to convert sound into text and check if the answer is accurate.

* **Models:**
    * **Whisper:** A powerful model from OpenAI that converts speech to text. It is loaded as `self.stt_model`.
    * **SentenceTransformer:** A model that turns text into numbers (embeddings) to compare meanings.
* **`transcribe(audio_path)`:** It runs the Whisper model on the audio file and returns the text string.
* **`score_answer(user_text, correct_answer)`:** It compares the user's spoken answer with a "correct" answer key. It calculates a "cosine similarity" score (0 to 100). If the meanings are similar, the score is high, even if the exact words are different.

---

### 4. Vocal Agent (`vocal_agent/vocal_analyzer.py`)
**Role:** The Tone Analyst.
This agent ignores *what* was said and looks at *how* it was said.

* **Library:** It uses `librosa`, a standard library for audio analysis.
* **`analyze(audio_path)`:**
    * **Pitch:** It detects the pitch (frequency) of the voice. A varied pitch is good (expressive), while a flat pitch is robotic.
    * **Energy:** It measures volume (RMS). Low energy might mean shyness.
    * **Tempo:** It estimates the speech rate (beats per minute). Too fast might mean nervousness.
    * **Scoring:** It implements a simple rule-based algorithm: start with a base score of 50, and add points if the volume, tempo, and pitch are within "healthy" ranges.

---

### 5. TTS Agent (`tts_agent/tts_engine.py`)
**Role:** The Voice (Text-to-Speech).
This agent gives the AI a voice.

* **Piper TTS:** It uses a tool called Piper, which is a fast, offline text-to-speech engine. It runs as a separate command-line process.
* **`speak(text)`:**
    * It creates a unique filename for the new audio.
    * It constructs a system command that pipes the text into the Piper executable.
    * It runs the command using `subprocess`.
    * It creates a `.wav` file that the frontend can play.
* **Volume Scaling:** It includes a helper function `_scale_volume` to lower the volume of the generated speech (multiplying by 0.2), as raw TTS can sometimes be very loud.

---

## Codebase Analysis & Troubleshooting

### 1. Backend Server (`server.py`)

* **Potential Error:** `RuntimeError: Agent initialization failed.`
    * **Context:** The server attempts to initialize all agents on startup. If any dependency (like `librosa` or `ffmpeg` for Whisper) is missing or if a model file is not found, the entire server will crash.
    * **Solution:** Wrap each agent initialization in its own `try-except` block. This allows the server to start even if a non-critical agent (like `VocalAnalyzer`) fails, ensuring basic functionality remains available. Log the specific error for each agent to aid debugging.

* **Potential Error:** `HTTPException: 500` during `process_audio`
    * **Context:** The `process_audio` endpoint is complex, involving file I/O, transcription, AI inference, and TTS generation. A failure at any step (e.g., corrupt audio file upload) triggers a generic 500 error.
    * **Solution:** Implement more granular error handling within the endpoint. Check for valid file types before processing. Use specific exception types (e.g., `TranscriptionError`, `ModelInferenceError`) to provide more informative error messages to the client. Ensure that temporary files are cleaned up in a `finally` block even if an error occurs.

### 2. Brain Agent (`brain_agent/orchestrator.py`)

* **Potential Error:** Logic Flaw in State Management
    * **Context:** The current logic relies on simple keyword matching (`if "hello" in words`) to transition states. If a user's response is complex or doesn't contain specific keywords, the state might get stuck or loop unintentionally.
    * **Solution:** Enhance the state logic. Instead of strict keyword matching, consider using a lightweight Intent Classification model (or even regex patterns) to better understand user intent. Implement a fallback mechanism or a "default" state transition to keep the interview moving forward if the user's input is ambiguous.

* **Potential Error:** Unhandled Input
    * **Context:** If the user provides empty input or unintelligible speech (resulting in an empty transcription), the agent might not return a valid response string.
    * **Solution:** Add a check for empty input strings at the beginning of `get_response`. If the input is empty, return a prompt asking the user to repeat themselves or speak up.

### 3. Verbal Agent (`verbal_agent/verbal_analyzer.py`)

* **Potential Error:** `FileNotFoundError` or `FFmpeg` issues
    * **Context:** Whisper relies heavily on `ffmpeg` being installed and accessible in the system path for audio processing. If it's missing, transcription will fail immediately.
    * **Solution:** Add a check during initialization to verify that `ffmpeg` is installed. You can do this by attempting to run a simple `ffmpeg -version` command using `subprocess`. If it fails, log a critical warning advising the user to install `ffmpeg`.

* **Potential Error:** Model Loading Latency
    * **Context:** Loading the Whisper model (`base.en`) and the SentenceTransformer model can take significant time and memory. This happens on every server restart.
    * **Solution:** While not an error per se, it affects startup time. Consider loading models asynchronously or implementing a "warm-up" routine. For production, ensure the server has sufficient RAM (at least 4-8GB) to hold both models in memory concurrently.

### 4. Vocal Agent (`vocal_agent/vocal_analyzer.py`)

* **Potential Error:** `librosa.load` Failure (Sampling Rate)
    * **Context:** The code specifies `sr=16000`. If the uploaded audio file has a drastically different sampling rate or an incompatible codec, `librosa` might fail or return artifacts.
    * **Solution:** While `librosa` is robust, adding a check to ensure the file is a valid audio format *before* passing it to `librosa` is good practice. Also, verify that the `target_sr` matches what `Whisper` expects if you plan to share audio processing steps.

* **Potential Error:** Division by Zero or `NaN` Results
    * **Context:** In `_get_empty_metrics` or during calculation (e.g., average pitch), if the audio is silent or very short, `len(selected_pitches)` could be 0.
    * **Solution:** The code already has checks (`if len(y) == 0`), which is good. Ensure that all division operations (like calculating averages) are protected against division by zero. The existing code seems to handle empty lists well, but explicit checks are safer.

### 5. TTS Agent (`tts_agent/tts_engine.py`)

* **Potential Error:** `FileNotFoundError: [WinError 2] The system cannot find the file specified`
    * **Context:** The code looks for `piper.exe` in a relative path. If the working directory of the `server.py` process is different from what `tts_engine.py` expects, it won't find the executable.
    * **Solution:** Ensure `piper_path` is resolved using an *absolute path* relative to the file location (`__file__`), which is correctly done in your code (`os.path.abspath`). However, double-check that the `piper` binary exists at that exact location after deployment or movement of files. On Linux/Mac, the binary is just `piper`, not `piper.exe`. Add logic to detect the OS and select the correct binary name.

* **Potential Error:** `subprocess.Popen` Deadlock or Blocking
    * **Context:** Using `process.communicate` is generally safe, but if the input text is extremely large, it could potentially hang.
    * **Solution:** For typical interview responses, this is unlikely. However, adding a `timeout` parameter to `communicate` is a robust safety measure to prevent the server from hanging indefinitely if the TTS engine freezes.

## Summary of Recommended Fixes

1.  **Robust Initialization:** Wrap individual agent setups in `server.py` with specific `try-except` blocks.
2.  **FFmpeg Check:** Explicitly verify `ffmpeg` availability for the Verbal Agent.
3.  **OS-Agnostic TTS:** Update `TTSEngine` to select `piper` (Linux/Mac) or `piper.exe` (Windows) dynamically.
4.  **Input Validation:** Add checks for empty strings/files in `server.py` and `BrainAgent`.
5.  **Path Safety:** Triple-check that all file paths (models, binaries, temp folders) are absolute paths to avoid "file not found" errors when running the server from different directories.
