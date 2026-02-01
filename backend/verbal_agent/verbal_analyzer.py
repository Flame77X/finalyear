import os
import logging
import speech_recognition as sr
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QualityScore(BaseModel):
    score: float = Field(description="A score between 0.0 and 100.0 representing semantic similarity and accuracy.")

class VerbalAnalyzer:
    def __init__(self, model_size="base.en"):
        """
        Initializes the Verbal Agent. 
        Uses Google Speech Recognition (Online) as a robust fallback since Whisper download failed.
        """
        print("--- Initializing Speech Recognition (Google API) ---")
        
        # We don't need to load a heavy model for Google API
        self.recognizer = sr.Recognizer()
        
        # Initialize LLM for scoring
        self.api_key = os.getenv("GROQ_API_KEY")
        if self.api_key:
            self.llm = ChatGroq(
                temperature=0.0, 
                model_name="llama-3.3-70b-versatile", 
                api_key=self.api_key
            )
        else:
            logger.warning("GROQ_API_KEY not found. Scoring features will return 0.")
            self.llm = None

    def transcribe(self, audio_path: str) -> str:
        """
        Transcribes the given audio file to text using Google Speech Recognition.
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        print(f"--- Transcribing Audio File: {audio_path} ---")
        logger.info(f"Transcribing {audio_path}...")
        
        try:
            with sr.AudioFile(audio_path) as source:
                audio_data = self.recognizer.record(source)
                
            # Use Google Web Speech API (Free, high quality, requires internet)
            transcribed_text = self.recognizer.recognize_google(audio_data)
            
            print(f"--- Transcription Result: '{transcribed_text}' ---")
            return transcribed_text
            
        except sr.UnknownValueError:
             # This is NOT an error, just means silence/noise.
             # print("--- Google Speech Recognition could not understand audio ---")
            return ""
        except sr.RequestError as e:
            print(f"--- Could not request results from Google Speech Recognition service; {e} ---")
            logger.error(f"Google API Error: {e}")
            return ""
        except Exception as e:
            print(f"--- Transcription Failed: {e} ---")
            logger.error(f"Transcription failed: {e}")
            return ""

    def score_answer(self, user_text: str, correct_answer_concept: str) -> float:
        """
        Scores the user's answer against a concept using LLM-based semantic evaluation.
        Returns a score between 0.0 and 100.0.
        """
        if not user_text or not correct_answer_concept:
            return 0.0
        
        if not self.llm:
            return 0.0

        parser = JsonOutputParser(pydantic_object=QualityScore)
        prompt = ChatPromptTemplate.from_template(
            "Compare the User's Answer to the Ideal Answer Concept.\n"
            "Assess semantic similarity, factual accuracy, and relevance.\n"
            "User Answer: {user_text}\n"
            "Ideal Concept: {concept}\n"
            "Provide a score from 0.0 to 100.0 (100 being a perfect match in meaning).\n"
            "\n{format_instructions}"
        )
        
        chain = prompt | self.llm | parser
        
        try:
            result = chain.invoke({
                "user_text": user_text,
                "concept": correct_answer_concept,
                "format_instructions": parser.get_format_instructions()
            })
            return float(result.get("score", 0.0))
            
        except Exception as e:
            logger.error(f"LLM Scoring failed: {e}")
            return 0.0

if __name__ == "__main__":
    # Test
    agent = VerbalAnalyzer()
