import json

with open('data/real_question_bank.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

genai = [q for q in data if 'gen' in q['subject'].lower()]
print(f"Total Gen AI questions in DB: {len(genai)}\n")

print("=" * 60)
print("ALL GEN AI QUESTIONS:")
print("=" * 60)

for q in genai:
    text_preview = q['question_text'][:60].replace('\n', ' ')
    print(f"  [{q['id']}] exam={q['exam_type']} | batch={q['batch']}")
    print(f"         text: {text_preview}...")
    print()

# Now check folders on disk
import os
print("=" * 60)
print("FOLDER STRUCTURE ON DISK:")
print("=" * 60)

genai_folder = "data/Question_Papers/Gen_AI"
if os.path.exists(genai_folder):
    for root, dirs, files in os.walk(genai_folder):
        for file in files:
            if file.endswith('.pdf'):
                print(f"  Found PDF: {os.path.join(root, file)}")
else:
    print(f"  ERROR: Folder {genai_folder} does NOT exist!")
    print("  Checking alternative folder names...")
    base = "data/Question_Papers"
    if os.path.exists(base):
        print(f"  Available folders in {base}:")
        for item in os.listdir(base):
            print(f"    - {item}")