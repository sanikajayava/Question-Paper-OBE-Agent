import pymupdf
import pytesseract
from PIL import Image
import io
import os
import shutil

tesseract_cmd = os.getenv("TESSERACT_CMD") or shutil.which("tesseract")
if not tesseract_cmd and os.name == "nt":
    windows_tesseract = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if os.path.isfile(windows_tesseract):
        tesseract_cmd = windows_tesseract

if tesseract_cmd:
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF. If the PDF is scanned (no text),
    it converts the page to an image and uses OCR.
    """
    try:
        document = pymupdf.open(pdf_path)
        extracted_text = ""
        
        for page_number, page in enumerate(document, start=1):
            # 1. Try to extract normal text first (for digital PDFs)
            text = page.get_text("text").strip()
            
            # 2. If no text is found, use OCR (for scanned PDFs)
            if not text:
                # Render page to a pixmap (image)
                pix = page.get_pixmap(dpi=300) # 300 DPI gives good OCR accuracy
                
                # Convert pixmap to PIL Image
                img_bytes = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_bytes))
                
                # Use Tesseract to extract text
                text = pytesseract.image_to_string(img)
                
            extracted_text += f"\n--- Page {page_number} ---\n{text}\n"
            
        document.close()
        return {
            "status": "success",
            "text": extracted_text
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }