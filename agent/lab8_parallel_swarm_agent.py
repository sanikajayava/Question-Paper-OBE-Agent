import time

class ParallelSwarmAgent:
    def __init__(self):
        self.name = "Lab 8: Parallel Swarm"
        self.swarm_log = []

    def _worker_agent(self, role, task):
        """Simulates a single agent in the swarm."""
        print(f"  [Swarm Worker: {role}] Working on '{task}'...")
        time.sleep(1.5) # Simulate parallel work
        result = f"{role} finished the {task}."
        self.swarm_log.append({"role": role, "result": result})
        return result

    def _manager_merge(self, results):
        """Merges the parallel outputs."""
        print(f"\n  [Swarm Manager] Merging {len(results)} parallel outputs...")
        time.sleep(1)
        merged = " | ".join(results)
        return f"FINAL HACKATHON PLAN: {merged}"

    def run_swarm(self, goal):
        print(f"\n[{self.name}] Launching Swarm for goal: {goal}")
        
        # In real code, these would be separate threads/processes. 
        # Here we simulate the concept of parallel role-based agents.
        print("  -> Dispatching agents in parallel...")
        result1 = self._worker_agent("Logistics Agent", "booking venue")
        result2 = self._worker_agent("Food Agent", "ordering catering")
        result3 = self._worker_agent("Tech Agent", "setting up Wi-Fi")
        
        # Manager merges results
        final_output = self._manager_merge([result1, result2, result3])
        
        print(f"\n✅ [{self.name}] Swarm Complete.")
        print(final_output)
        return final_output

if __name__ == "__main__":
    agent = ParallelSwarmAgent()
    agent.run_swarm("Organize a 24-hour college Hackathon")