import sys
import os
import json
import re

# Add project root to path so 'tools' can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.pdf_reader_tool import extract_text_from_pdf

BASE_PDF_DIR = "data/Question_Papers"
OUTPUT_JSON = "data/real_question_bank.json"

def clean_text(text):
    # Clean up OCR noise
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n+', '\n', text)
    return text.strip()

def parse_batch_and_year(exam_type, year_str):
    try:
        year = int(year_str)
        if exam_type == "ESA":
            return f"Oct {year-1} - Feb {year}"
        else:
            return f"Academic Year {year}"
    except ValueError:
        return "Unknown"

def build_database():
    all_questions = []
    question_id_counter = 1

    print("Starting Smarter Database Build from PDFs...\n")

    for root, dirs, files in os.walk(BASE_PDF_DIR):
        for file in files:
            if not file.lower().endswith(".pdf"):
                continue

            pdf_path = os.path.join(root, file)
            parts = root.replace("\\", "/").split("/")
            subject = parts[-2].replace("_", " ")
            exam_type = parts[-1]
            
            year_match = re.search(r'(\d{4})', file)
            year = year_match.group(1) if year_match else "Unknown"
            batch = parse_batch_and_year(exam_type, year)

            print(f"Processing: {subject} | {exam_type} | {year}")

            result = extract_text_from_pdf(pdf_path)
            if result["status"] != "success":
                print(f"  -> Skipping due to error.")
                continue

            raw_text = clean_text(result["text"])

            # Smarter Split Logic:
            # Looks for question numbers (1.a, 2, Q1) OR marks (10 marks, (08marks))
            split_pattern = r'(?=(?:Q?\.?\s*\d+[a-z]?\s*[\.\)]|\b\d{1,2}\s*(?:marks|Marks|MARKs)\b|\(\d+\s*marks\)))'
            
            chunks = re.split(split_pattern, raw_text)
            
            for chunk in chunks:
                chunk = chunk.strip()
                
                # Filter out very short chunks (headers, page numbers, table rows)
                if len(chunk) < 40:
                    continue
                    
                # Filter out obvious non-questions (university headers)
                if "KLE Technological" in chunk or "Course Code" in chunk or "Model Question Paper" in chunk or "Max. Marks" in chunk or "Department of" in chunk:
                    continue

                all_questions.append({
                    "id": f"Q{question_id_counter:04d}",
                    "subject": subject,
                    "exam_type": exam_type,
                    "year": year,
                    "batch": batch,
                    "question_text": chunk,
                })
                question_id_counter += 1

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(all_questions, f, indent=4)

    print(f"\nSUCCESS: Extracted {len(all_questions)} smarter chunks.")
    print(f"Database saved to: {OUTPUT_JSON}")

if __name__ == "__main__":
    build_database()