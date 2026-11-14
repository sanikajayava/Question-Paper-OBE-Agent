import sys
import os
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.retrieval_tool import RetrievalTool

class QuestionRetrievalAgent:
    def __init__(self):
        self.name = "Question Retrieval Agent"
        self.tool = RetrievalTool()

    def retrieve_questions(self, subject, exam_type, target_batch):
        print(f"\n[{self.name}] Using RetrievalTool for: {subject} | {exam_type} | {target_batch}")
        
        # AGENT CALLS TOOL
        raw_results = self.tool.query(subject, exam_type, target_batch)
        
        # Agent post-processes: strip noise from each question
        cleaned = []
        for q in raw_results:
            text = q["question_text"]
            noise_prefixes = [
                "--- Page 1 ---", "--- Page 2 ---", "--- Page 3 ---",
                "Note:", "Note;", "Duration:", "Max. Marks:", "Max, Marks:",
                "Course Code:", "Course Title:", "Answer any", "SRN",
            ]
            for prefix in noise_prefixes:
                if text.strip().startswith(prefix):
                    parts = text.split(prefix, 1)
                    if len(parts) > 1:
                        text = parts[1].strip()
            
            if len(text) < 60:
                continue
            
            noise_count = sum(1 for kw in ["kle technological", "department of", "srn", "usn"] if kw in text.lower())
            if noise_count >= 2:
                continue
            
            cleaned_q = dict(q)
            cleaned_q["question_text"] = text
            cleaned.append(cleaned_q)
        
        print(f"[{self.name}] Tool returned {len(raw_results)} raw, {len(cleaned)} cleaned questions.")
        return cleaned