import json
import os
import re

class RetrievalTool:
    """Tool for retrieving questions from the database."""
    def __init__(self, db_path="data/real_question_bank.json"):
        self.db_path = db_path
        self.data = self._load()
    
    def _load(self):
        with open(self.db_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def _normalize_subject(self, text):
        """Remove ALL non-alphanumeric characters and lowercase."""
        return re.sub(r'[^a-z0-9]', '', text.lower())
    
    def _normalize_batch(self, text):
        """Remove ALL whitespace and uppercase."""
        return re.sub(r'\s+', '', text).upper()
    
    def query(self, subject_name, exam_type, target_batch):
        """Returns all questions matching the given criteria."""
        results = []
        target_subj_norm = self._normalize_subject(subject_name)
        target_exam_norm = exam_type.strip().upper()
        target_batch_norm = self._normalize_batch(target_batch)
        
        for q in self.data:
            db_subj_norm = self._normalize_subject(q["subject"])
            if db_subj_norm != target_subj_norm:
                continue
            if q["exam_type"].strip().upper() != target_exam_norm:
                continue
            if self._normalize_batch(q["batch"]) != target_batch_norm:
                continue
            results.append(q)
        
        return results
    
    def get_stats(self):
        stats = {}
        for q in self.data:
            subj = q["subject"]
            stats[subj] = stats.get(subj, 0) + 1
        return stats