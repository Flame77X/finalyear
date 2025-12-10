import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tts_agent.tts_engine import TTSEngine

def test_tts():
    print("Initializing TTS Engine...")
    try:
        engine = TTSEngine()
        print("Engine initialized.")
        
        text = "System restructure successful. TTS Agent is online."
        print(f"Synthesizing: '{text}'")
        
        output_path = engine.speak(text)
        
        if output_path and os.path.exists(output_path):
            print(f"SUCCESS: Audio generated at {output_path}")
            print(f"File size: {os.path.getsize(output_path)} bytes")
        else:
            print("FAILURE: Audio file not generated.")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_tts()
