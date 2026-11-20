
import json
import os
import sys
from datetime import datetime


class SafetyGovernanceAgent:
    def __init__(self):
        self.name = "Lab 12: Safety & Governance"
        self.output_dir = "output/lab12_safety_governance"
        os.makedirs(self.output_dir, exist_ok=True)

        self.audit_log = []
        self.approval_log = []
        self.rollback_log = []

    def save_json(self, filename, data):
        path = os.path.join(self.output_dir, filename)
        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
        print(f"[Saved] {path}")

    def log(self, action, status):
        self.audit_log.append({
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "status": status
        })

    # 1. Risk Assessment
    def assess_risk(self, action, likelihood, impact):
        print("\n[Risk Assessment Agent] Assessing potential risks...")

        score = likelihood * impact

        if score >= 16:
            level = "HIGH"
        elif score >= 8:
            level = "MEDIUM"
        else:
            level = "LOW"

        report = {
            "action": action,
            "likelihood": likelihood,
            "impact": impact,
            "risk_score": score,
            "risk_level": level,
            "approval_required": level in ["HIGH", "MEDIUM"]
        }

        print(f"[Risk Assessment] Risk Score: {score}/25")
        print(f"[Risk Assessment] Risk Level: {level}")

        self.save_json("risk_assessment.json", report)
        self.log("risk_assessment", "completed")

        return report

    # 2. Human Approval
    def request_approval(self, risk_report):
        print("\n[Approval Agent] Human approval required.")

        print("Proposed Action:", risk_report["action"])
        print("Risk Level:", risk_report["risk_level"])

        if not risk_report["approval_required"]:
            approved = True
            print("[Approval Agent] Low risk. Automatically approved.")
        else:
            choice = input("Approve this action? (yes/no): ").strip().lower()
            approved = choice in ["yes", "y"]

        record = {
            "action": risk_report["action"],
            "approved": approved,
            "approval_type": "human" if risk_report["approval_required"]
                             else "automatic",
            "timestamp": datetime.now().isoformat()
        }

        self.approval_log.append(record)
        self.save_json("approval_log.json", self.approval_log)

        self.log("approval_check", "approved" if approved else "rejected")

        return approved

    # 3. Execute Action
    def execute_action(self, state, simulate_failure=False):
        print("\n[Execution Agent] Applying approved change...")

        old_value = state["validation_threshold"]

        if simulate_failure:
            state["validation_threshold"] = 999
        else:
            state["validation_threshold"] = 80

        print("[Execution Agent] Change applied.")

        return old_value

    # 4. Evaluation
    def evaluate_action(self, state):
        print("\n[Evaluation Agent] Evaluating implementation...")

        checks = {
            "threshold_within_valid_range":
                0 <= state["validation_threshold"] <= 100,
            "configuration_available":
                "validation_threshold" in state
        }

        passed = all(checks.values())

        report = {
            "evaluation_checks": checks,
            "total_checks": len(checks),
            "passed_checks": sum(checks.values()),
            "evaluation_status": "PASS" if passed else "FAIL"
        }

        print("[Evaluation Agent] Status:", report["evaluation_status"])

        self.save_json("evaluation_report.json", report)
        self.log("evaluation", report["evaluation_status"])

        return passed

    # 5. Rollback
    def rollback(self, state, old_value):
        print("\n[Rollback Agent] Evaluation failed!")
        print("[Rollback Agent] Reverting previous configuration...")

        state["validation_threshold"] = old_value

        record = {
            "rollback_status": "SUCCESS",
            "restored_value": old_value,
            "timestamp": datetime.now().isoformat()
        }

        self.rollback_log.append(record)
        self.save_json("rollback_log.json", self.rollback_log)

        self.log("rollback", "success")

        print("[Rollback Agent] Previous state restored.")

    # Complete workflow
    def run(self):
        print("\n" + "=" * 65)
        print("  LAB 12: SAFETY & GOVERNANCE")
        print("  Risk -> Approval -> Evaluation -> Rollback")
        print("=" * 65)

        state = {"validation_threshold": 70}

        print("\nInitial System State:", state)

        # Step 1: Assess risk
        risk_report = self.assess_risk(
            action="Update question validation threshold",
            likelihood=3,
            impact=4
        )

        # Step 2: Approval
        approved = self.request_approval(risk_report)

        if not approved:
            print("\n[Governance] Action rejected. No changes made.")
            self.log("workflow", "rejected")
        else:
            # Step 3: Execute
            old_value = self.execute_action(
                state,
                simulate_failure="--simulate-failure" in sys.argv
            )

            # Step 4: Evaluate
            passed = self.evaluate_action(state)

            # Step 5: Rollback if necessary
            if not passed:
                self.rollback(state, old_value)
            else:
                print("\n[Governance] Action completed successfully.")
                self.log("workflow", "success")

        print("\nFinal System State:", state)

        self.save_json("audit_log.json", self.audit_log)

        print("\n" + "=" * 65)
        print("  LAB 12 EXECUTION COMPLETED")
        print("  Final State:", state)
        print("  Output Directory:", os.path.abspath(self.output_dir))
        print("=" * 65)


if __name__ == "__main__":
    agent = SafetyGovernanceAgent()
    agent.run()
