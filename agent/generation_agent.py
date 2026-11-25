
import sys
import os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from tools.generation_tool import GenerationTool
from tools.question_tagging_tool import QuestionTaggingTool
from agent.blueprint_agent import BlueprintAgent
from agent.question_selection_agent import QuestionSelectionAgent


class QuestionGenerationAgent:

    def __init__(self):
        self.name = "Question Generation Agent"
        self.tool = GenerationTool()
        self.tagging_tool = QuestionTaggingTool()
        self.blueprint_agent = BlueprintAgent()
        self.selection_agent = QuestionSelectionAgent()

    def generate_paper(
        self,
        valid_questions,
        lesson_plan,
        bloom_report,
        total_marks,
        marks_per_question,
        exam_type,
        set_name="",
        blueprint=None
    ):

        # 1. Validate total marks
        if (
            not isinstance(total_marks, int)
            or isinstance(total_marks, bool)
            or total_marks <= 0
        ):
            raise ValueError("Total marks must be a positive integer.")

        exam_type = exam_type.strip().upper()
        blueprint = blueprint or self.blueprint_agent.create_blueprint(
            lesson_plan, exam_type, total_marks
        )

        # 2. Prepare question pool
        pool = []
        synthetic_pool = []

        # Generate fallback questions if extracted questions are insufficient
        if len(valid_questions) < 10 and any(
            unit.get("topics") for unit in lesson_plan["units"].values()
        ):

            action_verbs = [
                "Analyze",
                "Explain",
                "Design",
                "Discuss",
                "Evaluate",
                "Compare",
                "Illustrate"
            ]

            for unit_name, unit in lesson_plan["units"].items():
                for verb in action_verbs:
                    for topic in unit.get("topics", []):

                        topic_clean = topic.strip().capitalize()

                        synthetic_q = (
                            f"{verb} the concept of {topic_clean} in detail."
                        )

                        synthetic_pool.append({
                            "id": f"SYN_{len(synthetic_pool)}",
                            "question_text": synthetic_q,
                            "unit": unit_name,
                        })

            for question, tags in zip(
                synthetic_pool,
                self.tagging_tool.tag_questions(
                    synthetic_pool, use_gemini=False
                )
            ):
                question.update(tags)

        # Select a balanced, de-duplicated set before formatting.
        selected_questions = self.selection_agent.select_questions(
            valid_questions, blueprint
        )
        pool.extend(selected_questions)
        pool.extend(synthetic_pool)

        if not pool:
            raise ValueError(
                "No questions available. Please check the lesson plan "
                "and extracted question bank."
            )

        # 3. Modify questions for different sets
        final_pool = []

        for q in pool:

            new_q = dict(q)

            text = new_q.get("question_text", "").strip()

            if not text:
                continue

            if set_name == "Set_B" and not text.startswith("Consider"):
                text = (
                    "Consider a real-world case study and "
                    + text[0].lower()
                    + text[1:]
                )

            elif set_name == "Set_C" and not text.startswith("Illustrate"):
                text = (
                    "Illustrate with a diagram and "
                    + text[0].lower()
                    + text[1:]
                )

            new_q["question_text"] = text

            final_pool.append(new_q)

        if not final_pool:
            raise ValueError(
                "The question pool contains no usable questions."
            )

        selected_units = blueprint["selected_units"]
        questions_per_unit = blueprint["question_counts_by_unit"]
        sub_marks = blueprint["sub_marks"]
        instructions = blueprint["instructions"]

        # 5. Create question paper structure
        paper = {
            "subject": lesson_plan["course"],
            "course_code": lesson_plan.get("course_code", "Auto"),
            "exam_type": exam_type,
            "total_marks": total_marks,
            "duration": "3 Hours" if exam_type == "ESA" else "2 Hours",
            "instructions": instructions,
            "blueprint": blueprint,
            "analysis_summary": (
                f"Dominant Bloom Level: {bloom_report['dominant_level']}"
            ),
            "sections": []
        }

        questions_by_unit = {unit: [] for unit in selected_units}
        unassigned_questions = []
        for question in final_pool:
            unit = self.selection_agent._unit_for(question)
            if unit in questions_by_unit:
                questions_by_unit[unit].append(question)
            else:
                unassigned_questions.append(question)
        fallback_index = 0

        def get_next_q(unit_name):
            nonlocal fallback_index
            if questions_by_unit[unit_name]:
                return questions_by_unit[unit_name].pop(0)
            if unassigned_questions:
                return unassigned_questions.pop(0)
            if not final_pool:
                return None
            question = final_pool[fallback_index % len(final_pool)]
            fallback_index += 1
            return question

        # 6. Generate questions section-wise
        full_q_number = 1

        for unit_name in selected_units:

            section = {
                "unit": unit_name,
                "title": lesson_plan["units"][unit_name]["title"],
                "questions": []
            }

            for q_num_idx in range(questions_per_unit[unit_name]):

                sub_parts = []

                for part_idx in range(2):

                    q = get_next_q(unit_name)

                    if q:

                        sub_parts.append({
                            "q_no": (
                                f"{full_q_number}"
                                f"{chr(97 + part_idx)}"
                            ),
                            "text": q["question_text"],
                            "marks": sub_marks[part_idx],
                            "source_id": q.get("id", "N/A")
                        })
                        for tag in ("bloom", "difficulty", "co", "po"):
                            if tag in q:
                                sub_parts[-1][tag] = q[tag]

                if sub_parts:

                    section["questions"].append({
                        "main_q": str(full_q_number),
                        "sub_questions": sub_parts
                    })

                full_q_number += 1

            paper["sections"].append(section)

        return paper
