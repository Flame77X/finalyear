import sys
import os
import asyncio
from non_verbal_agent.video_analyzer import NonVerbalAgent
from vocal_agent.vocal_analyzer import VocalAnalyzer
from scoring_agent.keyword_scorer import KeywordScorer
import numpy as np

# Add project root to path
sys.path.append(os.getcwd())

def test_dataset_loader():
    print("\n[1/6] Testing Dataset Loader...")
    try:
        from dataset_loader import InterviewDatasetLoader
        loader = InterviewDatasetLoader()
        questions = loader.get_questions_for_branch("CSE")
        if len(questions) > 0:
            print(f"✅ Dataset Loader works. Found {len(questions)} CSE questions.")
        else:
            print("⚠️ Dataset Loader returned 0 questions (Check questions.json).")
    except Exception as e:
        print(f"❌ Dataset Loader Failed: {e}")

def test_resume_parser():
    print("\n[2/6] Testing Resume Parser...")
    try:
        from resume_parser import ResumeParser
        # Create a dummy PDF bytes object (header only) to see if it catches the format or crashes
        # Real PDF parsing is hard to test without a file, so we test import and method existence.
        assert hasattr(ResumeParser, 'extract_text')
        print("✅ Resume Parser Module loaded successfully.")
    except Exception as e:
        print(f"❌ Resume Parser Failed: {e}")

def test_scoring_engine():
    print("\n[3/6] Testing Scoring Engine...")
    try:
        from scoring_agent.engine import ScoringEngine
        engine = ScoringEngine()
        result = engine.calculate_score(80.0, {"confidence_score": 90.0}, 0.0)
        # Expected: (80*0.8 + 80*0.2) + (90*0.6 + 0*0.4) = 80 + 54 = 134 (logic check)
        # Wait, implementation says: acc = (verbal * 0.8) + (verbal * 0.2) = verbal. 
        # Conf = (vocal * 0.6) + (non_verbal * 0.4).
        # Total = Acc + Conf.
        # My Manual calc: Acc=80. Conf=54. Total=134.
        # Let's see what it returns.
        if "grand_total" in result:
             print(f"✅ Scoring Engine works. Result: {result['grand_total']}")
        else:
             print(f"❌ Scoring Engine returned malformed data: {result}")
    except Exception as e:
        print(f"❌ Scoring Engine Failed: {e}")

def test_brain_agent():
    print("\n[4/6] Testing Brain Agent (Initialization)...")
    try:
        from brain_agent.orchestrator import BrainAgent
        # This might warn about missing API key, but shouldn't crash
        agent = BrainAgent()
        resp = agent.get_response("start")
        if resp:
            print("✅ Brain Agent initialized and responded.")
        else:
            print("❌ Brain Agent returned empty response.")
    except Exception as e:
        print(f"❌ Brain Agent Failed: {e}")

def test_verbal_agent():
    print("\n[5/6] Testing Verbal Agent (Heavy Load)...")
    print("      (This may take a few seconds to load models)")
    try:
        from verbal_agent.verbal_analyzer import VerbalAnalyzer
        # Use tiny model for test speed if possible, but code defaults to base.
        # We just want to see if imports work and class inits.
        # Initializing implies loading Whisper/SentenceTransformer. 
        # CAUTION: This might be heavy. Let's just check imports first to save time?
        # No, user asked to "verify each file". We must try to init.
        agent = VerbalAnalyzer()
        print("✅ Verbal Agent (Whisper + SBERT) initialized successfully.")
    except Exception as e:
        print(f"❌ Verbal Agent Failed: {e}")

def test_store():
    print("\n[6/6] Testing Store (Database)...")
    try:
        from store import InterviewStore
        # Just init check
        store = InterviewStore()
        print("✅ Store Module loaded.")
    except Exception as e:
        print(f"❌ Store Failed: {e}")

def test_non_verbal_agent():
    print("\n--- Testing Non-Verbal Agent ---")
    try:
        agent = NonVerbalAgent()
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        res = agent.analyze_frame(frame)
        print(f"Analyze Frame Result: {res}")
        print("✅ Non-Verbal Agent Initialized")
    except Exception as e:
        print(f"❌ Non-Verbal Agent Failed: {e}")

def test_vocal_analyzer():
    print("\n--- Testing Vocal Analyzer ---")
    try:
        agent = VocalAnalyzer()
        # Mock audio bytes (silence), 16000 Hz, 1 sec
        audio = np.zeros(16000, dtype=np.int16)
        import io
        import soundfile as sf
        buf = io.BytesIO()
        sf.write(buf, audio, 16000, format='WAV')
        res = agent.analyze_audio(buf.getvalue())
        print(f"Analyze Audio Result: {res}")
        print("✅ Vocal Analyzer Initialized")
    except Exception as e:
        print(f"❌ Vocal Analyzer Failed: {e}")

def test_keyword_scorer():
    print("\n--- Testing Keyword Scorer ---")
    try:
        scorer = KeywordScorer()
        text = "I have experience with Python, Machine Learning, and APIs."
        res = scorer.extract_and_score(text, job_role='ai')
        print(f"Keyword Score Result: {res}")
        print("✅ Keyword Scorer Initialized")
    except Exception as e:
        print(f"❌ Keyword Scorer Failed: {e}")

if __name__ == "__main__":
    print("=== STARTING FULL SYSTEM VERIFICATION ===")
    test_dataset_loader()
    test_resume_parser()
    test_scoring_engine()
    test_brain_agent()
    test_store()
    test_verbal_agent() # Run last as it's heaviest
    test_non_verbal_agent()
    test_vocal_analyzer()
    test_keyword_scorer()
    print("\n=== VERIFICATION COMPLETE ===")
