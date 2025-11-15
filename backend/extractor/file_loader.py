import os
import shutil

# Allowed extensions and max file size (e.g., 10MB)
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.jpg', '.png','.jpeg', '.bmp', '.tiff'}
MAX_FILE_SIZE_MB = 10
TEMP_FOLDER = 'temp/'

def ensure_temp_folder():
    if not os.path.exists(TEMP_FOLDER):
        os.makedirs(TEMP_FOLDER)

def get_extension(filename):
    return os.path.splitext(filename)[1].lower()

def validate_file(file_path):
    # Check extension
    ext = get_extension(file_path)
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file extension: {ext}")

    # Check file size
    size_in_mb = os.path.getsize(file_path) / (1024 * 1024)
    if size_in_mb > MAX_FILE_SIZE_MB:
        raise ValueError(f"File size {size_in_mb:.2f}MB exceeds the limit of {MAX_FILE_SIZE_MB}MB.")

def save_temp_file(file_path):
    ensure_temp_folder()
    filename = os.path.basename(file_path)
    temp_path = os.path.join(TEMP_FOLDER, filename)

    # Copy file to temp folder
    shutil.copy2(file_path, temp_path)
    return temp_path

def load_file(file_path):
    validate_file(file_path)
    temp_path = save_temp_file(file_path)

    with open(temp_path, 'rb') as f:
        raw_data = f.read()

    return raw_data
