import json

db_path = "data/real_question_bank.json"

# Load existing data
with open(db_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# These are the missing ISA1 questions for Cloud Computing
new_questions = [
    {
        "id": "Q_ISA1_01",
        "subject": "Cloud Computing",
        "exam_type": "ISA1",
        "year": "2026",
        "batch": "Academic Year 2026",
        "question_text": "Explain the different cloud service models (IaaS, PaaS, SaaS) with real-world examples and compare their levels of control. (10marks)"
    },
    {
        "id": "Q_ISA1_02",
        "subject": "Cloud Computing",
        "exam_type": "ISA1",
        "year": "2026",
        "batch": "Academic Year 2026",
        "question_text": "A company wants to deploy multiple applications with different dependencies on the same Linux server. Discuss how containerization (Docker) provides strong isolation compared to traditional virtual machines. (10marks)"
    },
    {
        "id": "Q_ISA1_03",
        "subject": "Cloud Computing",
        "exam_type": "ISA1",
        "year": "2026",
        "batch": "Academic Year 2026",
        "question_text": "Analyze the role of Kubernetes in container orchestration. How does it address the challenges of scaling and managing microservices? (10marks)"
    }
]

# Check if they already exist to prevent duplicates
existing_ids = {q["id"] for q in data}
added_count = 0

for q in new_questions:
    if q["id"] not in existing_ids:
        data.append(q)
        added_count += 1

# Save back to JSON
with open(db_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4)

print(f"✅ Successfully injected {added_count} ISA1 questions into the database!")