import easyocr

def extract_text_with_easyocr(image_path, languages=['en']):
    """
    Extracts text from an image using EasyOCR.

    Args:
        image_path (str): Path to the input image file.
        languages (list): List of language codes (default is English).

    Returns:
        str: Extracted text as a plain string.
    """
    reader = easyocr.Reader(languages)
    results = reader.readtext(image_path, detail=0)  # detail=0 returns only text parts
    text = "\n".join(results)
    return text
