import asyncio
from store import InterviewStore
import pprint

async def check_db():
    print("Connecting to DB...")
    store = InterviewStore()
    
    if store.db is not None:
        print("\n=== CANDIDATES ===")
        async for candidate in store.db.candidates.find():
            pprint.pprint(candidate)
            
        print("\n=== SESSIONS ===")
        count = await store.db.sessions.count_documents({})
        print(f"Total Sessions Found: {count}")
        async for session in store.db.sessions.find().sort("created_at", -1).limit(5):
            pprint.pprint(session)
    else:
        print("Could not connect to database.")

if __name__ == "__main__":
    asyncio.run(check_db())
