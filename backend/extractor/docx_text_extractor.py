from docx import Document
from io import BytesIO

def extract_text_from_docx(docx_input):
    """
    Accepts path or bytes for docx.

    If bytes, wrap in BytesIO.
    """
    if isinstance(docx_input, bytes):
        docx_file = BytesIO(docx_input)
    else:
        docx_file = docx_input  # assume path string

    doc = Document(docx_file)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)
