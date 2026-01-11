
import asyncio
import json
import os
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "ai_interview_system"

class InterviewStore:
    def __init__(self):
        self.client = None
        self.db = None
        if MONGO_URI:
            try:
                self.client = AsyncIOMotorClient(
                    MONGO_URI,
                    serverSelectionTimeoutMS=2000,
                    connectTimeoutMS=2000,
                    socketTimeoutMS=2000
                )
                self.db = self.client[DB_NAME]
                print(f"Connected to MongoDB: {DB_NAME}")
            except Exception as e:
                print(f"Failed to connect to MongoDB: {e}")
        else:
            print("Warning: MONGO_URI not found in environment variables.")

    async def save_candidate(self, candidate_data: dict) -> str:
        """
        Saves candidate registration details.
        Returns the inserted ID as a string.
        """
        try:
            if self.db is None:
                return "offline_mode_no_db"
            
            candidate_data["created_at"] = datetime.utcnow()
            result = await self.db.candidates.insert_one(candidate_data)
            return str(result.inserted_id)
        except Exception as e:
            print(f"MongoDB Error in save_candidate: {e}")
            return "offline_mode_error"

    async def get_candidate(self, candidate_id: str) -> dict:
        if self.db is None:
            return {}
        from bson.objectid import ObjectId
        try:
            return await self.db.candidates.find_one({"_id": ObjectId(candidate_id)})
        except:
            return {}

    async def add_session(self, session_data: dict):
        """
        Saves the completed interview session data.
        """
        if self.db is None:
            print("MongoDB not connected. Session not saved.")
            return

        # Ensure non-blocking DB write
        session_data["saved_at"] = datetime.utcnow()
        await self.db.sessions.insert_one(session_data)
        print(f"Session {session_data.get('session_id')} saved to MongoDB.")

    # Legacy method support (optional, can be removed if not used)
    def save_history_blocking(self, history):
        pass
