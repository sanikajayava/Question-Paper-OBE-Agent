import time
import threading
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent.coordinator import QuestionPaperCoordinator

class ParallelSwarmAgent:
    def __init__(self):
        self.name = "Lab 8: Parallel Swarm"
        self.lock = threading.Lock() 
        self.results = []

    def _generate_paper_thread(self, subject, exam_type, target_batch, lesson_plan_path, total_marks, set_name):
        """Worker function running in a separate thread."""
        print(f"\n  [Thread Started] Generating {set_name} for {subject}...")
        
        coordinator = QuestionPaperCoordinator()
        start_time = time.time()
        
        try:
            # We pass a special flag 'set_name' to the coordinator to change the output filename
            # But we keep the 'subject' pure so validation passes.
            coordinator.run_workflow(
                subject=subject,
                exam_type=exam_type,
                target_batch=target_batch,
                lesson_plan_path=lesson_plan_path,
                total_marks=total_marks,
                set_name=set_name  # <--- Passing set name here
            )
            
            end_time = time.time()
            time_taken = round(end_time - start_time, 2)
            
            with self.lock:
                self.results.append(f"✅ {set_name} generated successfully in {time_taken}s")
                
        except Exception as e:
            with self.lock:
                self.results.append(f"❌ {set_name} failed: {e}")

    def run_swarm(self):
        print("\n" + "="*60)
        print("  🐝 LAB 8: PARALLEL SWARM GENERATOR")
        print("="*60)
        
        # --- 1. Display Available Lesson Plans ---
        print("\nAvailable Lesson Plans:")
        lp_dir = "data/lesson_plans"
        available_subjects = []
        if os.path.exists(lp_dir):
            for f in os.listdir(lp_dir):
                if f.endswith(".pdf") or f.endswith(".txt"):
                    subj = f.replace("_LP.pdf", "").replace("_LP.txt", "").replace("_", " ")
                    available_subjects.append(subj)
                    print(f"  - {subj}")
        
        # --- 2. Ask for Subject ---
        subject = input("\n👉 Enter Subject (exactly as shown above): ").strip()
        lesson_plan_path = f"data/lesson_plans/{subject.replace(' ', '_')}_LP.pdf"
        
        if not os.path.exists(lesson_plan_path):
            # Try txt fallback
            lesson_plan_path = f"data/lesson_plans/{subject.replace(' ', '_')}_LP.txt"
            if not os.path.exists(lesson_plan_path):
                print(f"❌ Error: Lesson plan not found for {subject}")
                return

        # --- 3. Ask for Exam Type ---
        print("\n  1. ISA1\n  2. ISA2\n  3. ESA")
        exam_choice = input("👉 Select Exam Type (1/2/3): ").strip()
        
        if exam_choice == "1": 
            exam_type = "ISA1"
            target_batch = "Academic Year 2026"
        elif exam_choice == "2": 
            exam_type = "ISA2"
            target_batch = "Academic Year 2026"
        else: 
            exam_type = "ESA"
            target_batch = "Oct 2025 - Feb 2026"
        
        # --- 4. Ask for Marks ---
        total_marks = int(input(f"👉 Enter Total Marks for {exam_type}: "))

        # --- 5. Ask for Number of Sets (Max 3) ---
        num_sets = int(input("👉 How many question papers to generate simultaneously? (1/2/3): "))
        if num_sets > 3:
            print("⚠️ Maximum 3 sets allowed to prevent memory overload. Generating 3.")
            num_sets = 3

        # --- 6. Launch Swarm ---
        print(f"\n[{self.name}] 🚀 Launching Swarm to generate {num_sets} parallel papers...")
        
        start_time = time.time()
        threads = []

        for i in range(num_sets):
            set_name = f"Set_{chr(65+i)}" # Set_A, Set_B, Set_C
            thread = threading.Thread(
                target=self._generate_paper_thread, 
                args=(subject, exam_type, target_batch, lesson_plan_path, total_marks, set_name)
            )
            threads.append(thread)
            thread.start()

        # Wait for all threads to finish
        for thread in threads:
            thread.join()

        end_time = time.time()
        total_time = round(end_time - start_time, 2)

        # --- 7. Print Summary ---
        print("\n" + "="*60)
        print("  🐝 SWARM EXECUTION SUMMARY")
        print("="*60)
        for res in self.results:
            print(f"  {res}")
        print(f"\n⏱️ Total Time Taken: {total_time} seconds.")
        print(f"📁 Check the 'output/' folder for the generated PDFs!")

if __name__ == "__main__":
    agent = ParallelSwarmAgent()
    agent.run_swarm()