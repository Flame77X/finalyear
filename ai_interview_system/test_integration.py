import requests
import wave
import os
import json
import time

URL = "http://localhost:8000/process_audio"
AUDIO_FILE = "test_audio_input.wav"

def create_dummy_audio():
    # Create 1 second of silence/tone
    with wave.open(AUDIO_FILE, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(16000)
        f.writeframes(b'\x00\x00' * 16000) # Silence

def test_integration():
    print("--- 🧪 SYSTEM INTEGRATION TEST ---")
    create_dummy_audio()
    
    try:
        print(f"1. Sending Audio to {URL}...")
        start = time.time()
        with open(AUDIO_FILE, "rb") as f:
            files = {"file": (AUDIO_FILE, f, "audio/wav")}
            response = requests.post(URL, files=files, timeout=60)
            
        duration = time.time() - start
        print(f"   ⏱️ Response time: {duration:.2f}s")
        
        if response.status_code != 200:
            print(f"❌ FAILED. Status: {response.status_code}")
            print(f"Error: {response.text}")
            return

        data = response.json()
        print("\n--- 📊 AGENT REPORT ---")
        
        # 1. Verbal
        print(f"✅ Verbal Agent: Transcript = '{data.get('transcript')}'")
        
        # 2. Vocal
        vm = data.get('vocal_metrics', {})
        if vm and 'confidence_score' in vm:
            print(f"✅ Vocal Agent: Score={vm['confidence_score']:.1f}% | Pitch={vm.get('avg_pitch'):.1f}Hz")
        else:
            print("⚠️ Vocal Agent: No metrics returned (Check FFmpeg?)")

        # 3. Brain
        ai_resp = data.get('ai_response_text', "")
        if ai_resp:
            print(f"✅ Brain Agent: Response = \"{ai_resp[:50]}...\"")
        else:
            print("❌ Brain Agent: No response text!")

        # 4. Scoring
        score = data.get('interview_score', {})
        if score:
            grand_total = score.get('grand_total')
            print(f"✅ Scoring Engine: Grand Total = {grand_total}/200")
            print(f"   Breakdown: {json.dumps(score.get('breakdown'), indent=2)}")
        else:
            print("❌ Scoring Engine: No score returned!")
            
        # 5. TTS
        audio_file = data.get('ai_audio_filename')
        if audio_file:
             print(f"✅ TTS Agent: Audio generated -> {audio_file}")
        else:
             print("❌ TTS Agent: No audio file returned!")

        print("\n--- 🏁 TEST COMPLETE ---")

    except Exception as e:
        print(f"❌ TEST CRASHED: {e}")
    finally:
        if os.path.exists(AUDIO_FILE):
             os.remove(AUDIO_FILE)

if __name__ == "__main__":
    test_integration()
