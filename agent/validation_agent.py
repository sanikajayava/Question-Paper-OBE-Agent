import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.validation_tool import ValidationTool

class ValidationAgent:
    def __init__(self):
        self.name = "Validation Agent"
        self.tool = ValidationTool()  # <-- AGENT USES TOOL
        
        self.subject_keywords = {
            "cloud computing": ["cloud", "docker", "kubernetes", "virtualization", "serverless", "container"],
            "deep learning": ["neural", "cnn", "rnn", "lstm", "deep", "network", "activation", "dropout", "training"],
            "gen ai": ["generative", "gan", "llm", "diffusion", "transformer", "attention", "prompt", "bert", "gpt", "autoencoder"],
            "cyber security": ["cyber", "security", "attack", "firewall", "encryption", "soc", "siem", "forensics", "malware", "cia", "threat"]
        }

    def validate_questions(self, questions, expected_subject):
        print(f"\n[{self.name}] Using ValidationTool on {len(questions)} questions...")
        
        keywords = self.subject_keywords.get(expected_subject.lower(), [])
        duplicates = self.tool.check_duplicates(questions)  # AGENT CALLS TOOL
        
        valid_questions = []
        rejected = []

        for q in questions:
            issues = []
            
            # AGENT CALLS TOOL - length check
            ok, msg = self.tool.check_length(q["question_text"])
            if not ok:
                issues.append(msg)
            
            # AGENT CALLS TOOL - keyword check
            if not self.tool.check_keywords(q["question_text"], keywords):
                issues.append("Not relevant to subject keywords.")
            
            # Duplicate check
            if q["id"] in duplicates:
                issues.append("Duplicate question.")
            
            if issues:
                rejected.append({"id": q["id"], "issues": issues})
            else:
                valid_questions.append(q)

        print(f"[{self.name}] Tool complete. Valid: {len(valid_questions)}, Rejected: {len(rejected)}")
        for r in rejected:
            print(f"     [Rejected] {r['id']}: {', '.join(r['issues'])}")

        return valid_questions, rejected