import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from datetime import datetime

from skills.question_paper_skill import QuestionPaperSkill
from tools.question_bank_tool import read_question_bank
from memory.memory_manager import MemoryManager


class OpenClawRuntime:
    """
    OpenCLA/OpenClaw Runtime for the Question Paper OBE Agent.

    Coordinates:
    - Skills (Lab 1-6)
    - Tools (Lab 1-6)
    - Memory (Lab 1-6)
    - Audit Log (Lab 1-6)
    - NEW: Multi-Agent Coordinator (Lab 7-10)
    """

    def __init__(self):
        self.skill = QuestionPaperSkill()
        self.memory = MemoryManager()
        self.audit_log = []

    def log_event(self, action, status):
        """Record an auditable runtime event."""
        self.audit_log.append({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "action": action,
            "status": status
        })

    def execute(self, request):
        """Execute the agent workflow through the runtime."""

        self.log_event("runtime_started", "success")

        # ===== LAB 1-6: ORIGINAL SKILL EXECUTION =====
        question_bank = read_question_bank()
        self.log_event("question_bank_tool", question_bank.get("status", "unknown"))

        past_papers = self.memory.retrieve_by_tag("agents")
        self.log_event("memory_retrieval", "success")

        blueprint = self.skill.create_blueprint({
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
        self.log_event("question_paper_skill", "success")

        self.log_event("runtime_completed", "success")

        return {
            "runtime": "OpenCLA/OpenClaw Runtime",
            "request": request,
            "status": "success",
            "skill_status": "executed",
            "tool_status": question_bank.get("status", "unknown"),
            "memory_count": len(past_papers),
            "blueprint": blueprint,
            "audit_log": self.audit_log
        }

    # ===== LAB 7-10: NEW MULTI-AGENT EXECUTION =====
    def execute_multi_agent(self, subject, exam_type, target_batch, lesson_plan_path):
        """Execute the NEW multi-agent coordinator (Lab 7-10)."""
        self.log_event("multi_agent_started", "success")
        
        from agent.coordinator import QuestionPaperCoordinator
        coordinator = QuestionPaperCoordinator()
        
        # Run the full 5-agent pipeline
        coordinator.run_workflow(
            subject=subject,
            exam_type=exam_type,
            target_batch=target_batch,
            lesson_plan_path=lesson_plan_path
        )
        
        self.log_event("multi_agent_completed", "success")
        
        return {
            "multi_agent_status": "success",
            "subject": subject,
            "exam_type": exam_type,
            "audit_log": self.audit_log
        }


if __name__ == "__main__":
    # ===== TEST 1: Original Lab 1-6 Runtime =====
    print("\n" + "=" * 60)
    print("  TEST 1: ORIGINAL LAB 1-6 RUNTIME")
    print("=" * 60)
    
    runtime = OpenClawRuntime()
    result = runtime.execute("Generate a 50-mark question paper for Agentic AI.")

    print("\n===== OPENCLA/OPENCLAW RUNTIME =====")
    print("Runtime:", result["runtime"])
    print("Status:", result["status"])

    print("\n===== SKILL =====")
    print("Skill Status:", result["skill_status"])

    print("\n===== MEMORY =====")
    print("Past Papers Retrieved:", result["memory_count"])

    print("\n===== BLUEPRINT =====")
    print(result["blueprint"])

    print("\n===== AUDIT LOG =====")
    for event in result["audit_log"]:
        print(f"{event['timestamp']} | {event['action']} | {event['status']}")