import sys

import pytest


def test_raw_traceback_argument_shows_explanation_and_translation(capsys, monkeypatch):
    """`explain-error "NameError: ..."` should translate the string and print
    an Explanation panel, without raising / exiting with an error."""
    from error_translator.cli import main

    monkeypatch.setattr(sys, "argv", ["explain-error", "NameError: name 'foo' is not defined"])
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)

    main()  # should return normally (no sys.exit on this path)

    captured = capsys.readouterr().out
    assert "Explanation" in captured
    assert "foo" in captured


def test_raw_traceback_argument_with_json_flag_emits_json(capsys, monkeypatch):
    import json

    from error_translator.cli import main

    monkeypatch.setattr(
        sys, "argv", ["explain-error", "--json", "NameError: name 'foo' is not defined"]
    )
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)

    main()

    captured = capsys.readouterr().out
    parsed = json.loads(captured.strip())
    assert "foo" in parsed["explanation"]


def test_about_flag_shows_about_screen_and_exits_zero(capsys, monkeypatch):
    from error_translator.cli import main

    monkeypatch.setattr(sys, "argv", ["explain-error", "--about"])
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)

    with pytest.raises(SystemExit) as excinfo:
        main()

    assert excinfo.value.code == 0
    captured = capsys.readouterr().out
    assert "Project" in captured
    assert "Features" in captured


def test_version_flag_shows_version_and_exits_zero(capsys, monkeypatch):
    from error_translator.cli import main

    monkeypatch.setattr(sys, "argv", ["explain-error", "--version"])
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)

    with pytest.raises(SystemExit) as excinfo:
        main()

    assert excinfo.value.code == 0
    captured = capsys.readouterr().out
    assert "Version" in captured
    assert "Python:" in captured
    assert "C Extension:" in captured
    assert "Platform:" in captured


def test_no_arguments_shows_help_and_exits_with_code_one(capsys, monkeypatch):
    """Running the CLI with no arguments at all should show help and exit(1),
    not silently do nothing or crash."""
    from error_translator.cli import main

    monkeypatch.setattr(sys, "argv", ["explain-error"])
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)

    with pytest.raises(SystemExit) as excinfo:
        main()

    assert excinfo.value.code == 1
    captured = capsys.readouterr().out
    assert "Command Line Interface" in captured


def test_piped_stdin_input_is_translated(capsys, monkeypatch):
    """`cat error.log | explain-error` — stdin is not a TTY, so the piped text
    is read and translated directly, without needing any positional args."""
    from error_translator.cli import main

    monkeypatch.setattr(sys, "argv", ["explain-error"])
    monkeypatch.setattr(sys.stdin, "isatty", lambda: False)
    monkeypatch.setattr(sys.stdin, "read", lambda: "NameError: name 'bar' is not defined")

    main()

    captured = capsys.readouterr().out
    assert "bar" in captured


def test_run_subcommand_translates_failing_script_traceback(capsys, monkeypatch, tmp_path):
    """`explain-error run script.py` should execute the script and translate
    whatever traceback it raises on stderr."""
    from error_translator.cli import main

    script = tmp_path / "failing_script.py"
    script.write_text("print('hello from script')\nprint(undefined_variable)\n")

    monkeypatch.setattr(sys, "argv", ["explain-error", "run", str(script)])
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)

    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code == 1

    captured = capsys.readouterr().out
    assert "hello from script" in captured  # the script's own stdout is preserved
    assert "undefined_variable" in captured  # the NameError got translated


def test_run_subcommand_missing_script_reports_detected_error(capsys, monkeypatch):
    """`explain-error run nonexistent.py` must not crash the CLI; it should
    surface a translated/handled error instead."""
    from error_translator.cli import main

    monkeypatch.setattr(sys, "argv", ["explain-error", "run", "definitely_missing_script.py"])
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)

    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code == 127

    captured = capsys.readouterr().out
    assert (
        "No such file" in captured or "can't open file" in captured or "Execution Error" in captured
    )


