class QuestionPaperSkill:
    """
    Reusable skill for creating a question-paper blueprint
    and formatting the paper structure.
    """

    def create_blueprint(self, criteria):
        """Create a reusable blueprint from examination criteria."""
        return {
            "total_marks": criteria.get("total_marks"),
            "duration": criteria.get("duration"),
            "unit_weightage": criteria.get("unit_weightage"),
            "bloom_distribution": criteria.get("bloom_distribution"),
            "question_type_mix": criteria.get("question_type_mix")
        }

    def format_question(self, question_number, question):
        """Format a selected question for the question paper."""
        return (
            f"{question_number}. "
            f"{question['question']} "
            f"[{question['marks']} Marks | {question['bloom']}]"
        )

    def format_paper(self, questions):
        """Format a list of selected questions."""
        formatted_questions = []

        for number, question in enumerate(questions, start=1):
            formatted_questions.append(
                self.format_question(number, question)
            )

        return "\n".join(formatted_questions)

if __name__ == "__main__":
    skill = QuestionPaperSkill()

    sample_questions = [
        {
            "question": "What is an AI agent?",
            "marks": 5,
            "bloom": "L1"
        },
        {
            "question": "Explain the role of tools in an AI agent.",
            "marks": 10,
            "bloom": "L2"
        }
    ]

    print("===== FORMATTED QUESTIONS =====")
    print(skill.format_paper(sample_questions))