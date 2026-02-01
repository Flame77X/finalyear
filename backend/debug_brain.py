import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from brain_agent.orchestrator import BrainAgent
from dataset_loader import InterviewDatasetLoader

def debug_brain_logic():
    print("--- Debugging BrainAgent Logic ---")
    
    # Check Dataset Loader
    loader = InterviewDatasetLoader()
    print(f"Dataset Loader Branches: {loader.get_all_branches()}")
    
    # Check BrainAgent Fallback (simulate no API key)
    # temporarily unset api key if set
    old_key = os.environ.get("GROQ_API_KEY")
    if old_key:
        del os.environ["GROQ_API_KEY"]
    
    try:
        agent = BrainAgent()
        print(f"BrainAgent initialized. LLM present? {agent.llm is not None}")
        
        # Simulate Flow
        # 1. Intro
        resp1 = agent.get_response("start")
        print(f"Response 1 (Intro): {resp1}")
        print(f"Stage after 1: {agent.stage}")
        
        # 2. Branch Selection
        user_input = "CSE"
        resp2 = agent.get_response(user_input)
        print(f"User Input: '{user_input}'")
        print(f"Response 2 (Branch): {resp2}")
        print(f"Stage after 2: {agent.stage}")
        print(f"Selected Branch: {agent.selected_branch}")
        
        if agent.selected_branch != "CSE":
            print("❌ FAILURE: Did not detect CSE in fallback mode.")
        else:
            print("✅ SUCCESS: Detected CSE via fallback.")

    finally:
        if old_key:
            os.environ["GROQ_API_KEY"] = old_key

    print("\n--- Testing Richer Mapping Fallback ---")
    # Test if it fails for 'Computer Science'
    if old_key:
        del os.environ["GROQ_API_KEY"]
    
    agent2 = BrainAgent()
    agent2.stage = "branch_selection"
    resp3 = agent2.get_response("I study Computer Science")
    print(f"User Input: 'I study Computer Science'")
    print(f"Result: {resp3}")
    print(f"Detected Branch: {agent2.selected_branch}")
    
    if agent2.selected_branch is None:
        print("⚠️ NOTE: 'Computer Science' failed (Expected regression from previous code if key is missing)")

if __name__ == "__main__":
    debug_brain_logic()
