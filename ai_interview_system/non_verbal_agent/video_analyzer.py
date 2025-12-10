import logging
import cv2
try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
except ImportError:
    DEEPFACE_AVAILABLE = False

logger = logging.getLogger(__name__)

class VideoAnalyzer:
    def __init__(self):
        self.enabled = DEEPFACE_AVAILABLE
        if self.enabled:
            logger.info("✅ DeepFace loaded for Video Analysis.")
        else:
            logger.warning("⚠️ DeepFace not found. Non-Verbal analysis will be mocked.")

    def analyze_frame(self, image_path: str) -> dict:
        """
        Analyzes a single video frame for emotion/confidence.
        """
        if not self.enabled:
            return {"confidence_score": 0.0, "emotion": "unknown"}

        try:
            # Analyze emotion
            objs = DeepFace.analyze(
                img_path=image_path, 
                actions=['emotion'],
                enforce_detection=False,
                silent=True
            )
            
            if not objs:
                return {"confidence_score": 0.0, "emotion": "no_face"}
            
            result = objs[0]
            dominant_emotion = result['dominant_emotion']
            
            # Simple Heuristic for "Confidence"
            # Happy/Neutral -> High Confidence
            # Fear/Sad/Surprise -> Low Confidence
            score_map = {
                "happy": 90.0,
                "neutral": 85.0,
                "surprise": 60.0,
                "sad": 40.0,
                "fear": 30.0,
                "angry": 50.0,
                "disgust": 30.0
            }
            
            confidence = score_map.get(dominant_emotion, 50.0)
            
            logger.info(f"Video Analysis: {dominant_emotion} ({confidence}%)")
            
            return {
                "confidence_score": confidence,
                "emotion": dominant_emotion
            }

        except Exception as e:
            logger.error(f"Video analysis failed: {e}")
            return {"confidence_score": 0.0, "emotion": "error"}
