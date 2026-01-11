import asyncio
import os
from store import InterviewStore
from dotenv import load_dotenv

async def test_store():
    load_dotenv()
    print(f"MONGO_URI from env: {os.getenv('MONGO_URI')}")
    
    store = InterviewStore()
    
    candidate_data = {
        "name": "Test User",
        "email": "test@example.com",
        "branch": "CSE"
    }
    
    print("Attempting to save candidate...")
    try:
        cid = await store.save_candidate(candidate_data)
        print(f"Candidate saved with ID: {cid}")
    except Exception as e:
        print(f"ERROR Saving Candidate: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_store())
