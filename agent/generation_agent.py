import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.generation_tool import GenerationTool

class QuestionGenerationAgent:
    def __init__(self):
        self.name = "Question Generation Agent"
        self.tool = GenerationTool()  # <-- AGENT USES TOOL

    def generate_paper(self, valid_questions, lesson_plan, analysis_report, total_marks=100):
        print(f"\n[{self.name}] Using GenerationTool for {total_marks} marks...")
        
        marks_per_question = 10
        questions_needed = total_marks // marks_per_question

        # AGENT CALLS TOOL - clean + format
        cleaned_questions = []
        for q in valid_questions:
            clean = self.tool.clean_text(q["question_text"])  # AGENT CALLS TOOL
            if len(clean) > 50:
                cleaned_questions.append({"id": q["id"], "text": clean})

        selected = cleaned_questions[:questions_needed]
        
        print(f"  -> Available: {len(cleaned_questions)}, Needed: {questions_needed}, Selected: {len(selected)}")
        if len(selected) < questions_needed:
            print(f"  [!] WARNING: Database lacks enough questions for full {total_marks} marks.")

        paper = {
            "subject": lesson_plan["course"],
            "total_marks": total_marks,
            "duration": "3 Hours",
            "instructions": "Answer all questions. All questions carry equal marks.",
            "analysis_summary": analysis_report["pattern_summary"],
            "sections": []
        }

        units = list(lesson_plan["units"].keys())
        num_units = len(units)
        
        for i, unit_name in enumerate(units):
            section = {
                "unit": unit_name,
                "title": lesson_plan["units"][unit_name]["title"],
                "questions": []
            }
            for j in range(i, len(selected), num_units):
                if j < len(selected):
                    q = selected[j]
                    # AGENT CALLS TOOL - format_question
                    formatted = self.tool.format_question(q["text"], marks_per_question)
                    section["questions"].append({
                        "question_number": f"{i+1}.{len(section['questions'])+1}",
                        "text": q["text"],
                        "formatted": formatted,
                        "marks": marks_per_question,
                        "source_id": q["id"]
                    })
            paper["sections"].append(section)

        print(f"[{self.name}] Tool-based generation complete.")
        return paper