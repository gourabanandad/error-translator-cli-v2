import pytest
from error_translator.core import translate_error, load_rules, compiled_rules

# --- 1. EDGE CASE TESTS ---

def test_name_error_translation_double_quotes():
    """Test standard traceback with double quotes around the filename."""
    mock_traceback = """Traceback (most recent call last):
  File "script.py", line 2, in <module>
    print(my_variable)
NameError: name 'my_variable' is not defined"""

    result = translate_error(mock_traceback)
    assert "my_variable" in result["explanation"]
    assert result["file"] == "script.py"
    assert result["line"] == "2"

def test_name_error_translation_single_quotes():
    """Test PowerShell-style traceback with single quotes."""
    mock_traceback = """Traceback (most recent call last):
  File 'script.py', line 2, in <module>
    print(my_variable)
NameError: name 'my_variable' is not defined"""

    result = translate_error(mock_traceback)
    assert result["file"] == "script.py"
    assert result["line"] == "2"

def test_unknown_error_fallback():
    """Test that garbage input returns the default safe message."""
    mock_traceback = "Something completely random went wrong here."
    result = translate_error(mock_traceback)
    
    assert "unknown error" in result["explanation"]
    assert result["matched_error"] == "Something completely random went wrong here."


def test_empty_input_returns_helpful_message():
    result = translate_error("   \n   ")
    assert result["explanation"] == "No error text provided."
    assert result["fix"] == "Provide a valid Python error."


def test_unexpected_eof_translation():
    """Unexpected EOF should explain the likely missing closing delimiter."""
    mock_traceback = """Traceback (most recent call last):
  File "script.py", line 8
    print("hello"
                 ^
SyntaxError: unexpected EOF while parsing"""

    result = translate_error(mock_traceback)

    assert "end of your file before the code was finished" in result["explanation"]
    assert "properly closed" in result["fix"]
    assert result["file"] == "script.py"
    assert result["line"] == "8"


def test_rule_loading_is_cached():
    first = load_rules()
    second = load_rules()
    assert first is second


def test_compiled_rules_are_cached():
    first = compiled_rules()
    second = compiled_rules()
    assert first is second


# --- 2. THE PARAMETERIZED ENGINE FOR ALL ERRORS ---

@pytest.mark.parametrize("mock_traceback, expected_in_explanation", [
    (
        """Traceback (most recent call last):
  File "script.py", line 5, in <module>
    print("Age: " + 25)
TypeError: can only concatenate str (not "int") to str""",
        "int"  # Checks if regex (*.) captured the type 'int'
    ),
    (
        """Traceback (most recent call last):
  File "script.py", line 5, in <module>
    result = 5 + "10"
TypeError: unsupported operand type(s) for +: 'int' and 'str'""",
        "int"  # Checks if regex captured the first type
    ),
    (
        """Traceback (most recent call last):
  File "script.py", line 5, in <module>
    my_list[10]
IndexError: list index out of range""",
        "position that doesn't exist"
    ),
    (
        """Traceback (most recent call last):
  File "script.py", line 5, in <module>
    my_dict['missing_key']
KeyError: 'missing_key'""",
        "missing_key" # Checks if regex captured the key name
    ),
    (
        """Traceback (most recent call last):
  File "script.py", line 5, in <module>
    1 / 0
ZeroDivisionError: division by zero""",
        "divide a number by zero"
    ),
    (
        """Traceback (most recent call last):
  File "script.py", line 5, in <module>
    import numpy
ModuleNotFoundError: No module named 'numpy'""",
        "numpy" # Checks if regex captured the module name
    ),
    (
        """Traceback (most recent call last):
  File "script.py", line 5, in <module>
    [].appendd(1)
AttributeError: 'list' object has no attribute 'appendd'""",
        "appendd" # Checks if regex captured the method typo
    ),
    (
        """Traceback (most recent call last):
  File "script.py", line 5, in <module>
    int("abc")
ValueError: invalid literal for int() with base 10: 'abc'""",
        "abc" # Checks if regex captured the bad value
    ),
    (
        """Traceback (most recent call last):
  File "script.py", line 5, in <module>
    open('data.csv')
FileNotFoundError: [Errno 2] No such file or directory: 'data.csv'""",
        "data.csv" # Checks if regex captured the missing filename
    ),
    (
        """Traceback (most recent call last):
  File "script.py", line 5, in <module>
    from math import pie
ImportError: cannot import name 'pie' from 'math'""",
        "pie" # Checks if regex captured the bad import
    ),
    (
        """  File "script.py", line 5
    if True
           ^
SyntaxError: invalid syntax""",
        "grammar"
    )
])
def test_regex_extraction_for_supported_errors(mock_traceback, expected_in_explanation):
    """
    This single function will run 11 different times automatically, 
    once for every error in the list above!
    """
    result = translate_error(mock_traceback)
    
    # 1. Prove the Regex Engine successfully extracted the variable and injected it
    assert expected_in_explanation in result["explanation"], f"Failed to find '{expected_in_explanation}' in explanation."
    
    # 2. Prove the Context Engine successfully parsed the file location
    assert result["file"] == "script.py"
    assert result["line"] == "5"


def test_print_result_json_emits_valid_json(capsys):
    """The --json formatter writes a single line of valid JSON containing the result keys."""
    import json
    from error_translator.cli import print_result_json

    payload = {
        "explanation": "x is undefined",
        "fix": "Define x before use",
        "matched_error": "NameError: name 'x' is not defined",
        "file": "Unknown File",
        "line": "Unknown Line",
        "code": "",
        "ast_insight": None,
    }
    print_result_json(payload)
    captured = capsys.readouterr().out
    # Single line, valid JSON, contains the key fields
    assert captured.count("\n") == 1
    parsed = json.loads(captured.strip())
    assert parsed == payload


def test_cli_help(capsys, monkeypatch):
    """Test that running the main CLI entrypoint with help flags displays the help information."""
    import sys
    from error_translator.cli import main

    monkeypatch.setattr(sys, "argv", ["explain-error", "--help"])
    
    with pytest.raises(SystemExit) as excinfo:
        main()
        
    assert excinfo.value.code == 0
    captured = capsys.readouterr().out
    assert "Error Translator CLI" in captured
    assert "Command Line Interface" in captured
    assert "CLI Options & Flags" in captured
