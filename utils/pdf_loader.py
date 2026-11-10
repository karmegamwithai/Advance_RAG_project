import fitz

def extract_pdf_pages(file_path: str):
    pages = []
    with fitz.open(file_path) as pdf:
        for page_number, page in enumerate(pdf, start=1):
            text = page.get_text("text")
            if text and text.strip():
                pages.append({
                    "page_number": page_number,
                    "text": text,
                })
    if not pages:
        raise ValueError(
            "No extractable text was found. This may be a scanned PDF; OCR is not included."
        )
    return pages
