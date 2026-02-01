
import zipfile
import os

# Configuration
base_dir = r"c:\Users\amith\OneDrive\Desktop\mainproject\finalyear"
output_zip = r"c:\Users\amith\OneDrive\Desktop\ai-interview-minimal.zip"

# Files and Folders to include explicitly (Relative to base_dir)
includes = [
    "backend/server.py",
    "backend/requirements.txt",
    "backend/store.py",
    "backend/report_generator.py",
    "backend/email_service.py",
    "backend/dataset_loader.py",
    "backend/resume_parser.py",
    "backend/questions.json",
    # Agents
    "backend/agents/lazy_loader.py",
    "backend/brain_agent/orchestrator.py",
    "backend/verbal_agent/verbal_analyzer.py",
    "backend/vocal_agent/vocal_analyzer.py",
    "backend/non_verbal_agent/video_analyzer.py",
    "backend/scoring_agent/engine.py",
    "backend/scoring_agent/keyword_scorer.py",
    # Frontend
    "web_client/package.json",
    "web_client/vite.config.js",
    "web_client/index.html",
    "web_client/src/main.jsx",
    "web_client/src/App.jsx",
    "web_client/src/pages/CandidateLogin.jsx",
    "web_client/src/pages/InterviewPage.jsx",
    "web_client/src/styles/InterviewPage.css",
]

def create_zip():
    print(f"Creating zip at: {output_zip}")
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for item in includes:
            file_path = os.path.join(base_dir, item)
            if os.path.exists(file_path):
                print(f"Adding: {item}")
                zipf.write(file_path, arcname=item)
            else:
                print(f"Warning: File not found: {item}")
    
    print("Zip creation complete.")

if __name__ == "__main__":
    create_zip()
