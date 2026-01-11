import os
import smtplib
from email.message import EmailMessage
import logging

logger = logging.getLogger(__name__)

def send_email_with_report(to_email, candidate_name, pdf_path):
    """
    Sends the Interview Report PDF via email.
    """
    user = os.getenv("GMAIL_USER")
    password = os.getenv("GMAIL_APP_PASSWORD")

    if not user or not password:
        logger.warning("GMAIL_USER or GMAIL_APP_PASSWORD not set. Skipping email.")
        print(f"Mock Email Sent to {to_email} with attachment {pdf_path}")
        return

    msg = EmailMessage()
    msg['Subject'] = f'Interview Report - {candidate_name}'
    msg['From'] = user
    msg['To'] = to_email
    msg.set_content(f"""
    Hello {candidate_name},

    Thank you for completing the AI Interview.
    
    Please find your detailed performance report attached.

    Best regards,
    AI Interviewer Team
    """)

    try:
        with open(pdf_path, 'rb') as f:
            file_data = f.read()
            file_name = os.path.basename(pdf_path)
        
        msg.add_attachment(file_data, maintype='application', subtype='pdf', filename=file_name)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(user, password)
            smtp.send_message(msg)
            
        print(f"Email sent successfully to {to_email}")
        
    except Exception as e:
        print(f"Failed to send email: {e}")
        logger.error(f"Email failed: {e}")
