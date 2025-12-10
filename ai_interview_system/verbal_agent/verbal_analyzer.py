import os
import logging
from faster_whisper import WhisperModel
from sentence_transformers import SentenceTransformer, util

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VerbalAnalyzer:
    def __init__(self, model_size="base.en", embedding_model="all-MiniLM-L6-v2"):
        """
        Initializes the Verbal Agent with Whisper for STT and SentenceTransformers for scoring.
        """
        logger.info(f"Loading Whisper model: {model_size}...")
        try:
            # Run on CPU by default (easier for compatibility), can switch to 'cuda' if GPU available
            self.stt_model = WhisperModel(model_size, device="cpu", compute_type="int8")
            logger.info("Whisper model loaded.")
        except Exception as e:
            logger.error(f"Failed to load Whisper: {e}")
            raise

        logger.info(f"Loading Embedding model: {embedding_model}...")
        try:
            self.embed_model = SentenceTransformer(embedding_model)
            logger.info("Embedding model loaded.")
        except Exception as e:
            logger.error(f"Failed to load Embedding model: {e}")
            raise

    def transcribe(self, audio_path: str) -> str:
        """
        Transcribes the given audio file to text.
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        logger.info(f"Transcribing {audio_path}...")
        try:
            segments, info = self.stt_model.transcribe(audio_path, beam_size=5)
            
            # Collect all segments
            transcribed_text = " ".join([segment.text for segment in segments]).strip()
            
            logger.info(f"Transcription complete. Language: {info.language} ({info.language_probability:.2f})")
            return transcribed_text
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return ""

    def score_answer(self, user_text: str, correct_answer_concept: str) -> float:
        """
        Scores the user's answer against a concept using semantic similarity.
        Returns a score between 0.0 and 100.0.
        """
        if not user_text or not correct_answer_concept:
            return 0.0

        try:
            embeddings1 = self.embed_model.encode(user_text, convert_to_tensor=True)
            embeddings2 = self.embed_model.encode(correct_answer_concept, convert_to_tensor=True)
            
            cosine_score = util.cos_sim(embeddings1, embeddings2)
            score = float(cosine_score[0][0]) * 100
            
            return max(0.0, min(100.0, score)) # Clamp between 0-100
            
        except Exception as e:
            logger.error(f"Scoring failed: {e}")
            return 0.0

if __name__ == "__main__":
    # Test
    agent = VerbalAnalyzer()
    print("Agent initialized.")
