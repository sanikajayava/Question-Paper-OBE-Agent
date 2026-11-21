
import time
import threading
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from agent.coordinator import QuestionPaperCoordinator


class ParallelSwarmAgent:
    def __init__(self):
        self.name = "Lab 8: Parallel Swarm"
        self.results = []
        self.lock = threading.Lock()

    def _generate_paper_thread(
        self,
        subject,
        exam_type,
        target_batch,
        lesson_plan_path,
        total_marks,
        set_name
    ):
        """Generate one question paper independently."""

        print(f"\n[Thread Started] Generating {set_name} for {subject}")

        start_time = time.time()

        try:
            coordinator = QuestionPaperCoordinator()

            paper = coordinator.run_workflow(
                subject=subject,
                exam_type=exam_type,
                target_batch=target_batch,
                lesson_plan_path=lesson_plan_path,
                total_marks=total_marks,
                set_name=set_name,
                generate_valuation=False
            )

            output_dir = "output"
            subject_name = subject.replace(" ", "_")
            suffix = f"_{set_name}"

            json_path = os.path.join(
                output_dir,
                f"{subject_name}_{exam_type}{suffix}_Paper.json"
            )

            pdf_path = os.path.join(
                output_dir,
                f"{subject_name}_{exam_type}{suffix}_Paper.pdf"
            )

            result = {
                "set_name": set_name,
                "status": "success",
                "paper": paper,
                "json_path": json_path,
                "pdf_path": pdf_path,
                "time_taken": round(time.time() - start_time, 2),
                "error": None
            }

            print(f"[Completed] {set_name}: {pdf_path}")

        except Exception as e:

            result = {
                "set_name": set_name,
                "status": "failed",
                "paper": None,
                "json_path": None,
                "pdf_path": None,
                "time_taken": round(time.time() - start_time, 2),
                "error": str(e)
            }

            print(f"[Failed] {set_name}: {e}")

        with self.lock:
            self.results.append(result)

        return result

    def run_swarm(
        self,
        subject,
        exam_type,
        target_batch,
        lesson_plan_path,
        total_marks,
        num_sets=1
    ):
        """Generate 1, 2, or 3 papers using parallel threads."""

        if not isinstance(num_sets, int) or isinstance(num_sets, bool):
            raise ValueError("Number of papers must be an integer.")

        if num_sets < 1 or num_sets > 3:
            raise ValueError("You can generate between 1 and 3 papers.")

        self.results = []

        set_names = [
            f"Set_{chr(65 + i)}"
            for i in range(num_sets)
        ]

        print(
            f"\n[{self.name}] Starting parallel generation "
            f"for {num_sets} paper(s)."
        )

        start_time = time.time()

        with ThreadPoolExecutor(max_workers=num_sets) as executor:

            futures = [
                executor.submit(
                    self._generate_paper_thread,
                    subject,
                    exam_type,
                    target_batch,
                    lesson_plan_path,
                    total_marks,
                    set_name
                )
                for set_name in set_names
            ]

            for future in as_completed(futures):
                future.result()

        self.results.sort(
            key=lambda item: item["set_name"]
        )

        print("\n" + "=" * 55)
        print("PARALLEL GENERATION SUMMARY")
        print("=" * 55)

        for result in self.results:
            print(
                f"{result['set_name']}: {result['status']}"
            )

        print(
            f"Total time: {round(time.time() - start_time, 2)} seconds"
        )

        return self.results


if __name__ == "__main__":

    agent = ParallelSwarmAgent()

    results = agent.run_swarm(
        subject="Cloud Computing",
        exam_type="ESA",
        target_batch="2027",
        lesson_plan_path="data/lesson_plans/Cloud_Computing_LP.pdf",
        total_marks=60,
        num_sets=2
    )

    print("\nGenerated papers:")
    for result in results:
        if result["status"] == "success":
            print(result["pdf_path"])
