import re

class AnalysisTool:
    """Tool for analyzing question patterns and marks."""

    BLOOM_VERBS = {
        "L1_Remember": ["define", "list", "name", "what is", "identify"],
        "L2_Understand": ["explain", "describe", "discuss", "illustrate", "summarize"],
        "L3_Apply": ["apply", "calculate", "compute", "write", "implement", "use"],
        "L4_Analyze": ["analyze", "compare", "differentiate", "examine", "classify"],
        "L5_Evaluate": ["evaluate", "justify", "assess", "critique", "judge"],
        "L6_Create": ["design", "construct", "develop", "create", "formulate"],
    }
    BLOOM_LEVELS = tuple(BLOOM_VERBS)

    def classify_bloom(self, text):
        text = text.lower()
        for level, verbs in self.BLOOM_VERBS.items():
            if any(verb in text for verb in verbs):
                return level
        return "L2_Understand"
    
    def analyze_bloom(self, questions):
        distribution = {level: 0 for level in self.BLOOM_VERBS}
        
        for q in questions:
            distribution[self.classify_bloom(q["question_text"])] += 1
        
        return distribution
    
    def analyze_topics(self, questions, keywords):
        counts = {}
        for q in questions:
            text = q["question_text"].lower()
            for kw in keywords:
                if kw in text:
                    counts[kw] = counts.get(kw, 0) + 1
        return sorted(counts.items(), key=lambda x: -x[1])

    def analyze_marks_pattern(self, questions):
        """NEW: Analyzes past papers to find the average marks per question."""
        marks_found = []
        
        # Regex to find patterns like "10 marks", "(08marks)", "07marks)", "5 Marks"
        pattern = r'(\d{1,2})\s*(?:marks|Marks|MARKs)'
        
        for q in questions:
            match = re.search(pattern, q["question_text"])
            if match:
                marks_found.append(int(match.group(1)))
        
        if not marks_found:
            # Fallback if OCR failed to capture marks
            return 10
            
        # Calculate the most common mark weight (mode) or average
        average = sum(marks_found) / len(marks_found)
        return int(round(average))