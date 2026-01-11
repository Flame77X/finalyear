import os
import time
from report_generator import generate_pdf_report
from email_service import send_email_with_report

def verify_system():
    print("--- Verifying Report & Email System ---")
    
    # 1. Dummy Data
    candidate_data = {
        "name": "Test Candidate",
        "email": "test@example.com",
        "branch": "Computer Science"
    }
    
    session_data = {
        "candidate_id": "test_123",
        "total_score": 165.5,
        "saved_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "score_breakdown": {
            "accuracy": {"total": 85.0},
            "confidence": {"total": 80.5}
        },
        "transcript": [
            {"question": "What is polymorphism?", "user_answer": "It is the ability of an object to take many forms."},
            {"question": "Explain ACID properties.", "user_answer": "Atomicity, Consistency, Isolation, Durability."}
        ]
    }
    
    output_pdf = "verify_report.pdf"
    
    # 2. Test PDF Gen
    print(f"\n[1/3] Generating PDF: {output_pdf}...")
    try:
        if os.path.exists(output_pdf):
            os.remove(output_pdf)
            
        success = generate_pdf_report(candidate_data, session_data, output_pdf)
        
        if success and os.path.exists(output_pdf):
            size = os.path.getsize(output_pdf)
            print(f"✅ PDF Generated Successfully! (Size: {size} bytes)")
        else:
            print(f"❌ PDF Generation Failed (File not found or error returned)")
            return
    except Exception as e:
        print(f"❌ PDF Generation Crashed: {e}")
        return

    # 3. Test Email
    print(f"\n[2/3] Sending Email (Mock Check)...")
    try:
        # This should print "Mock Email Sent" if no env vars are set
        send_email_with_report("test@example.com", "Test Candidate", output_pdf)
        print("✅ Email Service Triggered (Check console output above for Mock/Real status)")
    except Exception as e:
         print(f"❌ Email Service Crashed: {e}")
         
    # 4. Clean up
    print(f"\n[3/3] Cleanup...")
    # os.remove(output_pdf) # Keep it so user can see it if they want
    print(f"✅ Verification script finished. Check {output_pdf} content manually if needed.")

if __name__ == "__main__":
    verify_system()
