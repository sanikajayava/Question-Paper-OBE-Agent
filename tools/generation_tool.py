import re

class GenerationTool:
    """Tool for formatting questions for output."""
    
    def clean_text(self, text):
        """Remove OCR noise artifacts."""
        text = re.sub(r'\(?\d+\s*marks\)?', '', text, flags=re.IGNORECASE)
        text = re.sub(r'UNIT[\s\-]*[IVX]+', '', text, flags=re.IGNORECASE)
        text = re.sub(r'--- Page \d+ ---', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def format_question(self, text, marks):
        """Format a question into paper-ready form."""
        clean = self.clean_text(text)
        return f"[{marks} Marks] {clean}"
    
    def calculate_marks(self, total_marks, num_questions):
        """Distribute marks evenly."""
        if num_questions == 0:
            return 0
        return total_marks // num_questions