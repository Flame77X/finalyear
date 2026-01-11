import logging
import numpy as np
import cv2
from typing import Dict

logger = logging.getLogger(__name__)

class NonVerbalAgent:
    def __init__(self):
        self.emotion_map = {
            'happy': 0.9, 'neutral': 0.6, 'sad': 0.2, 'angry': 0.3,
            'surprised': 0.8, 'fearful': 0.4, 'disgusted': 0.2
        }
        # Lazy load deepface to avoid startup lag if not used
        self.deepface = None

    def _load_deepface(self):
        if not self.deepface:
            try:
                from deepface import DeepFace
                self.deepface = DeepFace
                logger.info("DeepFace loaded successfully.")
            except ImportError:
                logger.error("DeepFace not found. Please install deepface.")
                self.deepface = None

    def analyze_frame(self, frame_data: np.ndarray) -> Dict:
        """
        Process a single video frame. 
        Returns confidence score (0-1), emotions, etc.
        """
        try:
            if frame_data is None or frame_data.size == 0:
                return self._empty_response()
            
            # Ensure RGB
            if len(frame_data.shape) == 3:
                frame_rgb = cv2.cvtColor(frame_data, cv2.COLOR_BGR2RGB)
            else:
                frame_rgb = frame_data

            # 1. Emotions (DeepFace)
            self._load_deepface()
            emotions = {}
            if self.deepface:
                try:
                    # actions=['emotion'] only
                    res = self.deepface.analyze(frame_rgb, actions=['emotion'], enforce_detection=False)
                    # DeepFace returns a list of results (one per face)
                    if isinstance(res, list):
                        res = res[0]
                    
                    raw_emotions = res.get('emotion', {})
                    # Normalize 0-100 -> 0-1
                    emotions = {k: v/100.0 for k, v in raw_emotions.items()}
                except Exception as e:
                    logger.debug(f"DeepFace analyze failed (no face?): {e}")

            if not emotions:
                # Fallback to defaults
                emotions = {k: 0.1 for k in self.emotion_map}
                emotions['neutral'] = 0.5

            # 2. Eye Contact (Heuristic)
            # Without landmarks/dlib, we assume if face detected by DeepFace, contact is okay.
            # Real implementation needs gaze tracking.
            # For this prototype: Random fluctuation around high confidence if emotions detected.
            eye_contact = 0.8 if emotions.get('neutral', 0) > 0.1 else 0.4
            
            # 3. Posture (Heuristic)
            # Assume centered face if detection worked
            posture_score = 0.7 

            # 4. Aggregate
            confidence = self._calculate_aggregate_confidence(emotions, eye_contact, posture_score)

            return {
                'confidence_score': confidence,
                'emotions': emotions,
                'facial_expression': max(emotions, key=emotions.get),
                'eye_contact': eye_contact,
                'posture_score': posture_score,
                'success': True
            }

        except Exception as e:
            logger.error(f"Frame analysis error: {e}")
            return self._empty_response()

    def _calculate_aggregate_confidence(self, emotions, eye_contact, posture):
        # Weight positive emotions higher
        pos_score = emotions.get('happy', 0) + emotions.get('neutral', 0) + emotions.get('surprised', 0)
        neg_score = emotions.get('sad', 0) + emotions.get('angry', 0) + emotions.get('fearful', 0)
        
        # Simple weighted sum
        # Conf = 40% Emotion Balance + 30% Eye + 30% Posture
        emo_balance = min(1.0, max(0.0, (pos_score - neg_score + 1) / 2)) # Normalize -1..1 to 0..1
        
        total = (emo_balance * 0.4) + (eye_contact * 0.3) + (posture * 0.3)
        return round(total, 2)

    def _empty_response(self):
        return {
            'confidence_score': 0.0,
            'emotions': {},
            'facial_expression': 'none',
            'eye_contact': 0.0,
            'posture_score': 0.0,
            'success': False
        }

if __name__ == "__main__":
    # Test
    agent = NonVerbalAgent()
    print("NonVerbal Agent Initialized.")
