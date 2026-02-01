import os
import json
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from pydantic import BaseModel, Field
from dataset_loader import InterviewDatasetLoader

# Define structured output for Branch Classification
class BranchClassification(BaseModel):
    branch: str = Field(description="The engineering branch identified (e.g., 'CSE', 'ECE', 'MECHANICAL') or 'UNKNOWN'")
    confidence: float = Field(description="Confidence score between 0 and 1")

# Define structured output for Resume Question Generation
class ResumeQuestion(BaseModel):
    text: str = Field(description="The technical interview question text")
    ideal_answer: str = Field(description="A concise ideal answer or key points expected")

class BrainAgent:
    def __init__(self, resume_text=None):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.resume_text = resume_text
        
        # Initialize LLM
        if self.api_key:
            self.llm = ChatGroq(
                temperature=0.3, 
                model_name="llama-3.3-70b-versatile", 
                api_key=self.api_key
            )
        else:
            print("Warning: GROQ_API_KEY not found. LLM features will fail.")
            self.llm = None

        # Interview State
        self.stage = "introduction"  # introduction -> branch_selection -> interview -> feedback
        
        # Dataset & Logic
        self.loader = InterviewDatasetLoader()
        self.available_branches = self.loader.get_all_branches()
        
        self.selected_branch = None
        self.questions_list = []
        self.k = 0  # Question counter
        
        # Resume Specifics
        self.resume_questions_asked = 0
        self.MAX_RESUME_QUESTIONS = 2
        
        self.current_question = None  # {id, text, ideal_answer}

    def get_response(self, user_text):
        """
        Determines the next step in the interview flow using LangChain logic.
        """
        user_text = user_text.strip()

        # 1. Introduction Stage
        if self.stage == "introduction":
            self.stage = "branch_selection"
            # Use LLM to generate a welcoming message
            if self.llm:
                try:
                    chain = (
                        ChatPromptTemplate.from_template(
                            "You are a friendly professional AI Interviewer. "
                            "The user just connected. "
                            "Greet them warmly and ask them to confirm their engineering branch "
                            "(Available: {branches}). Keep it concise."
                        )
                        | self.llm 
                        | StrOutputParser()
                    )
                    return chain.invoke({"branches": ", ".join(self.available_branches)})
                except Exception as e:
                    print(f"LLM Error (Intro): {e}")
            
            return "Hello! I am your AI Interviewer. To begin, could you please confirm your engineering branch?"

        # 2. Branch Selection Stage
        if self.stage == "branch_selection":
            detected_branch = self._classify_branch(user_text)
            
            if detected_branch and detected_branch != "UNKNOWN":
                self.selected_branch = detected_branch
                self.questions_list = self.loader.get_questions_for_branch(self.selected_branch)
                self.stage = "interview"
                
                # Retrieve first question
                return self.get_next_question(user_last_response=user_text)
            else:
                return f"I didn't quite catch that. Please specify one of our supported branches: {', '.join(self.available_branches)}."

        # 3. Interview Stage
        if self.stage == "interview":
            return self.get_next_question(user_last_response=user_text)

        return "The interview is complete. Thank you!"

    def _classify_branch(self, user_text):
        """
        Uses LangChain to classify the user's input into a valid branch.
        """
        # Common Fallback/Pre-check Logic (Robust Mapping)
        # This runs if LLM is missing OR if LLM fails, OR as a fast-path
        def run_fallback(text):
            text_lower = text.lower()
            # 1. Comprehensive Mapping
            branch_map = {
                "cse": "CSE", "computer science": "CSE", "cs": "CSE", "computer": "CSE",
                "ai": "AI", "artificial intelligence": "AI", "aiml": "AI",
                "civil": "CIVIL", "construction": "CIVIL",
                "mechanical": "MECHANICAL", "mech": "MECHANICAL",
                "ec": "EC", "electronics": "EC", "ece": "EC", "communication": "EC",
                "eee": "EEE", "electrical": "EEE",
                "ise": "ISE", "information science": "ISE", "is": "ISE"
            }
            
            # Check map keys in text
            for key, val in branch_map.items():
                if key in text_lower:
                    # Validate against actually available branches from DB/JSON
                    # (Logic: if mapped val is likely close to a real branch)
                    for av in self.available_branches:
                        if val == av or val in av:
                            return av
            
            # 2. Direct containment check
            for b in self.available_branches:
                if b.lower() in text_lower:
                    return b
            
            return "UNKNOWN"

        if not self.llm:
            return run_fallback(user_text)

        parser = JsonOutputParser(pydantic_object=BranchClassification)
        prompt = ChatPromptTemplate.from_template(
            "Classify the user's input into one of the following engineering branches: {branches}.\n"
            "User Input: '{user_text}'\n"
            "If the input matches a branch (even vaguely, like 'CS' for 'CSE', or 'EC' for 'ECE'), return that branch ID exactly as listed.\n"
            "If it does not match anything, return 'UNKNOWN'.\n"
            "\n{format_instructions}"
        )
        
        chain = prompt | self.llm | parser
        
        try:
            result = chain.invoke({
                "branches": self.available_branches,
                "user_text": user_text,
                "format_instructions": parser.get_format_instructions()
            })
            return result.get("branch", "UNKNOWN")
        except Exception as e:
            print(f"Branch Classification Error: {e}")
            return run_fallback(user_text)

    def get_next_question(self, user_last_response=""):
        """
        Determines the next question (Resume-based or Dataset-based).
        Optionally acknowledges the previous answer.
        """
        
        # A. Resume Based Questions
        if self.resume_text and self.resume_questions_asked < self.MAX_RESUME_QUESTIONS:
            question_data = self._generate_resume_question()
            if question_data:
                self.resume_questions_asked += 1
                self.current_question = question_data
                return f"(Resume Context) {question_data['text']}"
        
        # B. Dataset Questions
        if self.k < len(self.questions_list):
            q_data = self.questions_list[self.k]
            self.k += 1
            self.current_question = q_data
            return f"Question {self.k + self.resume_questions_asked}: {q_data['text']}"
        
        # End of Interview
        self.stage = "feedback"
        self.current_question = None
        return "That concludes the technical round. Thank you for your time!"

    def _generate_resume_question(self):
        """
        Uses LangChain to generate a technical question from the resume.
        """
        if not self.llm:
            return None

        parser = JsonOutputParser(pydantic_object=ResumeQuestion)
        prompt = ChatPromptTemplate.from_template(
            "You are an expert technical interviewer.\n"
            "Candidate's Resume Context: {resume_snippet}\n\n"
            "Task: Generate 1 hard technical interview question based on a specific project or skill mentioned in the resume.\n"
            "Also provide a short 'Ideal Answer' for scoring purposes.\n"
            "\n{format_instructions}"
        )
        
        chain = prompt | self.llm | parser
        
        try:
            # We truncate resume to avoid context limits if necessary
            snippet = self.resume_text[:3000] if self.resume_text else "No resume provided."
            
            result = chain.invoke({
                "resume_snippet": snippet,
                "format_instructions": parser.get_format_instructions()
            })
            
            return {
                "id": f"resume_{self.resume_questions_asked + 1}",
                "text": result.get("text", "Tell me about your best project."),
                "ideal_answer": result.get("ideal_answer", "Candidate should describe challenges and solutions.")
            }
        except Exception as e:
            print(f"Resume Question Gen Error: {e}")
            return None
