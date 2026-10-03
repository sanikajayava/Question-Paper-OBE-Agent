from tools.question_bank_tool import read_question_bank


class QuestionPaperCoordinator:
    """
    Coordinator Agent for the Question Paper Setting
    and OBE Analysis System.
    """

    def understand_request(self, faculty_request):
        """Understand the faculty's request."""
        if not faculty_request or not faculty_request.strip():
            return {
                "status": "error",
                "message": "Please provide a question paper request."
            }

        return {
            "status": "success",
            "goal": faculty_request.strip()
        }

    def create_plan(self, goal):
        """Break the goal into smaller tasks."""
        return [
            "Read faculty examination criteria",
            "Retrieve questions from the question bank",
            "Select questions based on marks, units and Bloom levels",
            "Validate the generated question paper",
            "Prepare the scheme of valuation",
            "Perform OBE analysis",
            "Submit the paper for faculty approval"
        ]

    def retrieve_questions(self):
        """Retrieve questions using the question bank tool."""
        return read_question_bank()

    def run(self, faculty_request):
        """Coordinate the question paper generation workflow."""
        understanding = self.understand_request(faculty_request)

        if understanding["status"] == "error":
            return understanding

        plan = self.create_plan(understanding["goal"])
        question_bank_result = self.retrieve_questions()

        return {
    "agent": "Question Paper Coordinator",
    "goal": understanding["goal"],
    "status": "plan_created",
    "task_plan": plan,
    "question_bank_status": question_bank_result["status"],
    "question_count": question_bank_result.get("count", 0)
}