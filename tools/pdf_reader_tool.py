
import pymupdf
from pathlib import Path


def extract_text_from_pdf(pdf_path):
    """Extract text from all pages of a PDF file."""
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        return {
            "status": "error",
            "message": f"PDF not found: {pdf_path}"
        }

    try:
        extracted_pages = []

        with pymupdf.open(pdf_path) as document:
            for page_number, page in enumerate(document, start=1):
                text = page.get_text("text")

                extracted_pages.append({
                    "page": page_number,
                    "text": text.strip()
                })

        return {
            "status": "success",
            "file_name": pdf_path.name,
            "total_pages": len(extracted_pages),
            "pages": extracted_pages
        }

    except Exception as error:
        return {
            "status": "error",
            "message": str(error)
        }