def test_run_subcommand_sys_exit_code_is_propagated(capsys, monkeypatch, tmp_path):
    """`explain-error run script.py` should exit with the same code if the script explicitly sys.exits."""
    from error_translator.cli import main

    script = tmp_path / "exit_script.py"
    script.write_text("import sys\nprint('about to exit 3')\nsys.exit(3)\n")

    monkeypatch.setattr(sys, "argv", ["explain-error", "run", str(script)])
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)

    with pytest.raises(SystemExit) as excinfo:
        main()

    assert excinfo.value.code == 3
    captured = capsys.readouterr().out
    assert "about to exit 3" in captured


def test_run_subcommand_successful_script_exits_zero(capsys, monkeypatch, tmp_path):
    """`explain-error run script.py` should exit 0 if the script succeeds."""
    from error_translator.cli import main

    script = tmp_path / "success_script.py"
    script.write_text("print('success')\n")

    monkeypatch.setattr(sys, "argv", ["explain-error", "run", str(script)])
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)

    with pytest.raises(SystemExit) as excinfo:
        main()

    assert excinfo.value.code == 0
    captured = capsys.readouterr().out
    assert "success" in captured


def test_piped_stdin_ignored_when_positional_string_provided(capsys, monkeypatch):
    from error_translator.cli import main

    monkeypatch.setattr(sys, "argv", ["explain-error", "ValueError: explicit string"])
    monkeypatch.setattr(sys.stdin, "isatty", lambda: False)
    monkeypatch.setattr(sys.stdin, "read", lambda: "NameError: name 'piped_junk' is not defined")

    main()

    captured = capsys.readouterr().out
    assert "explicit string" in captured
    assert "piped_junk" not in captured


def test_no_arguments_with_tty_stdin_does_not_read(capsys, monkeypatch):
    from error_translator.cli import main

    read_called = False

    def mock_read():
        nonlocal read_called
        read_called = True
        return ""

    monkeypatch.setattr(sys, "argv", ["explain-error"])
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(sys.stdin, "read", mock_read)

    with pytest.raises(SystemExit) as excinfo:
        main()

    assert excinfo.value.code == 1
    assert not read_called
    captured = capsys.readouterr().out
    assert "Command Line Interface" in captured


def test_run_subcommand_ignores_piped_stdin(capsys, monkeypatch, tmp_path):
    from error_translator.cli import main

    script = tmp_path / "success_script.py"
    script.write_text("print('success')\n")

    monkeypatch.setattr(sys, "argv", ["explain-error", "run", str(script)])
    monkeypatch.setattr(sys.stdin, "isatty", lambda: False)
    monkeypatch.setattr(sys.stdin, "read", lambda: "NameError: name 'piped_junk' is not defined")

    with pytest.raises(SystemExit) as excinfo:
        main()

    assert excinfo.value.code == 0
    captured = capsys.readouterr().out
    assert "success" in captured
    assert "piped_junk" not in captured


def test_explicit_stdin_dash_argument(capsys, monkeypatch):
    from error_translator.cli import main

    monkeypatch.setattr(sys, "argv", ["explain-error", "-"])
    monkeypatch.setattr(sys.stdin, "isatty", lambda: False)
    monkeypatch.setattr(sys.stdin, "read", lambda: "NameError: name 'dash_input' is not defined")

    main()

    captured = capsys.readouterr().out
    assert "dash_input" in captured


def test_run_subcommand_forwards_args(capsys, monkeypatch, tmp_path):
    from error_translator.cli import main

    script = tmp_path / "show.py"
    script.write_text("import sys\nprint(sys.argv[1:])\n")
    monkeypatch.setattr(sys, "argv", ["explain-error", "run", str(script), "--verbose", "extra"])
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code == 0
    captured = capsys.readouterr().out
    assert "['--verbose', 'extra']" in captured


def test_direct_path_forwards_args(capsys, monkeypatch, tmp_path):
    from error_translator.cli import main

    script = tmp_path / "show.py"
    script.write_text("import sys\nprint(sys.argv[1:])\n")
    monkeypatch.setattr(sys, "argv", ["explain-error", str(script), "--flag", "value"])
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code == 0
    captured = capsys.readouterr().out
    assert "['--flag', 'value']" in captured


