import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from each page of the given PDF.

    Returns a list of dictionaries containing:
    - page_number (starting from 1)
    - text (full page text)
    """
    doc = fitz.open(pdf_path)
    extracted = []

    for page_number in range(len(doc)):
        page = doc.load_page(page_number)
        text = page.get_text()

        if text.strip():  # Skip empty pages
            extracted.append({
                "page_number": page_number + 1,
                "text": text
            })

    doc.close()
    return extracted