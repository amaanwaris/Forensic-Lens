# modules/file_analysis.py
import magic  # pip install python-magic

def analyze_file(file_path):
    """
    Detect file type using magic numbers.
    Returns file type as string.
    """
    try:
        file_type = magic.from_file(file_path)
        print(f"[File Analysis] File: {file_path}, Type: {file_type}")
        return file_type
    except Exception as e:
        print(f"[File Analysis] Error analyzing file: {e}")
        return None

