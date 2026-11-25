class BlueprintAgent:
    """Build an exam blueprint from the selected exam pattern."""

    BLOOM_TARGETS = {
        "L1_Remember": 15,
        "L2_Understand": 25,
        "L3_Apply": 25,
        "L4_Analyze": 20,
        "L5_Evaluate": 10,
        "L6_Create": 5,
    }

    def create_blueprint(self, lesson_plan, exam_type, total_marks):
        exam_type = exam_type.strip().upper()
        units = list(lesson_plan.get("units", {}))

        if exam_type == "ESA":
            patterns = {
                60: {
                    "required_units": 2,
                    "questions_per_unit": [3, 3],
                    "sub_marks": [8, 7],
                    "instructions": (
                        "Answer any TWO questions from Unit I and "
                        "any TWO questions from Unit II."
                    ),
                },
                100: {
                    "required_units": 3,
                    "questions_per_unit": [3, 3, 2],
                    "sub_marks": [10, 10],
                    "instructions": (
                        "Answer any TWO questions from Unit I, "
                        "any TWO questions from Unit II, and "
                        "any ONE question from Unit III."
                    ),
                },
            }
            if total_marks not in patterns:
                raise ValueError(
                    f"The ESA pattern for {total_marks} marks has not been "
                    "configured yet. Currently supported ESA patterns are "
                    "60 and 100 marks."
                )
            blueprint = patterns[total_marks]
            if len(units) < blueprint["required_units"]:
                raise ValueError(
                    f"This ESA pattern requires "
                    f"{blueprint['required_units']} units, but the lesson "
                    f"plan contains only {len(units)} units."
                )
            selected_units = units[:blueprint["required_units"]]
        elif exam_type in {"ISA1", "ISA2"}:
            if total_marks % 2:
                raise ValueError(
                    "ISA total marks must be an even number because students "
                    "answer two full questions."
                )
            if len(units) < 2:
                raise ValueError(
                    "The lesson plan must contain at least two units for ISA "
                    "question-paper generation."
                )
            selected_units = [units[0] if exam_type == "ISA1" else units[1]]
            marks_per_full_q = total_marks // 2
            blueprint = {
                "questions_per_unit": [3],
                "sub_marks": [
                    (marks_per_full_q + 1) // 2,
                    marks_per_full_q // 2,
                ],
                "instructions": "Answer any TWO full questions.",
            }
        else:
            raise ValueError("Invalid exam type. Use ISA1, ISA2 or ESA.")

        total_selected_questions = sum(blueprint["questions_per_unit"])
        unit_weightage = {}
        remaining_weight = 100.0
        for index, unit in enumerate(selected_units):
            weight = (
                round(remaining_weight, 2)
                if index == len(selected_units) - 1
                else round(100 / len(selected_units), 2)
            )
            unit_weightage[unit] = weight
            remaining_weight -= weight
        blueprint.update(
            {
                "exam_type": exam_type,
                "total_marks": total_marks,
                "selected_units": selected_units,
                "bloom_targets": dict(self.BLOOM_TARGETS),
                "unit_weightage": unit_weightage,
                "question_counts_by_unit": dict(
                    zip(selected_units, blueprint["questions_per_unit"])
                ),
                "required_question_count": total_selected_questions * 2,
            }
        )
        if exam_type in {"ISA1", "ISA2"}:
            blueprint["question_counts_by_unit"] = {
                selected_units[0]: blueprint["questions_per_unit"][0]
            }
        return blueprint
