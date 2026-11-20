
import json
from pathlib import Path
from datetime import datetime


BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output" / "lab14_capstone_studio"

LAB_OUTPUTS = {
    "lab11_sdlc_factory": BASE_DIR / "output" / "lab11_sdlc",
    "lab12_safety_governance": BASE_DIR / "output" / "lab12_safety_governance",
    "lab13_discipline_agents": BASE_DIR / "output" / "lab13_discipline_agents"
}


class CapstoneProjectStudio:

    def __init__(self):
        self.audit_log = []
        self.results = {}

    def log(self, message):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "message": message
        }
        self.audit_log.append(entry)
        print("[CAPSTONE]", message)

    def check_files(self, lab_name, required_files):
        self.log(f"Checking {lab_name}")

        checks = {}

        for relative_path in required_files:
            path = BASE_DIR / relative_path
            checks[relative_path] = path.is_file()

            status = "FOUND" if path.is_file() else "MISSING"
            self.log(f"{relative_path}: {status}")

        passed = all(checks.values())

        self.results[lab_name] = {
            "status": "PASS" if passed else "FAIL",
            "checks": checks
        }

        return passed

    def load_json(self, path):
        try:
            with open(path, "r", encoding="utf-8") as file:
                data = json.load(file)

            if not isinstance(data, (dict, list)):
                return False

            if isinstance(data, dict) and "error" in data:
                return False

            return True

        except (OSError, json.JSONDecodeError):
            return False

    def check_artifacts(self, lab_name, output_dir, required_files):
        self.log(f"Checking {lab_name}")

        checks = {}

        for filename in required_files:
            path = output_dir / filename

            if filename.endswith(".json"):
                valid = path.is_file() and self.load_json(path)
            else:
                valid = path.is_file() and path.stat().st_size > 0

            checks[filename] = valid

            self.log(
                f"{filename}: {'VALID' if valid else 'FAILED'}"
            )

        passed = all(checks.values())

        self.results[lab_name] = {
            "status": "PASS" if passed else "FAIL",
            "checks": checks
        }

        return passed

    def check_lab1_6(self):
        return self.check_files(
            "labs_1_to_6_runtime",
            [
                "runtime/openclaw_runtime.py",
                "skills/question_paper_skill.py",
                "memory/memory_manager.py",
                "tools/question_bank_tool.py",
                "tools/copo_tool.py",
                "tools/pdf_generator_tool.py"
            ]
        )

    def check_lab7_10(self):
        return self.check_files(
            "labs_7_to_10_agents",
            [
                "agent/lab7_node_graph_agent.py",
                "agent/lab8_parallel_swarm_agent.py",
                "agent/lab9_deep_research_agent.py",
                "agent/lab10_cloud_ops_agent.py",
                "agent/coordinator.py"
            ]
        )

    def check_lab11(self):
        return self.check_artifacts(
            "lab11_sdlc_factory",
            LAB_OUTPUTS["lab11_sdlc_factory"],
            [
                "requirements.json",
                "design.json",
                "question_validator.py",
                "test_report.json",
                "audit_log.json"
            ]
        )

    def check_lab12(self):
        return self.check_artifacts(
            "lab12_safety_governance",
            LAB_OUTPUTS["lab12_safety_governance"],
            [
                "risk_assessment.json",
                "approval_log.json",
                "evaluation_report.json",
                "rollback_log.json",
                "audit_log.json"
            ]
        )

    def check_lab13(self):
        return self.check_artifacts(
            "lab13_discipline_agents",
            LAB_OUTPUTS["lab13_discipline_agents"],
            [
                "me_agent.json",
                "ce_agent.json",
                "ee_agent.json",
                "combined_domain_report.json",
                "audit_log.json"
            ]
        )

    def check_integration(self):
        self.log("Checking complete project integration")

        main_file = BASE_DIR / "main.py"

        syntax_valid = False

        if main_file.is_file():
            try:
                source = main_file.read_text(encoding="utf-8")
                compile(source, str(main_file), "exec")
                syntax_valid = True
            except (SyntaxError, UnicodeDecodeError):
                syntax_valid = False

        checks = {
            "main.py_exists": main_file.is_file(),
            "main.py_syntax_valid": syntax_valid,
            "runtime_exists": (
                BASE_DIR / "runtime" / "openclaw_runtime.py"
            ).is_file(),
            "output_directory_exists": (
                BASE_DIR / "output"
            ).is_dir()
        }

        passed = all(checks.values())

        self.results["project_integration"] = {
            "status": "PASS" if passed else "FAIL",
            "checks": checks
        }

        for name, status in checks.items():
            self.log(f"{name}: {'PASS' if status else 'FAIL'}")

        return passed

    def evaluate_capstone(self):

        self.log("Evaluating complete capstone system")

        lab_names = [
            "labs_1_to_6_runtime",
            "labs_7_to_10_agents",
            "lab11_sdlc_factory",
            "lab12_safety_governance",
            "lab13_discipline_agents",
            "project_integration"
        ]

        statuses = {
            name: self.results.get(name, {}).get(
                "status", "NOT_CHECKED"
            )
            for name in lab_names
        }

        completed = sum(
            status == "PASS"
            for status in statuses.values()
        )

        total = len(lab_names)

        percentage = round(
            (completed / total) * 100, 2
        )

        evaluation = {
            "project": "Question Paper OBE Agent",
            "project_type": "Complete Team-Owned Agentic AI System",
            "evaluation_time": datetime.now().isoformat(),
            "labs_completed": completed,
            "total_components": total,
            "completion_percentage": percentage,
            "status": (
                "PASS" if completed == total else "INCOMPLETE"
            ),
            "component_status": statuses,
            "integration_scope": (
                "Structural and artifact validation of Labs 1-14. "
                "This check does not replace functional testing "
                "of every individual agent."
            )
        }

        self.results["capstone_evaluation"] = evaluation

        self.log(
            f"Capstone completion: {completed}/{total} components"
        )

        return evaluation

    def save_outputs(self):

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        report_path = OUTPUT_DIR / "capstone_report.json"
        audit_path = OUTPUT_DIR / "audit_log.json"

        self.log("Saving final capstone report")
        self.log("Saving capstone audit log")

        with open(report_path, "w", encoding="utf-8") as file:
            json.dump(self.results, file, indent=4)

        with open(audit_path, "w", encoding="utf-8") as file:
            json.dump(self.audit_log, file, indent=4)

        print(f"\n[Saved] {report_path}")
        print(f"[Saved] {audit_path}")

    def run(self):

        print("\n" + "=" * 65)
        print("       LAB 14 - CAPSTONE PROJECT STUDIO")
        print("       COMPLETE TEAM-OWNED AGENTIC SYSTEM")
        print("=" * 65)

        self.log("Starting complete capstone evaluation")

        self.check_lab1_6()
        self.check_lab7_10()
        self.check_lab11()
        self.check_lab12()
        self.check_lab13()
        self.check_integration()

        evaluation = self.evaluate_capstone()

        self.save_outputs()

        print("\n" + "=" * 65)
        print("                 CAPSTONE SUMMARY")
        print("=" * 65)

        for name, status in evaluation["component_status"].items():
            print(f"{name:30}: {status}")

        print("-" * 65)

        print(
            f"Components completed: "
            f"{evaluation['labs_completed']}/"
            f"{evaluation['total_components']}"
        )

        print(
            f"Completion percentage: "
            f"{evaluation['completion_percentage']}%"
        )

        print(f"Capstone status: {evaluation['status']}")

        print("-" * 65)
        print("Output directory:")
        print(OUTPUT_DIR)
        print("=" * 65)


if __name__ == "__main__":
    studio = CapstoneProjectStudio()
    studio.run()
