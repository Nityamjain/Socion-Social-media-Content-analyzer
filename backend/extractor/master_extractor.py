import os
from .file_loader import load_file,get_extension
from .pdf_text_extractor import extract_text_from_pdf
from .docx_text_extractor import extract_text_from_docx
from .img_text_extractor import extract_text_with_easyocr

def master_text_extractor(file_path):

    temp_path = None
    extracted_text = ""

    try:
        temp_path = load_file(file_path)
        ext = get_extension(file_path).lower()

        if ext == '.pdf':
            print("→ Using PDF Extractor")
            extracted_text = extract_text_from_pdf(temp_path)

        elif ext == '.docx':
            print("→ Using DOCX Extractor")
            extracted_text = extract_text_from_docx(temp_path)

        elif ext in {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}:
            print("→ Using OCR Extractor")
            extracted_text = extract_text_with_easyocr(temp_path)

        else:
            raise ValueError(f"No extractor available for extension {ext}")

        # Save extracted text
        with open("output_text.txt", "w", encoding="utf-8") as f:
            f.write(extracted_text)

        print(f"→ Success! {len(extracted_text):,} characters saved to output_text.txt")
        return extracted_text

    except Exception as e:
        print(f"Error extracting text: {e}")
        raise

    finally:
        # Always clean temp file if it exists
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
            print("→ Temp file cleaned")
