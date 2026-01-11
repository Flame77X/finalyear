import sys
import os

print("--- 🚀 Optimization Verification ---")

try:
    print("1. Testing Dataset Loader...", end=" ")
    from dataset_loader import InterviewDatasetLoader
    loader = InterviewDatasetLoader()
    print("✅ OK")
except Exception as e:
    print(f"❌ FAIL: {e}")

try:
    print("2. Testing BrainAgent Init...", end=" ")
    from brain_agent.orchestrator import BrainAgent
    brain = BrainAgent()
    print("✅ OK")
except Exception as e:
    print(f"❌ FAIL: {e}")

print("--- Verification Complete ---")
