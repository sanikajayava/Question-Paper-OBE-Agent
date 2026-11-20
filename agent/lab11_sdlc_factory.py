import json
from pathlib import Path
from datetime import datetime
import ast


# ============================================================
# LAB 11: AGENTIC SDLC FACTORY
# Requirement -> Design -> Implementation -> Testing
# ============================================================


class RequirementAnalysisAgent:
    """Converts user requirements into structured requirements."""

    def analyze(self, requirement):
        print("\n[Requirement Analysis Agent] Analyzing requirements...")

        if not requirement or not requirement.strip():
            raise ValueError("Project requirement cannot be empty.")

        result = {
            "project_name": "Question Bank Validator",
            "user_requirement": requirement,
            "functional_requirements": [
                "Accept question details as structured input.",
                "Check mandatory question fields.",
                "Validate Bloom's taxonomy levels.",
                "Validate marks assigned to questions.",
                "Return validation status and error messages."
            ],
            "acceptance_criteria": [
                "Valid questions must pass validation.",
                "Missing mandatory fields must be reported.",
                "Invalid Bloom levels must be rejected.",
                "Invalid marks must be rejected."
            ]
        }

        print("[Requirement Analysis Agent] Requirements identified.")
        return result


class SoftwareDesignAgent:
    """Creates a software design from analyzed requirements."""

    def design(self, requirements):
        print("\n[Software Design Agent] Creating software design...")

        design = {
            "architecture": "Modular Python Application",
            "components": [
                {
                    "name": "Question Validator",
                    "responsibility": "Validate question details."
                },
                {
                    "name": "Validation Response",
                    "responsibility": "Return status and validation errors."
                },
                {
                    "name": "Testing Module",
                    "responsibility": "Test valid and invalid question inputs."
                }
            ],
            "data_flow": [
                "Receive question input",
                "Check mandatory fields",
                "Validate Bloom level",
                "Validate marks",
                "Return validation result"
            ],
            "technology": "Python"
        }

        print("[Software Design Agent] Design completed.")
        return design


class CodeGenerationAgent:
    """Generates Python implementation from the approved design."""

    def generate(self, output_dir):
        print("\n[Code Generation Agent] Generating Python implementation...")

        source_code = '''\
def validate_question(question):
    """
    Validate a question bank entry.

    Required fields:
    id, text, unit, bloom_level, marks
    """

    errors = []

    required_fields = ["id", "text", "unit", "bloom_level", "marks"]

    for field in required_fields:
        if field not in question or question[field] is None:
            errors.append(f"Missing required field: {field}")

    if "text" in question and (
        not isinstance(question["text"], str) or not question["text"].strip()
    ):
        errors.append("Question text cannot be empty.")

    if "bloom_level" in question:
        if question["bloom_level"] not in ["L1", "L2", "L3", "L4", "L5", "L6"]:
            errors.append("Invalid Bloom taxonomy level.")

    if "marks" in question:
        if (
            not isinstance(question["marks"], (int, float))
            or isinstance(question["marks"], bool)
            or question["marks"] <= 0
        ):
            errors.append("Marks must be a positive number.")

    return {
        "valid": len(errors) == 0,
        "errors": errors
    }
'''

        output_dir.mkdir(parents=True, exist_ok=True)

        implementation_path = output_dir / "question_validator.py"
        implementation_path.write_text(source_code, encoding="utf-8")

        print(f"[Code Generation Agent] Implementation saved: {implementation_path}")

        return source_code


