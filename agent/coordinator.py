from tools.question_bank_tool import read_question_bank
from skills.question_paper_skill import QuestionPaperSkill
from memory.memory_manager import MemoryManager

class QuestionPaperCoordinator:
    """
    Coordinator Agent for the Question Paper Setting
    and OBE Analysis System.
    """
    def __init__(self):
        self.question_paper_skill = QuestionPaperSkill()
        self.memory_manager = MemoryManager()
    

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

    def create_blueprint(self, criteria):
        """Create a question-paper blueprint using the reusable skill."""
        return self.question_paper_skill.create_blueprint(criteria)        
        
    def retrieve_past_papers(self, tag):
        """Retrieve past papers from memory using a tag."""
        return self.memory_manager.retrieve_by_tag(tag)

    def run(self, faculty_request):
        """Coordinate the question paper generation workflow."""
        understanding = self.understand_request(faculty_request)

        if understanding["status"] == "error":
            return understanding

        plan = self.create_plan(understanding["goal"])
        question_bank_result = self.retrieve_questions()
        past_papers = self.retrieve_past_papers("agents")

        blueprint = self.create_blueprint({
            "total_marks": 50,
            "duration": "2 Hours",
            "unit_weightage": {
                "Unit 1": 20,
                "Unit 2": 20,
                "Unit 3": 20,
                "Unit 4": 20,
                "Unit 5": 20
            },
            "bloom_distribution": {
                "L1": 30,
                "L2": 40,
                "L3": 30
            },
            "question_type_mix": {
                "short": 40,
                "long": 60
            }
        })

        return {
            "agent": "Question Paper Coordinator",
            "goal": understanding["goal"],
            "status": "plan_created",
            "task_plan": plan,
            "question_bank_status": question_bank_result["status"],
            "question_count": question_bank_result.get("count", 0),
            "blueprint": blueprint,
            "past_papers": past_papers
        }
 