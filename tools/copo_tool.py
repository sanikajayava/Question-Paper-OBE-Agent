import re

class COPOTool:
    """Tool for mapping questions to Course Outcomes (CO) and Program Outcomes (PO)."""
    
    # Keyword-based CO classification
    CO_KEYWORDS = {
        "CO1": ["define", "list", "what is", "identify", "name", "state", "recall"],
        "CO2": ["explain", "describe", "discuss", "illustrate", "summarize", "compare"],
        "CO3": ["analyze", "apply", "calculate", "compute", "solve", "implement", "write"],
        "CO4": ["design", "develop", "construct", "create", "formulate"],
        "CO5": ["evaluate", "justify", "assess", "critique", "recommend", "propose"]
    }
    
    # CO -> PO mapping
    CO_TO_PO = {
        "CO1": ["PO1", "PO2"],
        "CO2": ["PO1", "PO2", "PO3"],
        "CO3": ["PO2", "PO3", "PO4"],
        "CO4": ["PO3", "PO4", "PO5"],
        "CO5": ["PO5", "PO6", "PO8"]
    }
    
    def classify_co(self, text):
        """Returns the most likely CO for a question based on action verbs."""
        text_lower = text.lower()
        
        # Score each CO
        scores = {co: 0 for co in self.CO_KEYWORDS}
        for co, verbs in self.CO_KEYWORDS.items():
            for verb in verbs:
                if verb in text_lower:
                    scores[co] += 1
        
        # If all scores are 0, default to CO2 (Understand)
        best_co = max(scores, key=scores.get)
        if scores[best_co] == 0:
            best_co = "CO2"
        
        return best_co
    
    def get_po_for_co(self, co):
        """Returns the list of POs mapped to a CO."""
        return self.CO_TO_PO.get(co, ["PO1"])
    
    def map_question(self, text):
        """Full mapping: returns {co, po, confidence}."""
        co = self.classify_co(text)
        po = self.get_po_for_co(co)
        return {"co": co, "po": po, "mapped": True}
    
    def map_paper(self, questions):
        """Maps all questions and returns coverage analysis."""
        results = []
        co_distribution = {co: 0 for co in self.CO_KEYWORDS}
        
        for q in questions:
            mapping = self.map_question(q["question_text"])
            co_distribution[mapping["co"]] += 1
            results.append({
                "id": q["id"],
                "co": mapping["co"],
                "po": mapping["po"]
            })
        
        return {
            "questions": results,
            "co_distribution": co_distribution,
            "covered_cos": [co for co, cnt in co_distribution.items() if cnt > 0],
            "uncovered_cos": [co for co, cnt in co_distribution.items() if cnt == 0]
        }