def test_cli_flags_are_still_parsed_for_ourselves(capsys, monkeypatch, tmp_path):
    import json

    from error_translator.cli import main

    script = tmp_path / "crash.py"
    script.write_text("1/0\n")
    monkeypatch.setattr(sys, "argv", ["explain-error", "--json", "run", str(script), "--arg"])
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code != 0
    captured = capsys.readouterr().out
    parsed = json.loads(captured.strip())
    assert "divide a number by zero" in parsed["explanation"]


def test_exit_code_propagation_with_args(capsys, monkeypatch, tmp_path):
    from error_translator.cli import main

    script = tmp_path / "e3.py"
    script.write_text("import sys\nprint('exiting with args', sys.argv[1:])\nsys.exit(3)\n")
    monkeypatch.setattr(sys, "argv", ["explain-error", "run", str(script), "-x", "1"])
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code == 3
    captured = capsys.readouterr().out
    assert "exiting with args ['-x', '1']" in captured


def test_raw_multi_word_error_text_still_translated(capsys, monkeypatch):
    from error_translator.cli import main

    monkeypatch.setattr(
        sys, "argv", ["explain-error", "ZeroDivisionError:", "division", "by", "zero"]
    )
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    main()
    captured = capsys.readouterr().out
    assert "divide a number by zero" in captured


def test_crashing_child_with_args_still_translated(capsys, monkeypatch, tmp_path):
    from error_translator.cli import main

    script = tmp_path / "crash_args.py"
    script.write_text(
        "import sys\nprint('args', sys.argv[1:])\nraise NameError(\"name 'foo' is not defined\")\n"
    )
    monkeypatch.setattr(sys, "argv", ["explain-error", "run", str(script), "--bad"])
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code != 0
    captured = capsys.readouterr().out
    assert "args ['--bad']" in captured
    assert "foo" in captured


def test_interactive_session_json(capsys, monkeypatch):
    import json

    from error_translator.cli import run_interactive_session

    inputs = ["ZeroDivisionError: division by zero", EOFError, EOFError]

    def mock_input(prompt=""):
        val = inputs.pop(0)
        if isinstance(val, type) and issubclass(val, Exception):
            raise val()
        return val

    monkeypatch.setattr("builtins.input", mock_input)

    run_interactive_session(as_json=True)

    captured = capsys.readouterr()
    lines = [line for line in captured.out.splitlines() if line.strip()]
    for line in lines:
        parsed = json.loads(line)
        assert "ZeroDivisionError" in parsed.get(
            "matched_error", ""
        ) or "divide a number by zero" in parsed.get("explanation", "")

    assert "Enter error:" in captured.err


def test_interactive_session_text(capsys, monkeypatch):
    from error_translator.cli import run_interactive_session

    inputs = ["ZeroDivisionError: division by zero", EOFError, EOFError]

    def mock_input(prompt=""):
        val = inputs.pop(0)
        if isinstance(val, type) and issubclass(val, Exception):
            raise val()
        return val

    monkeypatch.setattr("builtins.input", mock_input)

    run_interactive_session(as_json=False)

    captured = capsys.readouterr()
    assert "divide a number by zero" in captured.out
    assert "Enter error:" in captured.err


def test_interactive_session_json_ctrl_c(capsys, monkeypatch):
    from error_translator.cli import run_interactive_session

    def mock_input(prompt=""):
        raise KeyboardInterrupt()

    monkeypatch.setattr("builtins.input", mock_input)

    run_interactive_session(as_json=True)

    captured = capsys.readouterr()
    assert captured.out == ""
    assert "Enter error:" in captured.err


def test_help_writes_nothing(monkeypatch, tmp_path):
    from error_translator.cli import main

    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)
    monkeypatch.setattr(sys, "argv", ["explain-error", "--help"])
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code == 0
    assert not (tmp_path / ".config").exists()


