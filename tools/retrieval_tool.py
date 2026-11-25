import json
import os
import re
from pathlib import Path

from tools.vector_question_bank import VectorQuestionBank

class RetrievalTool:
    def __init__(self, db_path="data/real_question_bank.json"):
        self.db_path = Path(db_path)
        if not self.db_path.is_absolute():
            self.db_path = Path(__file__).resolve().parents[1] / self.db_path
        self.data = self._load()
        self.vector_store = None
    
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

    def semantic_query(self, query_text, subject, exam_type, target_batch, limit=20):
        if self.vector_store is None:
            self.vector_store = VectorQuestionBank()
            self.vector_store.index_questions(self.data)

        candidates = self.vector_store.search(query_text, limit=max(limit * 5, 50))
        target_subject = self._normalize_subject(subject)
        target_exam = exam_type.strip().upper()
        target_batch = self._normalize_batch(target_batch)
        matches = [
            item for item in candidates
            if self._normalize_subject(item.get("subject", "")) == target_subject
            and item.get("exam_type", "").strip().upper() == target_exam
            and self._normalize_batch(item.get("batch", "")) == target_batch
        ]
        return matches[:limit]