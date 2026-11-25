import re

from tools.analysis_tool import AnalysisTool
from tools.copo_tool import COPOTool


class QuestionSelectionAgent:
    """Rank questions for topic coverage and balanced cognitive levels."""

    def __init__(self):
        self.analysis_tool = AnalysisTool()
        self.copo_tool = COPOTool()

    @staticmethod
    def _unit_for(question):
        if question.get("unit"):
            return question["unit"]
        match = re.search(
            r"unit[\s_-]*([0-9]+|[ivx]+)", question.get("id", ""), re.I
        )
        if not match:
            return None
        number = match.group(1)
        if number.lower() in {"i", "ii", "iii", "iv", "v"}:
            number = str({"i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5}[number.lower()])
        return f"Unit {number}"

    def select_questions(self, questions, blueprint):
        target_count = blueprint.get("required_question_count", len(questions))
        target_bloom = {
            level: target_count * percentage / 100
            for level, percentage in blueprint.get("bloom_targets", {}).items()
        }
        selected_units = set(blueprint.get("selected_units", []))
        seen = set()
        candidates = []

        for question in questions:
            text = question.get("question_text", "").strip()
            normalized = re.sub(r"\W+", " ", text.lower()).strip()
            if not normalized or normalized in seen:
                continue
            unit = self._unit_for(question)
            if selected_units and unit and unit not in selected_units:
                continue
            seen.add(normalized)
            bloom = question.get("bloom") or self.analysis_tool.classify_bloom(text)
            co = question.get("co") or self.copo_tool.classify_co(text)
            candidates.append((question, unit, bloom, co))

        if not candidates:
            return []

        # Round-robin across units, then prefer underrepresented Bloom levels
        # and COs. This avoids selecting only one unit or one outcome.
        unit_groups = {}
        for candidate in candidates:
            unit_groups.setdefault(candidate[1] or "Unspecified", []).append(candidate)

        selected = []
        bloom_counts = {level: 0 for level in target_bloom}
        co_counts = {}
        while len(selected) < min(target_count, len(candidates)):
            progressed = False
            for group in unit_groups.values():
                if not group or len(selected) >= target_count:
                    continue
                candidate = max(
                    group,
                    key=lambda item: (
                        target_bloom.get(item[2], 0) - bloom_counts.get(item[2], 0),
                        -co_counts.get(item[3], 0),
                    ),
                )
                group.remove(candidate)
                selected.append(candidate)
                bloom_counts[candidate[2]] = bloom_counts.get(candidate[2], 0) + 1
                co_counts[candidate[3]] = co_counts.get(candidate[3], 0) + 1
                progressed = True
            if not progressed:
                break

        return [item[0] for item in selected]
