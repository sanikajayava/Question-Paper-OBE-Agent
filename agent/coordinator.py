import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.lesson_plan_agent import LessonPlanAgent
from agent.question_retrieval_agent import QuestionRetrievalAgent
from agent.past_paper_agent import PastPaperAnalysisAgent
from agent.validation_agent import ValidationAgent
from agent.generation_agent import QuestionGenerationAgent
from agent.bloom_taxonomy_agent import BloomTaxonomyAgent
from tools.copo_tool import COPOTool
from tools.pdf_generator_tool import PDFGeneratorTool

class QuestionPaperCoordinator:
    def __init__(self):
        self.name = "Question Paper Coordinator"
        self.lp_agent = LessonPlanAgent()
        self.retrieval_agent = QuestionRetrievalAgent()
        self.analysis_agent = PastPaperAnalysisAgent()
        self.bloom_agent = BloomTaxonomyAgent()
        self.validation_agent = ValidationAgent()
        self.generation_agent = QuestionGenerationAgent()
        self.copo_tool = COPOTool()
        self.pdf_tool = PDFGeneratorTool()

    def run_workflow(self, subject, exam_type, target_batch, lesson_plan_path, total_marks=100):
        print(f"\n{'='*60}")
        print(f"  {self.name.upper()}")
        print(f"  Goal: Generate a {exam_type} paper for {subject}")
        print(f"  Total Marks: {total_marks}")
        print(f"{'='*60}")

        # 1. Read Lesson Plan and Extract Questions per Unit
        lesson_plan = self.lp_agent.read_lesson_plan(lesson_plan_path)
        if not lesson_plan: 
            return

        # 2. Retrieve Questions (Filtered by Unit based on Exam Type)
        retrieved = self.retrieval_agent.retrieve_questions(subject, exam_type, target_batch, lesson_plan)
        if not retrieved: 
            return

        # 3. Analyze
        analysis = self.analysis_agent.analyze(retrieved)
        bloom_report = self.bloom_agent.analyze(retrieved)

        # 4. Validate
        valid_qs, _ = self.validation_agent.validate_questions(retrieved, subject)
        if not valid_qs: 
            return

        # 5. CO/PO Map
        print(f"\n[{self.name}] Performing CO/PO Mapping...")
        copo_report = self.copo_tool.map_paper(valid_qs)
        copo_by_id = {item["id"]: item for item in copo_report["questions"]}

        # 6. Generate Final Paper
        marks_per_question = analysis.get("marks_per_question", 10)
        final_paper = self.generation_agent.generate_paper(
            valid_qs, lesson_plan, bloom_report, total_marks, marks_per_question, exam_type
        )

        # Attach CO/PO to sub-questions
        for section in final_paper["sections"]:
            for main_q in section["questions"]:
                for q in main_q["sub_questions"]:
                    qid = q.get("source_id")
                    if qid and qid in copo_by_id:
                        q["CO"] = copo_by_id[qid]["co"]
                        q["PO"] = ", ".join(copo_by_id[qid]["po"])
                    else:
                        q["CO"] = "CO1"
                        q["PO"] = "PO1"

        final_paper["copo_analysis"] = copo_report
        final_paper["exam_type"] = exam_type
        final_paper["course_code"] = lesson_plan.get("course_code", "Auto")

        # 7. Print Final Output
        print("\n" + "="*60)
        print("  FINAL QUESTION PAPER")
        print("="*60)
        print(f"Subject: {final_paper['subject']} | Marks: {final_paper['total_marks']} | Duration: {final_paper['duration']}")
        print(f"Instructions: {final_paper['instructions']}\n")

        for section in final_paper["sections"]:
            print(f"--- {section['unit']}: {section['title']} ---")
            if not section["questions"]:
                print("  (No questions available for this unit)")
            for main_q in section["questions"]:
                print(f"  Q{main_q['main_q']})")
                for q in main_q["sub_questions"]:
                    print(f"    {q['q_no']}) [{q['marks']} Marks] [{q['CO']}] [{q['PO']}] {q['text'][:120]}...")
            print()

        # 8. Save JSON & PDF
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        
        output_filename = f"{subject.replace(' ', '_')}_{exam_type}_Paper.json"
        output_path = os.path.join(output_dir, output_filename)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(final_paper, f, indent=4)
            
        print(f"[Coordinator] 📁 Final paper JSON saved to: {output_path}")
        
        pdf_filename = f"output/{subject.replace(' ', '_')}_{exam_type}_Paper.pdf"
        self.pdf_tool.generate(final_paper, pdf_filename)

        print("\n[Coordinator] ✅ WORKFLOW COMPLETED SUCCESSFULLY.")

# --- RUNNING THE FULL SYSTEM (If executed directly) ---
if __name__ == "__main__":
    coordinator = QuestionPaperCoordinator()
    
    # Example run (can also be triggered via run_faculty_upload.py)
    coordinator.run_workflow(
        subject="Deep Learning",
        exam_type="ESA",
        target_batch="Oct 2025 - Feb 2026",
        lesson_plan_path="data/lesson_plans/Deep_Learning_LP.pdf",
        total_marks=100 
    )