class TestingAgent:
    """Tests the generated implementation before release."""

    def test(self, source_code):
        print("\n[Testing Agent] Running automated tests...")

        # First check whether the generated code is syntactically valid.
        ast.parse(source_code)

        namespace = {}
        exec(compile(source_code, "<generated_implementation>", "exec"), namespace)

        validate_question = namespace["validate_question"]

        valid_question = {
            "id": "Q001",
            "text": "Explain cloud computing.",
            "unit": "Unit 1",
            "bloom_level": "L2",
            "marks": 10
        }

        invalid_question = {
            "id": "Q002",
            "text": "",
            "unit": "Unit 1",
            "bloom_level": "L9",
            "marks": -5
        }

        tests = []

        # Test 1: Valid question
        result = validate_question(valid_question)
        tests.append({
            "test": "Valid question acceptance",
            "status": "PASS" if result["valid"] else "FAIL"
        })

        # Test 2: Invalid question
        result = validate_question(invalid_question)
        tests.append({
            "test": "Invalid question rejection",
            "status": "PASS" if not result["valid"] else "FAIL"
        })

        # Test 3: Missing mandatory fields
        result = validate_question({"id": "Q003"})
        tests.append({
            "test": "Missing field detection",
            "status": "PASS" if not result["valid"] else "FAIL"
        })

        passed = sum(1 for test in tests if test["status"] == "PASS")
        total = len(tests)

        report = {
            "total_tests": total,
            "passed": passed,
            "failed": total - passed,
            "tests": tests,
            "overall_status": "PASS" if passed == total else "FAIL"
        }

        print(f"[Testing Agent] Tests completed: {passed}/{total} passed.")

        return report


class AgenticSDLCFactory:
    """
    Coordinates the complete Agentic SDLC workflow.
    """

    def __init__(self):
        self.name = "Lab 11: Agentic SDLC Factory"

        self.requirement_agent = RequirementAnalysisAgent()
        self.design_agent = SoftwareDesignAgent()
        self.code_agent = CodeGenerationAgent()
        self.testing_agent = TestingAgent()

        self.audit_log = []

    def log_event(self, stage, status):
        self.audit_log.append({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "stage": stage,
            "status": status
        })

    def run(self, requirement):
        print("\n" + "=" * 65)
        print(f"  {self.name.upper()}")
        print("  Requirement -> Design -> Code -> Testing")
        print("=" * 65)

        output_dir = Path("output") / "lab11_sdlc"

        # Phase 1: Requirement Analysis
        requirements = self.requirement_agent.analyze(requirement)
        self.log_event("requirement_analysis", "success")

        # Phase 2: Software Design
        design = self.design_agent.design(requirements)
        self.log_event("software_design", "success")

        # Phase 3: Code Generation
        source_code = self.code_agent.generate(output_dir)
        self.log_event("code_generation", "success")

        # Phase 4: Automated Testing
        test_report = self.testing_agent.test(source_code)
        self.log_event("automated_testing", test_report["overall_status"].lower())

        # Save project artifacts
        artifacts = {
            "requirements.json": requirements,
            "design.json": design,
            "test_report.json": test_report,
            "audit_log.json": self.audit_log
        }

        for filename, data in artifacts.items():
            path = output_dir / filename
            path.write_text(
                json.dumps(data, indent=4),
                encoding="utf-8"
            )

        overall_status = (
            "SUCCESS"
            if test_report["overall_status"] == "PASS"
            else "FAILED"
        )

        print("\n" + "=" * 65)
        print(f"  LAB 11 EXECUTION STATUS: {overall_status}")
        print(f"  Tests Passed: {test_report['passed']}/{test_report['total_tests']}")
        print(f"  Output Directory: {output_dir.resolve()}")
        print("=" * 65)

        return {
            "status": overall_status,
            "requirements": requirements,
            "design": design,
            "test_report": test_report,
            "output_directory": str(output_dir),
            "audit_log": self.audit_log
        }


# ============================================================
# STANDALONE EXECUTION
# ============================================================

if __name__ == "__main__":

    factory = AgenticSDLCFactory()

    project_requirement = """
    Develop a Question Bank Validator for the Question Paper OBE Agent.
    The application should validate question IDs, question text,
    units, Bloom taxonomy levels and marks before questions
    are used for question paper generation.
    """

    result = factory.run(project_requirement)