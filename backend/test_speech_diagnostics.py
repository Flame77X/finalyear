import sys
import os
import asyncio

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from verbal_agent.verbal_analyzer import VerbalAnalyzer

def test_speech_system():
    print("\n" + "="*50)
    print("🔍 DIAGNOSTIC: SPEECH RECOGNITION SYSTEM")
    print("="*50 + "\n")

    # 1. Check FFmpeg
    print("[1] Checking FFmpeg...")
    exit_code = os.system("ffmpeg -version >nul 2>&1")
    if exit_code == 0:
        print("✅ FFmpeg is installed and accessible.")
    else:
        print("❌ FFmpeg NOT found. Please install FFmpeg and add to PATH.")
        return

    # 2. Check Model Load
    print("\n[2] Initializing Whisper Model (This may take time)...")
    try:
        agent = VerbalAnalyzer(model_size="base.en")
        print("✅ Model Init Successful")
    except Exception as e:
        print(f"❌ Model Init Failed: {e}")
        return

    # 3. Create Dummy Audio (Requires numpy/soundfile, which you likely have)
    print("\n[3] Creating Test Audio File...")
    try:
        import numpy as np
        import soundfile as sf
        
        # Generate 2 seconds of silence/noise just to test file I/O and processing
        # Note: Silence might result in empty transcript, which is expected behavior for VAD
        # but here we just want to see if it CRASHES.
        sr = 16000
        duration = 1.0
        audio_data = np.random.uniform(-0.1, 0.1, int(sr * duration)).astype(np.float32)
        
        test_file = "diagnostic_test.wav"
        sf.write(test_file, audio_data, sr)
        print(f"✅ Created {test_file}")
        
    except Exception as e:
        print(f"❌ Failed to create test audio: {e}")
        return

    # 4. Transcribe Test
    print("\n[4] Running Transcription on Test File...")
    try:
        text = agent.transcribe(test_file)
        print(f"✅ Transcription Run Complete (Expected Gibberish/Empty): '{text}'")
    except Exception as e:
        print(f"❌ Transcription Crashed: {e}")
    finally:
        if os.path.exists(test_file):
            try: os.remove(test_file)
            except: pass

    print("\n" + "="*50)
    print("✨ DIAGNOSTIC COMPLETE")
    print("="*50 + "\n")

if __name__ == "__main__":
    test_speech_system()
