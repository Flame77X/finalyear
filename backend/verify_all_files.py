import os
import sys
import asyncio
import json
import traceback

print("STARTING LINEAR VERIFICATION...")

def fail(msg):
    print(f"FAIL: {msg}")
    sys.exit(1)

def pass_step(msg):
    print(f"PASS: {msg}")

# 1. Dependencies
try:
    import fastapi
    import uvicorn
    import cv2
    import numpy
    import librosa
    import deepface
    import motor
    import reportlab
    import keybert
    import sentence_transformers
    import python_multipart
    pass_step("Dependencies Import")
except ImportError as e:
    fail(f"Dependency missing: {e}")

# 2. Data Files
required_files = ["questions.json", ".env.example", "requirements.txt", "store.py", "dataset_loader.py"]
for f in required_files:
    if not os.path.exists(f):
        fail(f"Missing file: {f}")

# Check questions.json
try:
    with open("questions.json", "r") as f:
        data = json.load(f)
        if "ISE" not in data.get("branches", {}):
            fail("ISE branch missing in questions.json")
    pass_step("Data Files & Content")
except Exception as e:
    fail(f"Data file check error: {e}")

# 3. Backend Modules (DatasetLoader fix check)
try:
    from dataset_loader import InterviewDatasetLoader
    loader = InterviewDatasetLoader()
    # Check if the alias method exists
    if not hasattr(loader, 'get_questions_for_branch'):
        fail("InterviewDatasetLoader missing 'get_questions_for_branch' method")
    
    # Check if it works
    qs = loader.get_questions_for_branch("CSE")
    if not isinstance(qs, list):
        fail(f"get_questions_for_branch returned {type(qs)}, expected list")
    pass_step("Backend Modules (DatasetLoader)")
except Exception as e:
    fail(f"Backend module error: {e}")

# 4. Store (Offline Mode check)
async def check_store():
    try:
        from store import InterviewStore
        store = InterviewStore()
        # Should not crash even if DB down
        res = await store.save_candidate({"name": "Test", "email": "a@b.com", "branch": "CSE"})
        print(f"   Store saved result: {res}")
        if not isinstance(res, str):
            fail(f"Store returned {type(res)}, expected str")
        pass_step("Store Offline Mode")
    except Exception as e:
        traceback.print_exc()
        fail(f"Store crashed: {e}")

# Run Async
try:
    asyncio.run(check_store())
except Exception as e:
    fail(f"Async loop error: {e}")

print("ALL CHECKS PASSED")
sys.exit(0)
