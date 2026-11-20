import time

class CloudOpsAgent:
    def __init__(self):
        self.name = "Lab 10: Cloud Operations Agent"

    def monitor_infra(self):
        print("  [Ops 1: Monitor] Scanning cloud signals for QP-Agent servers...")
        time.sleep(1)
        print("  [ALERT] Failed deployment detected in 'pdf_generator_service'!")
        return {"service": "pdf_generator_service", "error": "CrashLoopBackOff"}

    def diagnose(self, alert):
        print(f"  [Ops 2: Diagnose] Analyzing {alert['service']}...")
        time.sleep(1)
        print("  [Diagnosis] Reason: Missing 'fpdf2' library on the server.")
        return "Install fpdf2 and restart pod"

    def approval_gate(self, fix):
        print(f"  [Ops 3: Approval Gate] Proposed Fix: {fix}")
        time.sleep(1)
        print("  -> Auto-approval granted (Policy: safe fix).")
        return True

    def execute_fix(self, fix):
        print(f"  [Ops 4: Act] Applying fix: {fix}")
        time.sleep(1)
        print("  [Success] pdf_generator_service is now Running (1/1 Ready).")

    def run(self):
        print(f"\n[{self.name}] Starting cloud monitoring cycle...")
        alert = self.monitor_infra()
        fix = self.diagnose(alert)
        if self.approval_gate(fix):
            self.execute_fix(fix)
        print(f"\n✅ [{self.name}] Operations Complete.")

if __name__ == "__main__":
    agent = CloudOpsAgent()
    agent.run()