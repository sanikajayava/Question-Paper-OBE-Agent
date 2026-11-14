import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.lesson_plan_agent import LessonPlanAgent
from agent.question_retrieval_agent import QuestionRetrievalAgent
from agent.past_paper_agent import PastPaperAnalysisAgent
from agent.validation_agent import ValidationAgent
from agent.generation_agent import QuestionGenerationAgent
from tools.copo_tool import COPOTool

class QuestionPaperCoordinator:
    def __init__(self):
        self.name = "Question Paper Coordinator"
        self.lp_agent = LessonPlanAgent()
        self.retrieval_agent = QuestionRetrievalAgent()
        self.analysis_agent = PastPaperAnalysisAgent()
        self.validation_agent = ValidationAgent()
        self.generation_agent = QuestionGenerationAgent()
        self.copo_tool = COPOTool()

    def run_workflow(self, subject, exam_type, target_batch, lesson_plan_path):
        print(f"\n{'='*60}")
        print(f"  {self.name.upper()}")
        print(f"  Goal: Generate a {exam_type} paper for {subject}")
        print(f"  Target Batch: {target_batch}")
        print(f"{'='*60}")

        # 1. Read Lesson Plan
        lesson_plan = self.lp_agent.read_lesson_plan(lesson_plan_path)
        if not lesson_plan:
            print("[Coordinator] ERROR: Could not read lesson plan. Aborting.")
            return

        # 2. Retrieve Questions
        retrieved = self.retrieval_agent.retrieve_questions(subject, exam_type, target_batch)
        if not retrieved:
            print("[Coordinator] ERROR: No questions found. Aborting.")
            return

        # 3. Analyze Past Papers
        analysis = self.analysis_agent.analyze(retrieved)

        # 4. Validate Questions
        valid_qs, rejected = self.validation_agent.validate_questions(retrieved, subject)
        if not valid_qs:
            print("[Coordinator] ERROR: No valid questions after validation. Aborting.")
            return

        # 4.5. CO/PO Mapping
        print(f"\n[{self.name}] Performing CO/PO Mapping...")
        copo_report = self.copo_tool.map_paper(valid_qs)
        print(f"  -> CO Distribution: {copo_report['co_distribution']}")
        print(f"  -> Covered COs: {copo_report['covered_cos']}")
        if copo_report['uncovered_cos']:
            print(f"  -> Uncovered COs: {copo_report['uncovered_cos']}")
        
        copo_by_id = {item["id"]: item for item in copo_report["questions"]}

        # 5. Generate Final Paper
        final_paper = self.generation_agent.generate_paper(valid_qs, lesson_plan, analysis, total_marks=100)

        # 5.5. Attach CO/PO info to each question
        for section in final_paper["sections"]:
            for q in section["questions"]:
                qid = q.get("source_id")
                if qid and qid in copo_by_id:
                    q["CO"] = copo_by_id[qid]["co"]
                    q["PO"] = ", ".join(copo_by_id[qid]["po"])

        # Add overall CO/PO analysis to paper
        final_paper["copo_analysis"] = {
            "co_distribution": copo_report["co_distribution"],
            "covered_cos": copo_report["covered_cos"],
            "uncovered_cos": copo_report["uncovered_cos"]
        }

        # 6. Print Final Output
        print("\n" + "="*60)
        print("  FINAL QUESTION PAPER")
        print("="*60)
        print(f"Subject: {final_paper['subject']} | Marks: {final_paper['total_marks']} | Duration: {final_paper['duration']}")
        print(f"Instructions: {final_paper['instructions']}")
        print(f"Analysis Summary: {final_paper['analysis_summary']}\n")

        for section in final_paper["sections"]:
            print(f"--- {section['unit']}: {section['title']} ---")
            if not section["questions"]:
                print("  (No questions available for this unit)")
            for q in section["questions"]:
                co = q.get("CO", "?")
                po = q.get("PO", "?")
                print(f"Q{q['question_number']}) [{q['marks']} Marks] [{co}] [{po}] {q['text'][:180]}...")
            print()

        # CO/PO Summary
        print("📊 CO/PO COVERAGE ANALYSIS:")
        for co, cnt in final_paper["copo_analysis"]["co_distribution"].items():
            status = "✅" if cnt > 0 else "❌"
            print(f"   {status} {co}: {cnt} questions")
        print()

        # 7. Save the generated paper to a JSON file
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        
        output_filename = f"{subject.replace(' ', '_')}_{exam_type}_Paper.json"
        output_path = os.path.join(output_dir, output_filename)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(final_paper, f, indent=4)
            
        print(f"[Coordinator] 📁 Final paper saved to: {output_path}")
        print("\n[Coordinator] ✅ WORKFLOW COMPLETED SUCCESSFULLY.")

# --- RUNNING THE FULL SYSTEM FOR ALL 4 SUBJECTS ---
if __name__ == "__main__":
    coordinator = QuestionPaperCoordinator()
    
    subjects_to_process = [
        {
            "subject": "Cloud Computing",
            "exam_type": "ESA",
            "target_batch": "Oct 2025 - Feb 2026",
            "lesson_plan_path": "data/lesson_plans/Cloud_Computing_Lesson_Plan.txt"
        },
        {
            "subject": "Deep Learning",
            "exam_type": "ESA",
            "target_batch": "Oct 2025 - Feb 2026",
            "lesson_plan_path": "data/lesson_plans/Deep_Learning_Lesson_Plan.txt"
        },
        {
            "subject": "Gen AI",
            "exam_type": "ESA",
            "target_batch": "Oct 2025 - Feb 2026",
            "lesson_plan_path": "data/lesson_plans/Gen_AI_Lesson_Plan.txt"
        },
        {
            "subject": "Cyber Security",
            "exam_type": "ESA",
            "target_batch": "Oct 2024 - Feb 2025",
            "lesson_plan_path": "data/lesson_plans/Cyber_Security_Lesson_Plan.txt"
        }
    ]

    for config in subjects_to_process:
        try:
            coordinator.run_workflow(
                subject=config["subject"],
                exam_type=config["exam_type"],
                target_batch=config["target_batch"],
                lesson_plan_path=config["lesson_plan_path"]
            )
        except Exception as e:
            print(f"\n[Coordinator] ❌ ERROR processing {config['subject']}: {e}")