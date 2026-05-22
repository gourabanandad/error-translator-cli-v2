"""
Core translation engine for the Error Translator CLI.

This module is responsible for:
1. Orchestrating error translation.
2. Using a fast C extension for matching if available, with a Python fallback.
3. Delegating to AST handlers for deep, code-specific insights.
"""
from .ast.ast_handlers import AST_REGISTRY
from .rules import load_rules, compiled_rules
from .parser import extract_location, extract_code_context

# Attempt to load the ultra-fast C extension for matching rules,
# and fallback to the Python implementation if it's unavailable.
try:
    from .fast_matcher import match_loop  # type: ignore
    C_EXTENSION_AVAILABLE = True
except ImportError:
    C_EXTENSION_AVAILABLE = False


def translate_error(traceback_text: str) -> dict:
    """
    Translate a raw traceback string into a detailed explanation dictionary.
    
    Args:
        traceback_text (str): The raw traceback string.
        
    Returns:
        dict: A dictionary containing the explanation, suggested fix,
              AST-based insight (if any), file, line number, code context, 
              and the matched error line.
    """
    # Load configuration rules and pre-compiled regex patterns
    data = load_rules()
    rules = compiled_rules()
    default_error = data["default"]

    # Extract non-empty lines from the traceback
    lines = [line.strip() for line in traceback_text.strip().split("\n") if line.strip()]
    if not lines:
        return {"explanation": "No error text provided.", "fix": "Provide a valid Python error."}

    # The actual error message is typically the last line in a traceback
    actual_error_line = lines[-1]

    # Extract the origin of the error (file name and line number)
    file_name, line_number = extract_location(traceback_text)

    # Attempt to read the exact line of code that caused the error
    code_context = extract_code_context(file_name, line_number)

    # ==========================================
    # FAST MATCHING ENGINE (C Extension + Python Fallback)
    # ==========================================
    match = None
    rule = None

    if C_EXTENSION_AVAILABLE:
        # Execute the C extension for maximum performance
        result = match_loop(actual_error_line, rules)
        if result:
            match, rule = result
    else:
        # Fallback to standard Python regex loop
        for pattern, r in rules:
            m = pattern.search(actual_error_line)
            if m:
                match, rule = m, r
                break

    # If we found a matching rule, format the explanation and fix
    if match and rule:
        # Extract variables from the regex groups (e.g., variable names, functions)
        extracted_values = list(match.groups())
        
        # Inject the extracted values into the template fix string
        fix_text = rule["fix"].format(*extracted_values)

        # Parse the error type (e.g., "NameError", "TypeError") to dispatch AST insights
        error_type = actual_error_line.split(":")[0].strip()
        
        # Check if there's a specialized AST handler for this specific error type
        handler_function = AST_REGISTRY.get(error_type)
        insight = None
        
        # If an AST handler exists and the file is accessible, run deep code analysis
        if handler_function and file_name != "Unknown File":
            insight = handler_function(file_name, line_number, extracted_values)
        
        return {
            "explanation": rule["explanation"].format(*extracted_values),
            "fix": fix_text,
            "ast_insight": insight,
            "matched_error": actual_error_line,
            "file": file_name,
            "line": line_number,
            "code": code_context,
        }

    # Fallback when the error doesn't match any known rules
    return {
        "explanation": default_error["explanation"],
        "fix": default_error["fix"],
        "matched_error": actual_error_line,
        "file": file_name,
        "line": line_number,
        "code": code_context,
    }