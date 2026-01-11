import os
import json
from groq import Groq
from dataset_loader import InterviewDatasetLoader

class BrainAgent:
    def __init__(self, resume_text=None):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.client = None
        if self.api_key:
            try:
                self.client = Groq(api_key=self.api_key)
            except Exception as e:
                print(f"Error initializing Groq client: {e}")
        else:
            print("Warning: GROQ_API_KEY not found.")

        # Interview State
        self.stage = "introduction"  # introduction -> branch_selection -> interview -> feedback
        self.conversation_history = []
        
        # Dataset & Resume Logic
        self.loader = InterviewDatasetLoader()
        self.selected_branch = None
        self.questions_list = []
        self.k = 0  # Question counter
        
        # Resume Specifics
        self.resume_text = resume_text
        self.resume_questions_asked = 0
        self.MAX_RESUME_QUESTIONS = 2
        
        self.current_question = None  # {id, text, ideal_answer}

    def get_response(self, user_text):
        """
        Determines the next step in the interview flow:
        1. Intro
        2. Branch Selection (if not set)
        3. Technical Questions (Hybrid: Resume -> Dataset)
        """
        # 1. Introduction Stage
        if self.stage == "introduction":
            self.stage = "branch_selection"
            return "Hello! I am your AI Interviewer. To begin, could you please confirm your engineering branch? (e.g., CSE, ISE, ECE, Mechanical, Civil)"

        # 2. Branch Selection Stage
        if self.stage == "branch_selection":
            branch_map = {
                "cse": "CSE", "computer science": "CSE",
                "ai": "CSE", "artificial intelligence": "CSE", # AI mapped to CSE for now
                "civil": "CIVIL",
                "mechanical": "MECHANICAL", "mech": "MECHANICAL",
                "ec": "EC", "electronics": "EC",
                "eee": "EEE", "electrical": "EEE",
                "ise": "CSE" # Map ISE to CSE for now
            }
            
            normalized_input = user_text.lower().strip()
            detected_branch = None
            
            for key, val in branch_map.items():
                if key in normalized_input:
                    detected_branch = val
                    break
            
            if detected_branch:
                self.selected_branch = detected_branch
                self.questions_list = self.loader.get_questions_for_branch(self.selected_branch)
                self.stage = "interview"
                return self.get_next_question()
            else:
                return "I didn't quite catch that. Please specify your branch (CSE, AI, Civil, Mechanical, EC, EEE)."

        # 3. Interview Stage
        if self.stage == "interview":
            return self.get_next_question()

        return "The interview is complete. Thank you!"

    def get_next_question(self):
        """
        Hybrid Logic:
        - First, ask questions based on Resume (if available).
        - Then, switch to Dataset questions.
        """
        
        # A. Resume Based Questions
        if self.resume_text and self.resume_questions_asked < self.MAX_RESUME_QUESTIONS:
            question_data = self._generate_resume_question()
            if question_data:
                self.resume_questions_asked += 1
                self.current_question = question_data
                return f"(Resume Question) {question_data['text']}"
        
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
        Uses LLM to generate a technical question based on the candidate's resume.
        Returns: {id: 'resume_X', text: '...', ideal_answer: '...'}
        """
        if not self.client:
            return None

        prompt = f"""
        You are an expert technical interviewer.
        Candidate's Resume Extract:
        "{self.resume_text[:2000]}"... (truncated)
        
        Task: Generate 1 hard technical interview question based on a specific project or skill mentioned in the resume.
        Also provide a short "Ideal Answer" for scoring purposes.
        
        Output JSON format only:
        {{
            "text": "The question string",
            "ideal_answer": "The expected key points in the answer"
        }}
        """
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-8b-8192",
                response_format={"type": "json_object"}
            )
            response_content = chat_completion.choices[0].message.content
            data = json.loads(response_content)
            
            return {
                "id": f"resume_{self.resume_questions_asked + 1}",
                "text": data.get("text", "Tell me about your best project."),
                "ideal_answer": data.get("ideal_answer", "Candidate should describe challenges and solutions.")
            }
        except Exception as e:
            print(f"Error generating resume question: {e}")
            return None
