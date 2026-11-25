from collections import Counter
import re

from tools.analysis_tool import AnalysisTool
from tools.copo_tool import COPOTool


class DifficultyCoverageAgent:
    """Estimate difficulty and summarize Bloom, CO, and unit coverage."""

    DIFFICULTY_KEYWORDS = {
        "Easy": {"define", "list", "name", "state", "identify", "describe"},
        "Hard": {"design", "evaluate", "justify", "derive", "optimize", "critique"},
    }

    def __init__(self):
        self.analysis_tool = AnalysisTool()
        self.copo_tool = COPOTool()

    def _difficulty(self, text):
        words = set(re.findall(r"[a-z0-9]+", text.lower()))
        easy_score = len(words & self.DIFFICULTY_KEYWORDS["Easy"])
        hard_score = len(words & self.DIFFICULTY_KEYWORDS["Hard"])
        if hard_score > easy_score:
            return "Hard"
        if easy_score > hard_score:
            return "Easy"
        return "Medium"

    def analyze(self, questions, blueprint=None):
        bloom = Counter()
        difficulty = Counter()
        outcomes = Counter()
        units = Counter()

        for question in questions:
            text = question.get("text", question.get("question_text", ""))
            bloom[question.get("bloom") or self.analysis_tool.classify_bloom(text)] += 1
            difficulty[question.get("difficulty") or self._difficulty(text)] += 1
            outcomes[question.get("CO") or question.get("co") or
                     self.copo_tool.classify_co(text)] += 1
            unit = question.get("unit")
            if unit:
                units[unit] += 1

        return {
            "question_count": len(questions),
            "bloom_distribution": dict(bloom),
            "difficulty_distribution": dict(difficulty),
            "co_distribution": dict(outcomes),
            "unit_distribution": dict(units),
            "covered_cos": sorted(outcomes),
            "uncovered_cos": [
                f"CO{index}" for index in range(1, 6)
                if f"CO{index}" not in outcomes
            ],
            "blueprint": blueprint or {},
        }
