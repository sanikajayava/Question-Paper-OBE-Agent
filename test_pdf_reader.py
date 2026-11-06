import pymupdf

pdf_path = "data/Question_Papers/Cloud_Computing/ESA/ESA_2025.pdf"

document = pymupdf.open(pdf_path)

for page_number, page in enumerate(document, start=1):
    print(f"\nPage {page_number}")
    print("Text blocks:", len(page.get_text("blocks")))
    print("Images:", len(page.get_images(full=True)))

document.close()