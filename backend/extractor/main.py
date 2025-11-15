from master_extractor import master_text_extractor

if __name__ == "__main__":
    # Just change this path — everything else works automatically
    # FILE_PATH = r"C:\Users\admin\Downloads\Copy of Social Media Content Analyzer - Assignment 2 (2).pdf"
    FILE_PATH = r"Trainees- JD.docx"
    # FILE_PATH = r"D:\smca\Text Extraction\test.png"

    try:
        text = master_text_extractor(FILE_PATH)
        print("\n" + "="*60)
        print("PREVIEW (first 500 chars):")
        print(text[:500] + ("..." if len(text) > 500 else ""))
        print("="*60)
    except Exception as e:
        print(f"ERROR: {e}")