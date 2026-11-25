import json
import os
import re

from agent.difficulty_coverage_agent import DifficultyCoverageAgent
from tools.analysis_tool import AnalysisTool
from tools.copo_tool import COPOTool


class QuestionTaggingTool:
    """Tag questions with rules, optionally enhanced by Gemini."""

    def __init__(self):
        self.analysis_tool = AnalysisTool()
        self.copo_tool = COPOTool()
        self.difficulty_agent = DifficultyCoverageAgent()

    def _rule_tags(self, text):
        return {
            "bloom": self.analysis_tool.classify_bloom(text),
            "difficulty": self.difficulty_agent._difficulty(text),
            "co": self.copo_tool.classify_co(text),
            "po": self.copo_tool.get_po_for_co(
                self.copo_tool.classify_co(text)
            ),
        }

    def tag_questions(self, questions, use_gemini=True):
        rule_tags = [self._rule_tags(q.get("question_text", "")) for q in questions]
        api_key = os.getenv("GEMINI_API_KEY")
        if not use_gemini or not api_key or not questions:
            return rule_tags

        from google import genai

        client = genai.Client(api_key=api_key)
        prompt_items = [
            {"id": q.get("id", str(index)), "text": q.get("question_text", "")}
            for index, q in enumerate(questions)
        ]
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            contents=(
                "Classify each exam question. Return only a JSON array with "
                "objects containing id, bloom (one of L1_Remember, "
                "L2_Understand, L3_Apply, L4_Analyze, L5_Evaluate, "
                "L6_Create), difficulty (Easy, Medium, Hard), co (CO1-CO5), "
                "and po (array of PO labels). Do not rewrite questions.\n"
                + json.dumps(prompt_items, ensure_ascii=False)
            ),
        )

        try:
            model_tags = json.loads(response.text)
        except (TypeError, json.JSONDecodeError) as error:
            raise ValueError("Gemini returned invalid question-tag JSON.") from error
        if not isinstance(model_tags, list):
            raise ValueError("Gemini question tags must be a JSON array.")

        by_id = {
            str(item.get("id")): item
            for item in model_tags
            if isinstance(item, dict) and item.get("id") is not None
        }
        expected_ids = {
            str(question.get("id", index))
            for index, question in enumerate(questions)
        }
        if len(by_id) != len(questions) or set(by_id) != expected_ids:
            raise ValueError(
                "Gemini did not return exactly one tag record per question."
            )
        merged = []
        for index, question in enumerate(questions):
            model = by_id.get(str(question.get("id", index)), {})
            bloom = model.get("bloom")
            difficulty = model.get("difficulty")
            co = model.get("co")
            po = model.get("po")
            if (
                bloom not in self.analysis_tool.BLOOM_LEVELS
                or difficulty not in {"Easy", "Medium", "Hard"}
                or co not in self.copo_tool.CO_KEYWORDS
                or not isinstance(po, list)
                or not po
                or not all(
                    isinstance(item, str)
                    and re.fullmatch(r"PO(?:[1-9]|1[0-2])", item)
                    for item in po
                )
            ):
                raise ValueError(
                    f"Gemini returned invalid tags for question "
                    f"{question.get('id', index)}."
                )
            merged.append({
                "bloom": bloom,
                "difficulty": difficulty,
                "co": co,
                "po": po,
            })
        return merged
