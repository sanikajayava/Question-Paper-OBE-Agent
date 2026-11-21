import sys
import os
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.generation_tool import GenerationTool

class QuestionGenerationAgent:
    def __init__(self):
        self.name = "Question Generation Agent"
        self.tool = GenerationTool()

    def generate_paper(self, valid_questions, lesson_plan, bloom_report, total_marks, marks_per_question, exam_type, set_name=""):
        
        # 1. Build a massive pool of questions
        pool = []
        
        # Get all topics from the lesson plan to use as fallback
        all_topics = []
        for unit in lesson_plan["units"].values():
            all_topics.extend(unit.get("topics", []))
        
        # If we don't have enough extracted questions, generate synthetic ones from the syllabus
        if len(valid_questions) < 10 and all_topics:
            action_verbs = ["Analyze", "Explain", "Design", "Discuss", "Evaluate", "Compare", "Illustrate"]
            for verb in action_verbs:
                for topic in all_topics:
                    # Clean up topic name for sentence
                    topic_clean = topic.strip().capitalize()
                    synthetic_q = f"{verb} the concept of {topic_clean} in detail."
                    pool.append({"id": f"SYN_{len(pool)}", "question_text": synthetic_q})
        
        # Add the real extracted questions
        pool.extend(valid_questions)
        
        # 2. Modify based on Set Name
        final_pool = []
        for q in pool:
            new_q = dict(q)
            text = new_q["question_text"]
            if set_name == "Set_B" and not text.startswith("Consider"):
                text = "Consider a real-world case study and " + text[0].lower() + text[1:]
            elif set_name == "Set_C" and not text.startswith("Illustrate"):
                text = "Illustrate with a diagram and " + text[0].lower() + text[1:]
            new_q["question_text"] = text
            final_pool.append(new_q)

        random.shuffle(final_pool)
        
        if exam_type == "ESA":
            instructions = "Answer Five Questions: Any two full questions from each Unit-I & Unit II and one full question from Unit III"
            sub_marks = [10, 10] 
        else:
            marks_per_full_q = total_marks // 2
            instructions = f"Answer any Two full questions. Each full question carries {marks_per_full_q} marks"
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

        def get_next_q():
            nonlocal q_index
            if not final_pool: return None
            if q_index >= len(final_pool):
                q_index = 0
            q = final_pool[q_index]
            q_index += 1
            return q

        # 3. Generate the sections
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