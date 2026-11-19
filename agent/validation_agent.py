import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.validation_tool import ValidationTool

class ValidationAgent:
    def __init__(self):
        self.name = "Validation Agent"
        self.tool = ValidationTool()
        
        # Very broad keywords to allow more questions
        self.subject_keywords = {
            "cloud computing": ["cloud", "docker", "kubernetes", "virtualization", "serverless", "container", "network"],
            "deep learning": ["neural", "cnn", "rnn", "lstm", "deep", "network", "activation", "dropout", "training", "architectures", "convolution", "yolo", "rcnn", "transfer learning", "hyperparameter", "weight", "feature"],
            "gen ai": ["generative", "gan", "llm", "diffusion", "transformer", "attention", "prompt", "bert", "gpt", "autoencoder"],
            "cyber security": ["cyber", "security", "attack", "firewall", "encryption", "soc", "siem", "forensics", "malware", "cia", "threat"]
        }
        
        # Book names and document garbage
        self.garbage_keywords = [
            "page 1", "page 2", "srn", "e010", "machine learning and deep learning with python", 
            "text books", "references", "tom mitchell", "christopher bishop", "aurelien geron",
            "sebastian raschka", "mixing of sub-questions"
        ]

    def validate_questions(self, questions, expected_subject):
        print(f"\n[{self.name}] Validating {len(questions)} questions...")
        
        keywords = self.subject_keywords.get(expected_subject.lower(), [])
        duplicates = self.tool.check_duplicates(questions)
        
        valid_questions = []
        rejected = []

        for q in questions:
            text = q["question_text"].lower()
            issues = []
            
            # Lowered from 80 to 50 to accept shorter questions
            if len(text) < 50:
                issues.append("Too short.")
                
            if any(g in text for g in self.garbage_keywords):
                issues.append("Garbage OCR text.")
            
            # If it comes from the PDF fallback, we trust it more
            is_fallback = "fallback" in q["id"].lower()
            
            # If it's a DB question, it MUST have a keyword. Fallback questions are exempt.
            if not is_fallback:
                if not any(kw in text for kw in keywords):
                    issues.append("Not relevant to subject.")
            
            if q["id"] in duplicates:
                issues.append("Duplicate.")

            if issues:
                rejected.append({"id": q["id"], "issues": issues})
            else:
                valid_questions.append(q)

        print(f"[{self.name}] Valid: {len(valid_questions)}, Rejected: {len(rejected)}")
        return valid_questions, rejected