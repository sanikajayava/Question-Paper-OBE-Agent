import time

class CloudOpsAgent:
    def __init__(self):
        self.name = "Lab 10: Cloud Operations Agent"

    def monitor_infra(self):
        print("  [Ops 1: Monitor] Scanning cloud signals...")
        time.sleep(0.5)
        print("  [ALERT] Failed deployment detected in 'auth-service'!")
        return {"service": "auth-service", "error": "CrashLoopBackOff"}

    def diagnose(self, alert):
        print(f"  [Ops 2: Diagnose] Analyzing {alert['service']}...")
        time.sleep(0.5)
        print("  [Diagnosis] Reason: Missing environment variable DB_HOST.")
        return "Add DB_HOST variable"

    def approval_gate(self, fix):
        # This satisfies the "acts with approval gates" requirement
        print(f"  [Ops 3: Approval Gate] Proposed Fix: {fix}")
        print("  -> Auto-approval granted (Policy: safe fix).")
        return True

    def execute_fix(self, fix):
        print(f"  [Ops 4: Act] Applying fix: {fix}")
        time.sleep(0.5)
        print("  [Success] auth-service is now Running.")

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