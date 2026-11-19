import json

with open('data/real_question_bank.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("--- Checking Cloud Computing Questions ---")
for q in data:
    if "cloud" in q["subject"].lower():
        print(f"ID: {q['id']} | Exam: '{q['exam_type']}' | Batch: '{q['batch']}'")