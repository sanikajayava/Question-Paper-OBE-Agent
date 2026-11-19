import json
import os
import re

class RetrievalTool:
    def __init__(self, db_path="data/real_question_bank.json"):
        self.db_path = db_path
        self.data = self._load()
    
    def _load(self):
        with open(self.db_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def _normalize_subject(self, text):
        return re.sub(r'[^a-z0-9]', '', text.lower())
    
    def _normalize_batch(self, text):
        return re.sub(r'\s+', '', text).upper()
    
    def get_available_batch(self, subject, exam_type):
        target_subj_norm = self._normalize_subject(subject)
        target_exam_norm = exam_type.strip().upper()
        
        available_batches = set()
        for q in self.data:
            if self._normalize_subject(q["subject"]) == target_subj_norm:
                if q["exam_type"].strip().upper() == target_exam_norm:
                    available_batches.add(q["batch"])
        
        if not available_batches:
            return None
        
        sorted_batches = sorted(list(available_batches), reverse=True)
        return sorted_batches[0]

    def query(self, subject_name, exam_type, target_batch):
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