from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
import os

def generate_pdf_report(candidate_data, session_data, output_path):
    """
    Generates a PDF report for the interview session.
    
    Args:
        candidate_data (dict): { "name", "email", "branch", ... }
        session_data (dict): { "total_score", "transcript", ... }
        output_path (str): File path to save the PDF.
    """
    try:
        c = canvas.Canvas(output_path, pagesize=letter)
        width, height = letter
        
        # --- Header ---
        c.setFont("Helvetica-Bold", 24)
        c.drawString(1 * inch, height - 1 * inch, "AI Interview Report")
        
        c.setFont("Helvetica", 12)
        c.drawString(1 * inch, height - 1.5 * inch, f"Date: {session_data.get('saved_at', 'N/A')}")
        
        # --- Candidate Details ---
        c.setLineWidth(1)
        c.line(1 * inch, height - 1.7 * inch, width - 1 * inch, height - 1.7 * inch)
        
        y_pos = height - 2.2 * inch
        c.setFont("Helvetica-Bold", 14)
        c.drawString(1 * inch, y_pos, "Candidate Details")
        y_pos -= 0.3 * inch
        
        c.setFont("Helvetica", 12)
        c.drawString(1.2 * inch, y_pos, f"Name: {candidate_data.get('name', 'N/A')}")
        y_pos -= 0.25 * inch
        c.drawString(1.2 * inch, y_pos, f"Email: {candidate_data.get('email', 'N/A')}")
        y_pos -= 0.25 * inch
        c.drawString(1.2 * inch, y_pos, f"Branch: {candidate_data.get('branch', 'N/A')}")
        
        # --- Score Summary ---
        y_pos -= 0.6 * inch
        c.setFont("Helvetica-Bold", 14)
        c.drawString(1, y_pos, "Performance Summary") # Fixed syntax error in x coord
        c.drawString(1 * inch, y_pos, "Performance Summary")
        y_pos -= 0.3 * inch
        
        total_score = session_data.get("total_score", 0)
        c.setFont("Helvetica-Bold", 16)
        
        if total_score >= 150:
            color = colors.green
            verdict = "Strong Hire"
        elif total_score >= 100:
            color = colors.orange
            verdict = "Consider"
        else:
            color = colors.red
            verdict = "Needs Improvement"
            
        c.setFillColor(color)
        c.drawString(1.2 * inch, y_pos, f"Total Score: {total_score} / 200")
        c.drawString(4 * inch, y_pos, f"Verdict: {verdict}")
        c.setFillColor(colors.black)
        
        # --- Breakdown ---
        y_pos -= 0.4 * inch
        c.setFont("Helvetica", 12)
        # Assuming breakdown might be in session_data, otherwise placeholder
        breakdown = session_data.get("score_breakdown", {})
        accuracy = breakdown.get("accuracy", {}).get("total", "N/A")
        confidence = breakdown.get("confidence", {}).get("total", "N/A")
        
        c.drawString(1.5 * inch, y_pos, f"• Accuracy Score: {accuracy} / 100")
        y_pos -= 0.25 * inch
        c.drawString(1.5 * inch, y_pos, f"• Confidence Score: {confidence} / 100")
        
        # --- Transcript / Question Summary ---
        y_pos -= 0.6 * inch
        c.setFont("Helvetica-Bold", 14)
        c.drawString(1 * inch, y_pos, "Interview Transcript Summary")
        y_pos -= 0.3 * inch
        
        c.setFont("Helvetica", 10)
        transcript = session_data.get("transcript", [])
        
        for turn in transcript:
            if y_pos < 1 * inch:
                c.showPage()
                y_pos = height - 1 * inch
                c.setFont("Helvetica", 10)
            
            question = turn.get("question", "Question")
            answer = turn.get("user_answer", "Answer")
            
            # Simple wrapping or truncation for PDF
            q_line = f"Q: {question[:80]}..." if len(question) > 80 else f"Q: {question}"
            a_line = f"A: {answer[:80]}..." if len(answer) > 80 else f"A: {answer}"
            
            c.drawString(1.2 * inch, y_pos, q_line)
            y_pos -= 0.2 * inch
            c.setFillColor(colors.dimgrey)
            c.drawString(1.4 * inch, y_pos, a_line)
            c.setFillColor(colors.black)
            y_pos -= 0.3 * inch

        c.save()
        return True
    except Exception as e:
        print(f"PDF Generation Failed: {e}")
        return False
