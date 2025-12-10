import os
import sys
from tts_wrapper import PiperTTSEngine
from audio_player import AudioPlayer

def main():
    # Paths (adjust as needed based on where you run this from)
    # Assuming running from 'text to speech agent' directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    piper_exe = os.path.join(current_dir, "piper", "piper.exe")
    model_path = os.path.join(current_dir, "models", "en_US-lessac-medium.onnx")
    
    print(f"Checking paths:\nPiper: {piper_exe}\nModel: {model_path}")
    
    if not os.path.exists(piper_exe):
        print("Error: Piper executable not found. Did the zip extract to a 'piper' folder?")
        return
    if not os.path.exists(model_path):
        print("Error: Model file not found.")
        return

    print("Initializing Engine...")
    tts = PiperTTSEngine(piper_exe, model_path)
    player = AudioPlayer()
    
    test_text = "Hello! I am your AI assistant. This is a test of the local text to speech system."
    print(f"Synthesizing: '{test_text}'")
    
    audio_data = tts.synthesize(test_text)
    
    if audio_data:
        print(f"Audio generated ({len(audio_data)} bytes). Playing...")
        player.play_audio(audio_data)
        print("Done.")
    else:
        print("Synthesis failed.")

if __name__ == "__main__":
    main()
