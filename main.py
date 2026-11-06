from tools.pdf_reader_tool import extract_text_from_pdf

pdf_path = "data/Question_Papers/Cloud_Computing/ESA/ESA_2025.pdf"

result = extract_text_from_pdf(pdf_path)

print("\n===== PDF READER TEST =====")
print("Status:", result["status"])

if result["status"] == "success":
    print("File:", result["file_name"])
    print("Total Pages:", result["total_pages"])

    for page in result["pages"]:
        print(f"\n===== PAGE {page['page']} =====")
        print(page["text"][:1000])
else:
    print("Error:", result["message"])