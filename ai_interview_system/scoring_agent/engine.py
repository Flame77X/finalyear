import logging

logger = logging.getLogger(__name__)

class ScoringEngine:
    def __init__(self):
        """
        Aggregates scores from all agents.
        """
        pass

    def calculate_score(self, verbal_score: float, vocal_metrics: dict, non_verbal_score: float = 0.0) -> dict:
        """
        Calculates the Final Interview Score.
        
        Weights (from Spec):
        1. Accuracy Score (Max 100):
           - Semantic Match: 80% (from Verbal Agent)
           - Keyword Match: 20% (TODO: Add spaCy keyword extraction) -> Currently Mocked as 100% of Semantic
        
        2. Confidence Score (Max 100):
           - Vocal Confidence: 60% (from Vocal Agent)
           - Non-Verbal Confidence: 40% (from Non-Verbal Agent)
        
        Grand Total: Accuracy + Confidence (Max 200)
        """
        try:
            # --- 1. Accuracy Score (Max 100) ---
            # Input: verbal_score comes from SentenceTransformer (0-100)
            # Logic: We treat the verbal_score as the "Semantic Score".
            # For now, we assume Keyword Score mimics Semantic Score until spaCy is added.
            semantic_score = verbal_score
            keyword_score = verbal_score # Placeholder
            
            accuracy_score = (semantic_score * 0.8) + (keyword_score * 0.2)
            
            # --- 2. Confidence Score (Max 100) ---
            # Input: vocal_metrics contains 'confidence_score' (0-100)
            # Input: non_verbal_score (0-100) -> Defaults to 0 if agent missing
            vocal_conf = vocal_metrics.get("confidence_score", 0.0)
            
            # If Non-Verbal is missing/zero, we might want to re-weight or just penalize.
            # Spec says 60/40 split.
            confidence_score = (vocal_conf * 0.6) + (non_verbal_score * 0.4)
            
            # --- 3. Grand Total (Max 200) ---
            grand_total = accuracy_score + confidence_score
            
            return {
                "grand_total": round(grand_total, 1),
                "breakdown": {
                    "accuracy": {
                        "total": round(accuracy_score, 1),
                        "semantic": round(semantic_score, 1),
                        "keyword": round(keyword_score, 1)
                    },
                    "confidence": {
                        "total": round(confidence_score, 1),
                        "vocal": round(vocal_conf, 1),
                        "non_verbal": round(non_verbal_score, 1)
                    }
                }
            }

        except Exception as e:
            logger.error(f"Scoring calculation failed: {e}")
            return {"error": str(e)}
