from agent.coordinator import QuestionPaperCoordinator


coordinator = QuestionPaperCoordinator()

request = "Generate a 50-mark question paper for Agentic AI."

result = coordinator.run(request)

print("\n===== QUESTION PAPER COORDINATOR =====")
print("Agent:", result.get("agent", "Not available"))
print("Goal:", result.get("goal", "Not available"))
print("Status:", result.get("status", "Not available"))

print("\n===== QUESTION PAPER SKILL =====")
print("Blueprint:", result.get("blueprint", {}))

print("\n===== QUESTION BANK TOOL =====")
print("Tool Status:", result.get("question_bank_status", "Not available"))
print("Total Questions:", result.get("question_count", 0))

print("\n===== MEMORY =====")
print("Past Papers Retrieved:", len(result.get("past_papers", [])))

for paper in result.get("past_papers", []):
    print(f"{paper['paper_id']} - {paper['year']}")


if result["status"] == "plan_created":
    print("\nExecution Plan:")

    for number, task in enumerate(result["task_plan"], start=1):
        print(f"{number}. {task}")
else:
    print(result.get("message", "Unknown error"))