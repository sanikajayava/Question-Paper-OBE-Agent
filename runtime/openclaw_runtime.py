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
    - Skills
    - Tools
    - Memory
    - Audit Log
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

        # Tool execution
        question_bank = read_question_bank()
        self.log_event("question_bank_tool", question_bank.get("status", "unknown"))

        # Memory retrieval
        past_papers = self.memory.retrieve_by_tag("agents")
        self.log_event("memory_retrieval", "success")

        # Skill execution
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


if __name__ == "__main__":
    runtime = OpenClawRuntime()

    result = runtime.execute(
        "Generate a 50-mark question paper for Agentic AI."
    )

    print("\n===== OPENCLA/OPENCLAW RUNTIME =====")
    print("Runtime:", result["runtime"])
    print("Status:", result["status"])

    print("\n===== SKILL =====")
    print("Skill Status:", result["skill_status"])

    print("\n===== TOOL =====")
    print("Tool Status:", result["tool_status"])

    print("\n===== MEMORY =====")
    print("Past Papers Retrieved:", result["memory_count"])

    print("\n===== BLUEPRINT =====")
    print(result["blueprint"])

    print("\n===== AUDIT LOG =====")
    for event in result["audit_log"]:
        print(
            f"{event['timestamp']} | "
            f"{event['action']} | "
            f"{event['status']}"
        )