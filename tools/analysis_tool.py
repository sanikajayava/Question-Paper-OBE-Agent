import re

class AnalysisTool:
    """Tool for analyzing question patterns."""
    
    def analyze_bloom(self, questions):
        """Estimates Bloom's level per question using action verbs."""
        bloom_verbs = {
            "L1_Remember": ["define", "list", "name", "what is", "identify"],
            "L2_Understand": ["explain", "describe", "discuss", "illustrate", "summarize"],
            "L3_Apply": ["apply", "calculate", "compute", "write", "implement", "use"],
            "L4_Analyze": ["analyze", "compare", "differentiate", "examine", "classify"],
            "L5_Evaluate": ["evaluate", "justify", "assess", "critique", "judge"],
            "L6_Create": ["design", "construct", "develop", "create", "formulate"]
        }
        
        distribution = {level: 0 for level in bloom_verbs}
        
        for q in questions:
            text = q["question_text"].lower()
            matched = False
            for level, verbs in bloom_verbs.items():
                if any(verb in text for verb in verbs):
                    distribution[level] += 1
                    matched = True
                    break
            if not matched:
                distribution["L2_Understand"] += 1
        
        return distribution
    
    def analyze_topics(self, questions, keywords):
        """Counts how often each topic keyword appears."""
        counts = {}
        for q in questions:
            text = q["question_text"].lower()
            for kw in keywords:
                if kw in text:
                    counts[kw] = counts.get(kw, 0) + 1
        return sorted(counts.items(), key=lambda x: -x[1])