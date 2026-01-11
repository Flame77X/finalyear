import io
from pypdf import PdfReader

class ResumeParser:
    @staticmethod
    def extract_text(file_bytes: bytes, filename: str) -> str:
        """
        Extracts text from a resume file (PDF).
        """
        if filename.lower().endswith('.pdf'):
            return ResumeParser._extract_from_pdf(file_bytes)
        else:
            # Placeholder for other formats or plain text
            return ""

    @staticmethod
    def _extract_from_pdf(file_bytes: bytes) -> str:
        try:
            reader = PdfReader(io.BytesIO(file_bytes))
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            print(f"Error parsing PDF: {e}")
            return ""
