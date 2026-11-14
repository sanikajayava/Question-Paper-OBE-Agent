import os
from tools.pdf_reader_tool import extract_text_from_pdf

base_path = "data/Question_Papers"

print("===== TESTING ALL PDFs =====\n")

total_pdfs = 0
success_count = 0
failed_pdfs = []

# Walk through all folders and subfolders
for root, dirs, files in os.walk(base_path):
    for file in files:
        if file.lower().endswith(".pdf"):
            total_pdfs += 1
            pdf_path = os.path.join(root, file)
            
            # Get just the relative path for clean printing
            rel_path = os.path.relpath(pdf_path, base_path)
            
            result = extract_text_from_pdf(pdf_path)
            
            if result["status"] == "success":
                # Check if text is actually empty (sometimes OCR finds nothing)
                text_length = len(result["text"].strip())
                if text_length > 50:
                    print(f"✅ SUCCESS: {rel_path} (Extracted {text_length} chars)")
                    success_count += 1
                else:
                    print(f"⚠️ WARNING: {rel_path} (Extracted too little text: {text_length} chars)")
                    failed_pdfs.append(rel_path)
            else:
                print(f"❌ FAILED: {rel_path} (Error: {result['message']})")
                failed_pdfs.append(rel_path)

print("\n===== TEST SUMMARY =====")
print(f"Total PDFs found: {total_pdfs}")
print(f"Successful: {success_count}")
print(f"Failed/Warnings: {len(failed_pdfs)}")

if failed_pdfs:
    print("\nList of failed/warning PDFs:")
    for f in failed_pdfs:
        print(f" - {f}")