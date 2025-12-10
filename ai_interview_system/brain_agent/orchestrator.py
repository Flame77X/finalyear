import os
import logging
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class BrainAgent:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            logger.error("❌ GROQ_API_KEY not found in .env!")
            raise ValueError("GROQ_API_KEY is missing. Please set it in .env file.")
        
        try:
            self.client = Groq(api_key=self.api_key)
            logger.info("✅ Groq Client initialized successfully.")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Groq: {e}")
            raise

        # System Persona
        self.system_prompt = {
            "role": "system",
            "content": (
                "You are Sarah, an expert Senior Software Engineer conducting a technical interview. "
                "Your goal is to assess the candidate's technical skills, problem-solving ability, and cultural fit. "
                "Guidelines: "
                "1. Ask ONE clear question at a time. "
                "2. Be professional, polite, and encouraging, but rigorous. "
                "3. Keep your responses concise (max 2-3 sentences) to keep the conversation flowing. "
                "4. Start by introducing yourself and asking the candidate to introduce themselves. "
                "5. If the candidate gives a good answer, acknowledge it briefly and move to a deeper technical follow-up. "
                "6. Cover topics like Data Structures, System Design, and Soft Skills. "
                "7. Do NOT generate long monologues. Simulate a real-time voice conversation."
            )
        }
        
        # Conversation History
        self.chat_history = [self.system_prompt]

    def get_response(self, user_text: str) -> str:
        """
        Generates a response using Llama 3 via Groq.
        """
        try:
            # 1. Append User Input
            self.chat_history.append({"role": "user", "content": user_text})
            
            # 2. Call API
            completion = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=self.chat_history,
                temperature=0.7,
                max_tokens=150,
                top_p=1,
                stream=False,
                stop=None,
            )
            
            # 3. Extract Response
            ai_response = completion.choices[0].message.content
            
            # 4. Append AI Response to History (Context)
            self.chat_history.append({"role": "assistant", "content": ai_response})
            
            return ai_response

        except Exception as e:
            logger.error(f"❌ Groq generation failed: {e}")
            return "I apologize, I'm having trouble retrieving the next question. Could you briefly summarize your last point?"
