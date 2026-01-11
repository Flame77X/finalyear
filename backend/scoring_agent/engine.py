import logging

logger = logging.getLogger(__name__)

class ScoringEngine:
    def __init__(self):
        """
        Aggregates scores from all agents.
        """
        from scoring_agent.keyword_scorer import KeywordScorer
        self.keyword_scorer = KeywordScorer()

    def calculate_score(self, semantic_score: float, vocal_metrics: dict, non_verbal_score: float, transcript_text: str = "", job_role: str = "cse") -> dict:
        """
        Calculates the Final Interview Score using Weighted Average.
        
        Args:
            semantic_score (float): 0-100 from SentenceTransformer
            vocal_metrics (dict): Contains 'confidence_score' (0-100)
            non_verbal_score (float): 0-100 from Video Analysis
            transcript_text (str): Full text for keyword analysis
            job_role (str): Branch/Role for keyword matching
        """
        try:
            # --- 1. Accuracy & Content (55%) ---
            # Semantic (35%) + Keyword (20%)
            
            # Dynamic Keyword Scoring
            kw_result = self.keyword_scorer.extract_and_score(transcript_text, job_role)
            keyword_score = kw_result.get('keyword_score', 0.0)
            
            # Combined Content Score
            content_score = (semantic_score * 0.65) + (keyword_score * 0.35)
            
            # --- 2. Presentation & Confidence (45%) ---
            # Vocal (25%) + Non-Verbal (20%)
            vocal_score = vocal_metrics.get("confidence_score", 0.0)
            
            presentation_score = (vocal_score * 0.55) + (non_verbal_score * 0.45)
            
            # --- 3. Grand Total (Max 200 scaled down to 100 or kept as is? System uses 200 max in report?) ---
            # Report generator expected Total / 200.
            # Let's keep it consistent: Content(100) + Presentation(100) = 200 Max.
            
            grand_total = content_score + presentation_score
            
            return {
                "grand_total": round(grand_total, 1),
                "breakdown": {
                    "accuracy": {
                        "total": round(content_score, 1),
                        "semantic": round(semantic_score, 1),
                        "keyword": round(keyword_score, 1)
                    },
                    "confidence": {
                        "total": round(presentation_score, 1),
                        "vocal": round(vocal_score, 1),
                        "non_verbal": round(non_verbal_score, 1)
                    }
                },
                "keyword_analysis": kw_result # Extra details
            }

        except Exception as e:
            logger.error(f"Scoring calculation failed: {e}")
            return {"error": str(e)}
