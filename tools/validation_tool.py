class ValidationTool:
    """Tool for validating question quality."""
    
    def check_length(self, text, min_len=80, max_len=3000):
        if len(text) < min_len:
            return False, f"Too short ({len(text)} chars)"
        if len(text) > max_len:
            return False, f"Too long ({len(text)} chars)"
        return True, "OK"
    
    def check_duplicates(self, questions):
        """Returns set of duplicate IDs."""
        seen = {}
        duplicates = set()
        for q in questions:
            key = q["question_text"].lower().strip()[:100]
            if key in seen:
                duplicates.add(q["id"])
            seen[key] = q["id"]
        return duplicates
    
    def check_keywords(self, text, keywords):
        return any(kw in text.lower() for kw in keywords)