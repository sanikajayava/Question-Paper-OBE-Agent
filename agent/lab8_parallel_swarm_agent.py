import time
import threading
import sys

class ParallelSwarmAgent:
    def __init__(self):
        self.name = "Lab 8: Parallel Swarm"
        self.results = []
        self.lock = threading.Lock()

    def _generate_paper_worker(self, subject_name, marks):
        """Simulates an agent generating a paper. Runs in a separate thread."""
        print(f"  [Thread Started] Agent generating {subject_name} paper ({marks} marks)...")
        
        # Simulate processing time (e.g., retrieval, generation, PDF creation)
        time.sleep(2) 
        
        result_msg = f"✅ {subject_name} Paper generated successfully."
        
        # Use lock to safely update shared memory
        with self.lock:
            self.results.append(result_msg)
        print(f"  [Thread Finished] {result_msg}")

    def run_swarm(self, subjects_to_generate):
        print(f"\n[{self.name}] 🚀 Launching Parallel Swarm with Threading...")
        print(f"  -> Memory Check: Current active threads = {threading.active_count()}")
        
        start_time = time.time()
        threads = []

        # 1. Dispatch all agents in parallel
        for subject, marks in subjects_to_generate.items():
            thread = threading.Thread(target=self._generate_paper_worker, args=(subject, marks))
            threads.append(thread)
            thread.start()

        # 2. Wait for all agents to finish
        for thread in threads:
            thread.join()

        end_time = time.time()
        total_time = round(end_time - start_time, 2)

        # 3. Manager merges the results
        print(f"\n[{self.name}] Manager merging results from shared memory...")
        for res in self.results:
            print(f"  -> {res}")
            
        print(f"\n✅ [{self.name}] Swarm Complete!")
        print(f"⏱️ Total Time Taken: {total_time} seconds (Saved time by running in parallel!)")
        
        return self.results

if __name__ == "__main__":
    swarm = ParallelSwarmAgent()
    
    # We are asking it to generate 3 papers at the exact same time
    subjects = {
        "Cloud Computing": 100,
        "Deep Learning": 50,
        "Cyber Security": 30
    }
    swarm.run_swarm(subjects)