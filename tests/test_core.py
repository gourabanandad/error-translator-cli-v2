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


# --- 3. INTERACTIVE MODE TESTS ---

def _stub_input(monkeypatch, responses):
    """Patch builtins.input to yield `responses` in order, then raise EOFError (stdin closed)."""
    it = iter(responses)

    def fake_input(prompt=""):
        try:
            return next(it)
        except StopIteration:
            raise EOFError

    monkeypatch.setattr("builtins.input", fake_input)


def test_interactive_translates_single_line_then_exits(capsys, monkeypatch):
    from error_translator.cli import run_interactive_session

    _stub_input(monkeypatch, [
        "NameError: name 'my_variable' is not defined",
        "",       # blank line submits the single-line entry
        "exit",   # leaves the session
    ])
    run_interactive_session(as_json=False)

    captured = capsys.readouterr().out
    assert "my_variable" in captured
    assert "Exiting interactive mode" in captured


def test_interactive_quit_command_is_case_insensitive_and_skips_translation(capsys, monkeypatch):
    from error_translator.cli import run_interactive_session

    _stub_input(monkeypatch, ["QUIT"])
    run_interactive_session(as_json=False)

    captured = capsys.readouterr().out
    assert "Detected Error" not in captured
    assert "Exiting interactive mode" in captured


def test_interactive_eof_at_prompt_ends_session_without_crashing(monkeypatch):
    from error_translator.cli import run_interactive_session

    _stub_input(monkeypatch, [])  # first input() call raises EOFError immediately
    run_interactive_session(as_json=False)  # must return cleanly, not raise


def test_interactive_blank_first_line_is_ignored_not_submitted(capsys, monkeypatch):
    from error_translator.cli import run_interactive_session

    _stub_input(monkeypatch, [
        "",     # accidental empty Enter at the prompt: should just re-prompt
        "exit",
    ])
    run_interactive_session(as_json=False)

    captured = capsys.readouterr().out
    assert "Detected Error" not in captured


def test_interactive_multiline_paste_is_one_translation(capsys, monkeypatch):
    """A pasted multi-line traceback (ended by a blank line) must be translated as a single unit,
    not as one call per line."""
    from error_translator.cli import run_interactive_session

    _stub_input(monkeypatch, [
        "Traceback (most recent call last):",
        '  File "script.py", line 2, in <module>',
        "    print(my_variable)",
        "NameError: name 'my_variable' is not defined",
        "",       # blank line submits the whole block
        "exit",
    ])
    run_interactive_session(as_json=False)

    captured = capsys.readouterr().out
    # Only one "Detected Error" panel should appear, proving the 4 lines were joined.
    assert captured.count("Detected Error") == 1
    assert "script.py" in captured


def test_interactive_two_separate_entries_in_one_session(capsys, monkeypatch):
    from error_translator.cli import run_interactive_session

    _stub_input(monkeypatch, [
        "NameError: name 'a' is not defined", "",
        "NameError: name 'b' is not defined", "",
        "exit",
    ])
    run_interactive_session(as_json=False)

    captured = capsys.readouterr().out
    assert captured.count("Detected Error") == 2
    assert "'a' is not defined" in captured
    assert "'b' is not defined" in captured


def test_interactive_json_mode_emits_one_json_line_per_entry_and_skips_banner(capsys, monkeypatch):
    import json
    from error_translator.cli import run_interactive_session

    _stub_input(monkeypatch, [
        "NameError: name 'x' is not defined", "",
        "exit",
    ])
    run_interactive_session(as_json=True)

    captured = capsys.readouterr().out
    json_lines = [line for line in captured.splitlines() if line.strip().startswith("{")]
    assert len(json_lines) == 1
    parsed = json.loads(json_lines[0])
    assert "x" in parsed["explanation"]
    # The decorative Rich panel should not be printed in --json mode.
    assert "Interactive Mode" not in captured


def test_interactive_subcommand_is_wired_into_main(monkeypatch):
    """`explain-error interactive` should dispatch to run_interactive_session, not be treated
    as a raw traceback string."""
    import sys
    import error_translator.cli as cli_module

    monkeypatch.setattr(sys, "argv", ["explain-error", "interactive"])
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)

    called = {}
    def fake_run_interactive_session(as_json=False):
        called["hit"] = True
        called["as_json"] = as_json

    monkeypatch.setattr(cli_module, "run_interactive_session", fake_run_interactive_session)
    cli_module.main()

    assert called.get("hit") is True
    assert called.get("as_json") is False
    assert "CLI Options & Flags" in captured
