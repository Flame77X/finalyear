from typing import List, Dict, Tuple
import logging
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class KeywordAnalysis(BaseModel):
    matched_keywords: List[str] = Field(description="List of relevant technical keywords found in the text")
    missing_keywords: List[str] = Field(description="List of expected keywords that were missing")
    keyword_score: float = Field(description="A score from 0 to 100 representing domain relevance coverage")

class KeywordScorer:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if self.api_key:
            self.llm = ChatGroq(
                temperature=0.0,
                model_name="llama-3.3-70b-versatile", 
                api_key=self.api_key
            )
        else:
            logger.warning("GROQ_API_KEY not found. Keyword scoring will fallback or fail.")
            self.llm = None
            
        # Hardcoded fallback merely for safekeeping if LLM fails, 
        # ideally we should fetch from questions.json if we had topic metadata there.
        self.domain_keywords = {
            'cse': ['algorithm', 'database', 'api', 'system design', 'oop', 'java', 'python', 'sql', 'networking', 'os'],
            'ai': ['machine learning', 'deep learning', 'neural network', 'nlp', 'pytorch', 'tensorflow', 'model'],
            'mechanical': ['thermodynamics', 'fluid mechanics', 'cad', 'manufacturing', 'gears', 'stress'],
            'civil': ['structural analysis', 'concrete', 'surveying', 'autocad', 'soil mechanics'],
            'ec': ['vlsi', 'embedded systems', 'microcontroller', 'analog', 'digital signal processing'],
            'eee': ['circuit', 'power systems', 'generator', 'transformer', 'grid']
        }

    def _load_keybert(self):
        # Deprecated: No longer loading KeyBERT locally to save resources.
        pass

    def extract_and_score(self, transcript: str, job_role: str = 'cse', top_n: int = 10) -> Dict:
        """
        Extracts keywords and scores them using LLM reasoning.
        """
        job_role = job_role.lower()
        
        # 1. Fallback Logic (if LLM unavailable)
        if not self.llm:
            return self._fallback_score(transcript, job_role)

        # 2. LLM Logic
        parser = JsonOutputParser(pydantic_object=KeywordAnalysis)
        
        # We define a "Reference Set" based on our basic domain map to guide the LLM, 
        # but allow it to find synonyms or related relevant terms.
        expected_examples = ", ".join(self.domain_keywords.get(job_role, self.domain_keywords['cse']))
        
        prompt = ChatPromptTemplate.from_template(
            "You are an expert technical interviewer evaluating an answer.\n"
            "Domain: {job_role}\n"
            "Candidate Transcript: \"{transcript}\"\n\n"
            "Tasks:\n"
            "1. Identify technical keywords/concepts present in the transcript.\n"
            "2. Compare them against standard expectations for this domain (Examples: {expected_examples}).\n"
            "3. Calculate a relevance score (0-100) based on the density and quality of technical terms used.\n"
            "\n{format_instructions}"
        )
        
        chain = prompt | self.llm | parser
        
        try:
            result = chain.invoke({
                "job_role": job_role,
                "transcript": transcript,
                "expected_examples": expected_examples,
                "format_instructions": parser.get_format_instructions()
            })
            
            return {
                'keyword_score': result.get('keyword_score', 0),
                'matched_keywords': result.get('matched_keywords', []),
                'missing_keywords': result.get('missing_keywords', []),
                'success': True
            }
        except Exception as e:
            logger.error(f"LLM Keyword Analysis failed: {e}")
            return self._fallback_score(transcript, job_role)

    def _fallback_score(self, transcript: str, job_role: str) -> Dict:
        """Simple substring matching fallback."""
        raw_text_lower = transcript.lower()
        expected = self.domain_keywords.get(job_role, self.domain_keywords['cse'])
        
        actual_matches = [exp for exp in expected if exp in raw_text_lower]
        coverage = len(actual_matches) / len(expected) if expected else 0
        keyword_score = min(100.0, coverage * 100 * 1.5)

        return {
            'keyword_score': round(keyword_score, 1),
            'matched_keywords': actual_matches,
            'missing_keywords': [k for k in expected if k not in actual_matches][:5],
            'success': True
        }
