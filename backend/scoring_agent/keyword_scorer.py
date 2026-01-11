from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)

class KeywordScorer:
    def __init__(self):
        self.kw_model = None
        self.domain_keywords = {
            'cse': ['algorithm', 'database', 'api', 'system design', 'oop', 'java', 'python', 'sql', 'networking', 'os'],
            'ai': ['machine learning', 'deep learning', 'neural network', 'nlp', 'pytorch', 'tensorflow', 'model'],
            'mechanical': ['thermodynamics', 'fluid mechanics', 'cad', 'manufacturing', 'gears', 'stress'],
            'civil': ['structural analysis', 'concrete', 'surveying', 'autocad', 'soil mechanics'],
            'ec': ['vlsi', 'embedded systems', 'microcontroller', 'analog', 'digital signal processing'],
            'eee': ['circuit', 'power systems', 'generator', 'transformer', 'grid']
        }

    def _load_keybert(self):
        if not self.kw_model:
            try:
                from keybert import KeyBERT
                self.kw_model = KeyBERT('all-MiniLM-L6-v2')
            except ImportError:
                logger.warning("KeyBERT not installed. Using fallback keyword matching.")
                self.kw_model = None

    def extract_and_score(self, transcript: str, job_role: str = 'cse', top_n: int = 10) -> Dict:
        """
        Extracts keywords and scores them against the expected domain keywords.
        """
        self._load_keybert()
        job_role = job_role.lower()
        
        # 1. Extraction
        extracted_keywords = []
        if self.kw_model:
            try:
                extracted_data = self.kw_model.extract_keywords(
                    transcript, keyphrase_ngram_range=(1, 2), stop_words='english', top_n=top_n
                )
                extracted_keywords = [k[0] for k in extracted_data]
            except Exception as e:
                logger.error(f"KeyBERT extraction failed: {e}")
        
        # Fallback if KeyBERT failed or not installed: Simple split (naive)
        if not extracted_keywords:
            extracted_keywords = list(set(transcript.lower().split()))

        # 2. Matching
        expected = self.domain_keywords.get(job_role, self.domain_keywords['cse'])
        matched = [k for k in extracted_keywords if any(exp in k.lower() for exp in expected)]
        
        # 3. Scoring
        # Coverage: What % of EXTRACTED keywords are relevant? (Precision focus)
        # OR What % of EXPECTED keywords were mentioned? (Recall focus) -> Better for interview
        
        # We check mentions in the raw text too, to be generous
        raw_text_lower = transcript.lower()
        actual_matches = [exp for exp in expected if exp in raw_text_lower]
        
        coverage = len(actual_matches) / len(expected) if expected else 0
        keyword_score = min(100.0, coverage * 100 * 1.5) # multiplier to make it achievable (getting 60% of keywords is great)

        return {
            'keyword_score': round(keyword_score, 1),
            'matched_keywords': actual_matches,
            'missing_keywords': [k for k in expected if k not in actual_matches][:5],
            'success': True
        }
