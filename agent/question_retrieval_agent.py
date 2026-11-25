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
                    "question_text": text,
                    "unit": unit_name,
                })

        if os.getenv("ENABLE_VECTOR_RETRIEVAL", "1").strip().lower() not in {
            "0", "false", "no"
        }:
            known_text = {
                question["question_text"].strip().lower()
                for question in valid_questions
            }
            for unit_name, unit_data in lesson_plan_data["units"].items():
                if target_unit and unit_name != target_unit:
                    continue
                query_text = " ".join(unit_data.get("topics", [])) or " ".join(
                    unit_data.get("questions", [])
                )
                if not query_text:
                    continue
                semantic_questions = self.tool.semantic_query(
                    query_text,
                    subject,
                    exam_type,
                    target_batch,
                )
                for question in semantic_questions:
                    text = question["question_text"].strip()
                    if text.lower() in known_text:
                        continue
                    question["id"] = (
                        f"VEC_{unit_name.replace(' ', '')}_{question['id']}"
                    )
                    question["unit"] = unit_name
                    valid_questions.append(question)
                    known_text.add(text.lower())
                
        print(f"[{self.name}] Extracted {len(valid_questions)} questions for this exam.")
        return valid_questions