import json
import random
import os
from typing import Dict, List, Optional, Any

class InterviewDatasetLoader:
    """
    Load and manage interview question datasets for different branches.
    Handles greeting questions and branch-specific technical questions.
    """
    
    def __init__(self, json_file_path: str = None):
        """
        Initialize the dataset loader.
        
        Args:
            json_file_path: Path to the questions.json file.
                            If None, attempts to find it in the same directory.
        """
        if json_file_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            json_file_path = os.path.join(base_dir, "questions.json")
            
        self.file_path = json_file_path
        self.data = self._load_json(json_file_path)
        self.branches = list(self.data.get("branches", {}).keys())
        self.common_questions = self.data.get("common", [])
        
    def _load_json(self, file_path: str) -> Dict:
        """Load JSON dataset from file."""
        try:
            if not os.path.exists(file_path):
                print(f"[DatasetLoader] Error: File '{file_path}' not found.")
                return {"common": [], "branches": {}}
                
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"[DatasetLoader] Error: Invalid JSON in '{file_path}': {e}")
            return {"common": [], "branches": {}}
        except Exception as e:
            print(f"[DatasetLoader] Error loading file: {e}")
            return {"common": [], "branches": {}}
    
    def get_all_branches(self) -> List[str]:
        """Get list of all available branches."""
        return self.branches
    
    def get_greeting_questions(self) -> List[Dict]:
        """Get all greeting/common questions."""
        return self.common_questions
    
    def get_questions_for_branch(self, branch: str) -> List[Dict]:
        return self.get_branch_questions(branch)

    def get_branch_questions(self, branch: str) -> List[Dict]:
        """
        Get all questions for a specific branch.
        
        Args:
            branch: Branch name (CSE, AI, CIVIL, MECHANICAL, EC, EEE)
            
        Returns:
            List of questions for the branch
        """
        if not self.data or "branches" not in self.data:
            return []
            
        # Case-insensitive lookup attempt if exact match fails
        if branch not in self.data["branches"]:
            # Try upper case
            if branch.upper() in self.data["branches"]:
                return self.data["branches"][branch.upper()]
            print(f"[DatasetLoader] Error: Branch '{branch}' not found. Available: {self.branches}")
            return []
            
        return self.data["branches"][branch]
    
    def get_random_greeting_question(self, exclude_ids: List[str] = None) -> Optional[Dict]:
        """Get a random greeting question, optionally excluding specific IDs."""
        candidates = self.common_questions
        if exclude_ids:
            candidates = [q for q in candidates if q['id'] not in exclude_ids]
        
        if not candidates:
            return random.choice(self.common_questions) if self.common_questions else None
            
        return random.choice(candidates)
    
    def get_random_branch_question(self, branch: str, exclude_ids: List[str] = None) -> Optional[Dict]:
        """Get a random technical question for a branch."""
        questions = self.get_branch_questions(branch)
        if not questions:
            return None
            
        candidates = questions
        if exclude_ids:
            candidates = [q for q in candidates if q['id'] not in exclude_ids]
            
        if not candidates:
            return random.choice(questions)
            
        return random.choice(candidates)

    def get_question_by_id(self, question_id: str) -> Optional[Dict]:
        """Find a question by its unique ID (searches common and all branches)."""
        # Check common
        for q in self.common_questions:
            if q['id'] == question_id:
                return q
        
        # Check branches
        if "branches" in self.data:
            for branch_qs in self.data["branches"].values():
                for q in branch_qs:
                    if q['id'] == question_id:
                        return q
        return None

    def get_dataset_stats(self) -> Dict[str, Any]:
        """Return statistics about the loaded dataset."""
        stats = {
            "total_greeting": len(self.common_questions),
            "branches": {},
            "total_technical": 0
        }
        
        if "branches" in self.data:
            for branch, qs in self.data["branches"].items():
                count = len(qs)
                stats["branches"][branch] = count
                stats["total_technical"] += count
                
        stats["total_questions"] = stats["total_greeting"] + stats["total_technical"]
        return stats

# Example Usage
if __name__ == "__main__":
    loader = InterviewDatasetLoader()
    print(f"Loaded {loader.get_dataset_stats()['total_questions']} questions.")
    print("Branches:", loader.get_all_branches())
    
    # Test Greeting
    print("\nRandom Greeting:", loader.get_random_greeting_question())
    
    # Test Branch
    if "CSE" in loader.get_all_branches():
        print("\nRandom CSE Question:", loader.get_random_branch_question("CSE"))
