
import sys
import os
import random

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from tools.generation_tool import GenerationTool


class QuestionGenerationAgent:

    def __init__(self):
        self.name = "Question Generation Agent"
        self.tool = GenerationTool()

    def generate_paper(
        self,
        valid_questions,
        lesson_plan,
        bloom_report,
        total_marks,
        marks_per_question,
        exam_type,
        set_name=""
    ):

        # 1. Validate total marks
        if (
            not isinstance(total_marks, int)
            or isinstance(total_marks, bool)
            or total_marks <= 0
        ):
            raise ValueError("Total marks must be a positive integer.")

        exam_type = exam_type.strip().upper()

        if exam_type not in ["ISA1", "ISA2", "ESA"]:
            raise ValueError(
                "Invalid exam type. Use ISA1, ISA2 or ESA."
            )

        # 2. Prepare question pool
        pool = []

        all_topics = []

        for unit in lesson_plan["units"].values():
            all_topics.extend(unit.get("topics", []))

        # Generate fallback questions if extracted questions are insufficient
        if len(valid_questions) < 10 and all_topics:

            action_verbs = [
                "Analyze",
                "Explain",
                "Design",
                "Discuss",
                "Evaluate",
                "Compare",
                "Illustrate"
            ]

            for verb in action_verbs:
                for topic in all_topics:

                    topic_clean = topic.strip().capitalize()

                    synthetic_q = (
                        f"{verb} the concept of {topic_clean} in detail."
                    )

                    pool.append({
                        "id": f"SYN_{len(pool)}",
                        "question_text": synthetic_q
                    })

        # Add extracted questions
        pool.extend(valid_questions)

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

        random.shuffle(final_pool)

        # 4. Configure marks and examination pattern

        if exam_type == "ESA":

            # 60-mark ESA: Unit I and Unit II
            if total_marks == 60:

                required_units = 2
                questions_per_unit = [3, 3]

                sub_marks = [8, 7]

                instructions = (
                    "Answer any TWO questions from Unit I and "
                    "any TWO questions from Unit II."
                )

            # 100-mark ESA: Unit I, Unit II and Unit III
            elif total_marks == 100:

                required_units = 3
                questions_per_unit = [3, 3, 2]

                sub_marks = [10, 10]

                instructions = (
                    "Answer any TWO questions from Unit I, "
                    "any TWO questions from Unit II, and "
                    "any ONE question from Unit III."
                )

            else:

                raise ValueError(
                    f"The ESA pattern for {total_marks} marks "
                    "has not been configured yet. "
                    "Currently supported ESA patterns are 60 and 100 marks."
                )

            available_units = list(lesson_plan["units"].keys())

            if len(available_units) < required_units:
                raise ValueError(
                    f"This ESA pattern requires {required_units} units, "
                    f"but the lesson plan contains only "
                    f"{len(available_units)} units."
                )

            selected_units = available_units[:required_units]

        else:

            # ISA: Answer any TWO out of THREE full questions

            if total_marks % 2 != 0:
                raise ValueError(
                    "ISA total marks must be an even number "
                    "because students answer two full questions."
                )

            marks_per_full_q = total_marks // 2

            # Divide each full question into two subquestions
            sub_marks = [
                (marks_per_full_q + 1) // 2,
                marks_per_full_q // 2
            ]

            questions_per_unit = [3]

            available_units = list(lesson_plan["units"].keys())

            if len(available_units) < 2:
                raise ValueError(
                    "The lesson plan must contain at least two units "
                    "for ISA question-paper generation."
                )

            target_unit_name = (
                available_units[0]
                if exam_type == "ISA1"
                else available_units[1]
            )

            selected_units = [target_unit_name]

            instructions = "Answer any TWO full questions."

        # 5. Create question paper structure
        paper = {
            "subject": lesson_plan["course"],
            "course_code": lesson_plan.get("course_code", "Auto"),
            "exam_type": exam_type,
            "total_marks": total_marks,
            "duration": "3 Hours" if exam_type == "ESA" else "2 Hours",
            "instructions": instructions,
            "analysis_summary": (
                f"Dominant Bloom Level: {bloom_report['dominant_level']}"
            ),
            "sections": []
        }

        q_index = 0

        def get_next_q():

            nonlocal q_index

            if not final_pool:
                return None

            if q_index >= len(final_pool):
                q_index = 0

            q = final_pool[q_index]

            q_index += 1

            return q

        # 6. Generate questions section-wise
        full_q_number = 1

        for unit_index, unit_name in enumerate(selected_units):

            section = {
                "unit": unit_name,
                "title": lesson_plan["units"][unit_name]["title"],
                "questions": []
            }

            for q_num_idx in range(questions_per_unit[unit_index]):

                sub_parts = []

                for part_idx in range(2):

                    q = get_next_q()

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

                if sub_parts:

                    section["questions"].append({
                        "main_q": str(full_q_number),
                        "sub_questions": sub_parts
                    })

                full_q_number += 1

            paper["sections"].append(section)

        return paper
