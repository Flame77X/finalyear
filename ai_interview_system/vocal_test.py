import os
import sys

print("--- DIAGNOSTIC START ---")
print(f"Python: {sys.version}")

try:
    print("1. Importing Librosa...")
    import librosa
    print("✅ Librosa imported.")
except ImportError as e:
    print(f"❌ Librosa Import Failed: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected Import Error: {e}")
    sys.exit(1)

try:
    print("2. Importing Numba/LLVMLite...")
    import numba
    import llvmlite
    print(f"✅ Numba {numba.__version__} / LLVMLite {llvmlite.__version__}")
except ImportError as e:
    print(f"⚠️ Numba/LLVM Warning (Librosa might be slow/broken): {e}")

try:
    print("3. Checking VocalAnalyzer Logic...")
    # Fix import for running inside the directory
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from vocal_agent.vocal_analyzer import VocalAnalyzer
    agent = VocalAnalyzer()
    print("✅ VocalAnalyzer instantiated.")
    
    # Create dummy wav
    import wave
    dummy_wav = "test_tone.wav"
    with wave.open(dummy_wav, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(16000)
        f.writeframes(b'\x00\x00' * 16000) # 1 sec silence
        
    print(f"4. Analyzing dummy file: {dummy_wav}")
    metrics = agent.analyze(dummy_wav)
    print(f"✅ Analysis Result: {metrics}")
    
    os.remove(dummy_wav)
    print("--- DIAGNOSTIC SUCCESS ---")

except Exception as e:
    print(f"❌ RUNTIME ERROR: {e}")
    import traceback
    traceback.print_exc()
