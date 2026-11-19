import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.generation_tool import GenerationTool

class QuestionGenerationAgent:
    def __init__(self):
        self.name = "Question Generation Agent"
        self.tool = GenerationTool()

    def generate_paper(self, valid_questions, lesson_plan, bloom_report, total_marks, marks_per_question, exam_type):
        print(f"\n[{self.name}] Structuring {exam_type} paper for {total_marks} marks...")
        
        # Dynamic Marks Calculation
        if exam_type == "ESA":
            instructions = "Note: Answer Five Questions: Any two full questions from each Unit-I & Unit II and one full question from Unit III"
            sub_marks = [10, 10] # 10+10 = 20 per Q. Student answers 5 Qs = 100 Marks.
        else:
            # For ISA, student answers 2 questions. So each question is total_marks / 2.
            marks_per_full_q = total_marks // 2
            instructions = f"Note: Answer any Two full questions. Each full question carries {marks_per_full_q} marks"
            # Split the full marks into 'a' and 'b'
            sub_marks = [(marks_per_full_q // 2) + (marks_per_full_q % 2), marks_per_full_q // 2]

        paper = {
            "subject": lesson_plan["course"],
            "course_code": lesson_plan.get("course_code", "Auto"),
            "exam_type": exam_type,
            "total_marks": total_marks,
            "duration": "3 Hours" if exam_type == "ESA" else "2 Hours",
            "instructions": instructions,
            "analysis_summary": f"Dominant Bloom Level: {bloom_report['dominant_level']}",
            "sections": []
        }

        q_index = 0
        used_qs = []

        def get_next_q():
            nonlocal q_index
            if q_index < len(valid_questions):
                q = valid_questions[q_index]
                q_index += 1
                used_qs.append(q)
                return q
            else:
                if used_qs:
                    q = used_qs[q_index % len(used_qs)]
                    q_index += 1
                    return q
                return None

        if exam_type == "ESA":
            units = list(lesson_plan["units"].keys())
            questions_per_unit = [3, 3, 2]
            
            for i, unit_name in enumerate(units[:3]): 
                section = {"unit": unit_name, "title": lesson_plan["units"][unit_name]["title"], "questions": []}
                
                for q_num_idx in range(questions_per_unit[i]):
                    full_q_num = sum(questions_per_unit[:i]) + q_num_idx + 1
                    sub_parts = []
                    
                    for part_idx in range(2): 
                        q = get_next_q()
                        if q:
                            sub_parts.append({
                                "q_no": f"{full_q_num}{chr(97 + part_idx)}",
                                "text": q["question_text"],
                                "marks": sub_marks[part_idx],
                                "source_id": q["id"]
                            })
                    
                    if sub_parts:
                        section["questions"].append({"main_q": str(full_q_num), "sub_questions": sub_parts})
                paper["sections"].append(section)

        else:
            target_unit_name = list(lesson_plan["units"].keys())[0] if exam_type == "ISA1" else list(lesson_plan["units"].keys())[1]
            section = {"unit": target_unit_name, "title": lesson_plan["units"][target_unit_name]["title"], "questions": []}
            
            for full_q_num in range(1, 4): 
                sub_parts = []
                for part_idx in range(2):
                    q = get_next_q()
                    if q:
                        sub_parts.append({
                            "q_no": f"{full_q_num}{chr(97 + part_idx)}",
                            "text": q["question_text"],
                            "marks": sub_marks[part_idx],
                            "source_id": q["id"]
                        })
                
                if sub_parts:
                    section["questions"].append({"main_q": str(full_q_num), "sub_questions": sub_parts})
            
            paper["sections"].append(section)

        return paper