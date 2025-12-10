import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from verbal_agent.verbal_analyzer import VerbalAnalyzer

def transcribe_file():
    audio_path = r"C:\Users\rahul\Downloads\4d429da5-8db8-45fe-83d0-1b295ba841e3.wav"
    
    print("Initializing Verbal Agent...")
    try:
        agent = VerbalAnalyzer(model_size="base.en")
        print("Agent initialized.")
        
        if os.path.exists(audio_path):
            print(f"Transcribing: {audio_path}")
            text = agent.transcribe(audio_path)
            print("-" * 50)
            print("TRANSCRIPTION RESULT:")
            print(text)
            print("-" * 50)
        else:
            print(f"File not found: {audio_path}")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    transcribe_file()
