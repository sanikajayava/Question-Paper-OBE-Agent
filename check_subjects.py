import json
data = json.load(open('data/real_question_bank.json', encoding='utf-8'))
subjects = set()
for q in data:
    subjects.add(repr(q['subject']))
print("All subjects (with repr):")
for s in sorted(subjects):
    print(f"  {s}")

print("\nGen AI entries detailed:")
for q in data:
    if 'gen' in q['subject'].lower():
        print(f"  id={q['id']} | subject={repr(q['subject'])} | exam={repr(q['exam_type'])} | batch={repr(q['batch'])}")