"""
Traceback parsing module.
Responsible for extracting contextual information from traceback strings.
"""
import re
import linecache

def extract_location(traceback_text: str) -> tuple[str, str]:
    """
    Extract the file name and line number where the error occurred
    by parsing the standard Python traceback format.
    
    Args:
        traceback_text (str): The raw traceback text.
        
    Returns:
        tuple[str, str]: The file name and line number.
    """
    # Regex to capture "File <path>, line <number>"
    location_match = re.search(r'File\s+[\'"]?(.*?)[\'"]?,\s+line\s+(\d+)', traceback_text)
    if not location_match:
        return "Unknown File", "Unknown Line"
    return location_match.group(1), location_match.group(2)

def extract_code_context(file_name: str, line_number: str) -> str:
    """
    Attempt to read the exact line of code that caused the error.
    
    Args:
        file_name (str): Path to the source file.
        line_number (str): Line number string.
        
    Returns:
        str: The extracted line of code, or empty string if not found.
    """
    if file_name != "Unknown File" and line_number != "Unknown Line":
        try:
            raw_line = linecache.getline(file_name, int(line_number))
            if raw_line:
                return raw_line.strip()
        except Exception:
            pass
    return ""
