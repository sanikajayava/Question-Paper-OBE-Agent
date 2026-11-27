import os
import json
import unittest
import uuid
from unittest.mock import patch

from agent.blueprint_agent import BlueprintAgent
from agent.difficulty_coverage_agent import DifficultyCoverageAgent
from agent.generation_agent import QuestionGenerationAgent
from agent.question_selection_agent import QuestionSelectionAgent
from tools.question_tagging_tool import QuestionTaggingTool
from tools.vector_question_bank import VectorQuestionBank


class ObeAgentTests(unittest.TestCase):
    def test_blueprint_allocates_supported_esa_and_isa_patterns(self):
        lesson_plan = {
            "units": {
                "Unit 1": {},
                "Unit 2": {},
                "Unit 3": {},
            }
        }
        agent = BlueprintAgent()

        esa = agent.create_blueprint(lesson_plan, "ESA", 100)
        self.assertEqual(esa["required_question_count"], 16)
        self.assertEqual(esa["selected_units"], ["Unit 1", "Unit 2", "Unit 3"])
        self.assertAlmostEqual(sum(esa["unit_weightage"].values()), 100)

        isa = agent.create_blueprint(lesson_plan, "ISA1", 30)
        self.assertEqual(isa["selected_units"], ["Unit 1"])
        self.assertEqual(isa["sub_marks"], [8, 7])

    def test_question_selection_deduplicates_and_spreads_units(self):
        questions = [
            {"id": "Q_Unit1_1", "question_text": "Define neural networks."},
            {"id": "Q_Unit1_2", "question_text": "Explain neural training."},
            {"id": "Q_Unit2_1", "question_text": "Apply convolution filters."},
            {"id": "Q_Unit2_2", "question_text": "Design a neural architecture."},
            {"id": "Q_Unit2_3", "question_text": "Define neural networks."},
        ]
        blueprint = {
            "selected_units": ["Unit 1", "Unit 2"],
            "required_question_count": 4,
            "bloom_targets": {},
        }

        selected = QuestionSelectionAgent().select_questions(
            questions, blueprint
        )
        self.assertEqual(len(selected), 4)
        self.assertEqual(len({q["question_text"] for q in selected}), 4)
        self.assertEqual(
            {QuestionSelectionAgent._unit_for(q) for q in selected},
            {"Unit 1", "Unit 2"},
        )

    def test_difficulty_report_includes_uncovered_outcomes(self):
        report = DifficultyCoverageAgent().analyze(
            [{"text": "Design and evaluate a scalable system.", "CO": "CO5"}]
        )
        self.assertEqual(report["difficulty_distribution"], {"Hard": 1})
        self.assertIn("CO1", report["uncovered_cos"])
        self.assertEqual(report["covered_cos"], ["CO5"])

    def test_rule_tagger_works_without_gemini_key(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": ""}):
            tags = QuestionTaggingTool().tag_questions(
                [{"id": "Q1", "question_text": "Design a neural network."}]
            )
        self.assertEqual(tags[0]["bloom"], "L6_Create")
        self.assertEqual(tags[0]["difficulty"], "Hard")
        self.assertIn("co", tags[0])

    def test_gemini_tags_are_used_after_schema_validation(self):
        response = type("Response", (), {
            "text": json.dumps([{
                "id": "Q1",
                "bloom": "L6_Create",
                "difficulty": "Hard",
                "co": "CO4",
                "po": ["PO3"],
            }])
        })()
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}), \
                patch("google.genai.Client") as client_class:
            client_class.return_value.models.generate_content.return_value = response
            tags = QuestionTaggingTool().tag_questions(
                [{"id": "Q1", "question_text": "Design a neural network."}]
            )
        self.assertEqual(tags[0]["co"], "CO4")
        self.assertEqual(tags[0]["po"], ["PO3"])

    def test_local_vector_embedding_is_normalized_and_repeatable(self):
        first = VectorQuestionBank._embedding("neural network design")
        second = VectorQuestionBank._embedding("neural network design")
        self.assertEqual(first, second)
        self.assertAlmostEqual(sum(value * value for value in first), 1.0)

    def test_chroma_indexes_and_returns_questions_with_local_embeddings(self):
        store = VectorQuestionBank()
        question_id = f"TEST_{uuid.uuid4().hex}"
        try:
            store.index_questions([
                {
                    "id": question_id,
                    "subject": "AI",
                    "exam_type": "ESA",
                    "batch": "2025",
                    "question_text": (
                        f"Explain neural network training test {question_id}."
                    ),
                },
            ])
            matches = store.search(
                f"neural network training test {question_id}", limit=1
            )
            self.assertEqual(matches[0]["id"], question_id)
        finally:
            store.collection.delete(ids=[question_id])

    def test_paper_generation_preserves_tags_and_blueprint_allocation(self):
        lesson = {
            "course": "Test Subject",
            "course_code": "T1",
            "units": {
                "Unit 1": {"title": "One", "topics": ["neural networks"]},
                "Unit 2": {"title": "Two", "topics": ["optimization"]},
                "Unit 3": {"title": "Three", "topics": ["deployment"]},
            },
        }
        questions = [
            {
                "id": f"Q_Unit{unit}_{index}",
                "question_text": (
                    f"Explain neural network architecture and training "
                    f"approaches with detailed examples, set {index}."
                ),
                "bloom": "L2_Understand",
                "difficulty": "Medium",
                "co": "CO2",
                "po": ["PO1"],
            }
            for unit in range(1, 4)
            for index in range(3)
        ]

        paper = QuestionGenerationAgent().generate_paper(
            questions,
            lesson,
            {"dominant_level": "L2_Understand"},
            100,
            10,
            "ESA",
        )
        subquestions = [
            question
            for section in paper["sections"]
            for main_question in section["questions"]
            for question in main_question["sub_questions"]
        ]
        self.assertEqual(len(subquestions), 16)
        self.assertEqual(len(paper["blueprint"]["selected_units"]), 3)
        self.assertTrue(all(question.get("bloom") for question in subquestions))
        self.assertTrue(all(question.get("difficulty") for question in subquestions))
        units_used = {
            QuestionSelectionAgent._unit_for({"id": question["source_id"]})
            for section in paper["sections"]
            for main_question in section["questions"]
            for question in main_question["sub_questions"]
            if QuestionSelectionAgent._unit_for({"id": question["source_id"]})
        }
        self.assertTrue(units_used)
        self.assertTrue(units_used.issubset(set(paper["blueprint"]["selected_units"])))

    def test_paper_duration_matches_total_marks(self):
        lesson = {
            "course": "Test Subject",
            "units": {
                "Unit 1": {"title": "One", "topics": ["neural networks"]},
                "Unit 2": {"title": "Two", "topics": ["optimization"]},
            },
        }
        expected_durations = {
            30: "60 Minutes",
            40: "75 Minutes",
            60: "2 Hours",
            100: "3 Hours",
        }

        for total_marks, expected_duration in expected_durations.items():
            with self.subTest(total_marks=total_marks):
                paper = QuestionGenerationAgent().generate_paper(
                    [],
                    lesson,
                    {"dominant_level": "L2_Understand"},
                    total_marks,
                    10,
                    "ISA1",
                )
                self.assertEqual(paper["duration"], expected_duration)


if __name__ == "__main__":
    unittest.main()
