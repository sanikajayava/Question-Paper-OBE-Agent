import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.retrieval_tool import RetrievalTool

class QuestionRetrievalAgent:
    def __init__(self):
        self.name = "Question Retrieval Agent"
        self.tool = RetrievalTool()

    def retrieve_questions(self, subject, exam_type, target_batch, lesson_plan_data):
        print(f"\n[{self.name}] Filtering questions for: {exam_type}")
        
        valid_questions = []
        
        # 1. Map Exam Type to Target Unit
        if exam_type == "ISA1":
            target_unit = "Unit 1"
        elif exam_type == "ISA2":
            target_unit = "Unit 2"
        else:
            target_unit = None # ESA gets all units

        # 2. Extract questions from the Lesson Plan data structure
        for unit_name, unit_data in lesson_plan_data["units"].items():
            if target_unit and unit_name != target_unit:
                continue # Skip other units for ISA
                
            for idx, text in enumerate(unit_data["questions"]):
                valid_questions.append({
                    "id": f"Q_{unit_name.replace(' ', '')}_{idx}",
                    "question_text": text
                })
                
        print(f"[{self.name}] Extracted {len(valid_questions)} questions for this exam.")
        return valid_questions