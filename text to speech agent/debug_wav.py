import wave
import os
import sys
from tts_wrapper import PiperTTSEngine

def check_wav():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    piper_exe = os.path.join(current_dir, "piper", "piper.exe")
    model_path = os.path.join(current_dir, "models", "en_US-lessac-medium.onnx")
    
    tts = PiperTTSEngine(piper_exe, model_path)
    audio_data = tts.synthesize("Test")
    
    if not audio_data:
        print("No audio generated")
        return

    # Write to a test file
    test_file = "debug_audio.wav"
    with open(test_file, "wb") as f:
        f.write(audio_data)

    try:
        with wave.open(test_file, "rb") as wf:
            print(f"Channels: {wf.getnchannels()}")
            print(f"Sample Width: {wf.getsampwidth()} bytes")
            print(f"Frame Rate: {wf.getframerate()} Hz")
            print(f"Frames: {wf.getnframes()}")
            print(f"Duration: {wf.getnframes() / wf.getframerate():.2f} sec")
    except wave.Error as e:
        print(f"WAV Error: {e}")
        # If it's not a valid WAV, maybe it's raw PCM?
        print("File might be raw PCM or corrupted.")

if __name__ == "__main__":
    check_wav()