def test_first_run_creates_flag(monkeypatch, tmp_path, capsys):
    from error_translator.cli import main

    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    monkeypatch.delenv("APPDATA", raising=False)
    monkeypatch.setattr(sys, "argv", ["explain-error", "KeyError: 'x'"])
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    main()
    assert (tmp_path / ".config" / "error-translator" / ".initialized").exists()


def test_unreadable_file_fails_cleanly(monkeypatch, tmp_path, capsys):
    import os

    from error_translator.cli import main

    err_log = tmp_path / "err.log"
    err_log.write_text("boom")
    os.chmod(err_log, 0o000)

    if os.access(err_log, os.R_OK):
        pytest.skip("System ignores file permissions (e.g. root)")

    monkeypatch.setattr(sys, "argv", ["explain-error", str(err_log)])
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)

    with pytest.raises(SystemExit) as excinfo:
        main()

    assert excinfo.value.code == 1
    captured = capsys.readouterr().out
    assert "File Error" in captured
    assert "explanation" not in captured
    assert "Explanation" not in captured


def test_xdg_config_home_respected(monkeypatch, tmp_path, capsys):
    from error_translator.cli import main

    xdg_path = tmp_path / "xdg"
    monkeypatch.setenv("XDG_CONFIG_HOME", str(xdg_path))
    monkeypatch.setattr(sys, "argv", ["explain-error", "KeyError: 'x'"])
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    main()
    assert (xdg_path / "error-translator" / ".initialized").exists()


def test_no_color_flag_produces_zero_ansi_escapes(capsys, monkeypatch):
    import re

    from error_translator.cli import main
    from error_translator.ui import console

    monkeypatch.setattr(
        sys, "argv", ["explain-error", "--no-color", "NameError: name 'x' is not defined"]
    )
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)

    main()

    captured = capsys.readouterr().out
    assert "Explanation" in captured
    assert "Suggested Fix" in captured
    assert "NameError" in captured
    # Must have zero ANSI escape sequences
    ansi_escapes = re.findall(r"\x1b\[[0-9;]*[a-zA-Z]", captured)
    assert not ansi_escapes
    assert console.no_color is True


def test_no_color_flag_after_positional_produces_zero_ansi_escapes(capsys, monkeypatch):
    import re

    from error_translator.cli import main
    from error_translator.ui import console

    monkeypatch.setattr(
        sys, "argv", ["explain-error", "NameError: name 'x' is not defined", "--no-color"]
    )
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)

    main()

    captured = capsys.readouterr().out
    assert "Explanation" in captured
    ansi_escapes = re.findall(r"\x1b\[[0-9;]*[a-zA-Z]", captured)
    assert not ansi_escapes
    assert console.no_color is True


def test_no_color_flag_piped_input_produces_zero_ansi_escapes(capsys, monkeypatch):
    import re

    from error_translator.cli import main

    monkeypatch.setattr(sys, "argv", ["explain-error", "--no-color"])
    monkeypatch.setattr(sys.stdin, "isatty", lambda: False)
    monkeypatch.setattr(
        sys.stdin, "read", lambda: "ValueError: invalid literal for int() with base 10: 'abc'"
    )

    main()

    captured = capsys.readouterr().out
    assert "ValueError" in captured
    ansi_escapes = re.findall(r"\x1b\[[0-9;]*[a-zA-Z]", captured)
    assert not ansi_escapes


def test_no_color_flag_help_screen(capsys, monkeypatch):
    import re

    from error_translator.cli import main

    monkeypatch.setattr(sys, "argv", ["explain-error", "--no-color", "--help"])
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)

    with pytest.raises(SystemExit) as excinfo:
        main()

    assert excinfo.value.code == 0
    captured = capsys.readouterr().out
    assert "Error Translator CLI Version" in captured
    ansi_escapes = re.findall(r"\x1b\[[0-9;]*[a-zA-Z]", captured)
    assert not ansi_escapes


def test_colored_output_preserved_when_no_color_flag_absent(capsys, monkeypatch):
    from error_translator.cli import main
    from error_translator.ui import console

    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.setattr(sys, "argv", ["explain-error", "NameError: name 'x' is not defined"])
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)

    main()

    assert console.no_color is False
