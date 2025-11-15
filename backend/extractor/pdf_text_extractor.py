from pdfminer.high_level import extract_text

def extract_text_from_pdf(pdf_path):
    text = extract_text(pdf_path)
    # Further cleaning of newlines or whitespace can be done here if necessary
    return text.strip()


