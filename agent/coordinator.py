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

    def run_workflow(self, subject, exam_type, target_batch, lesson_plan_path, total_marks=100, set_name=""):
        print(f"\n{'='*60}")
        print(f"  {self.name.upper()}")
        print(f"  Goal: Generate {set_name} paper for {subject} ({exam_type})")
        print(f"{'='*60}")

        # 1. Read Lesson Plan
        lesson_plan = self.lp_agent.read_lesson_plan(lesson_plan_path)
        if not lesson_plan: return

        # 2. Retrieve Questions
        retrieved = self.retrieval_agent.retrieve_questions(subject, exam_type, target_batch, lesson_plan)
        if not retrieved: return

        # 3. Analyze
        analysis = self.analysis_agent.analyze(retrieved)
        bloom_report = self.bloom_agent.analyze(retrieved)

        # 4. Validate
        valid_qs, _ = self.validation_agent.validate_questions(retrieved, subject)
        if not valid_qs: 
            print(f"[Coordinator] ERROR: No valid questions found. Aborting.")
            return

        # 5. CO/PO Map
        print(f"\n[{self.name}] Performing CO/PO Mapping...")
        copo_report = self.copo_tool.map_paper(valid_qs)
        copo_by_id = {item["id"]: item for item in copo_report["questions"]}

        # 6. Generate Final Paper (Pass set_name to shift questions)
        marks_per_question = analysis.get("marks_per_question", 10)
        final_paper = self.generation_agent.generate_paper(
            valid_qs, lesson_plan, bloom_report, total_marks, marks_per_question, exam_type, set_name
        )

        # Attach CO/PO
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

        # 7. Save JSON & PDF
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        
        set_suffix = f"_{set_name}" if set_name else ""
        output_filename = f"{subject.replace(' ', '_')}_{exam_type}{set_suffix}_Paper.json"
        output_path = os.path.join(output_dir, output_filename)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(final_paper, f, indent=4)
            
        pdf_filename = f"output/{subject.replace(' ', '_')}_{exam_type}{set_suffix}_Paper.pdf"
        self.pdf_tool.generate(final_paper, pdf_filename)

        print(f"[Coordinator] ✅ {set_name} WORKFLOW COMPLETED. Check output folder.")

# --- RUNNING THE FULL SYSTEM (If executed directly) ---
if __name__ == "__main__":
    coordinator = QuestionPaperCoordinator()
    coordinator.run_workflow(
        subject="Deep Learning",
        exam_type="ESA",
        target_batch="Oct 2025 - Feb 2026",
        lesson_plan_path="data/lesson_plans/Deep_Learning_LP.pdf",
        total_marks=100 
    )