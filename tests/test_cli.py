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
    from error_translator.cli import main
    import json

    monkeypatch.setattr(sys, "argv", ["explain-error", "--json", "NameError: name 'foo' is not defined"])
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
    script.write_text(
        "print('hello from script')\n"
        "print(undefined_variable)\n"
    )

    monkeypatch.setattr(sys, "argv", ["explain-error", "run", str(script)])
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)

    main()

    captured = capsys.readouterr().out
    assert "hello from script" in captured  # the script's own stdout is preserved
    assert "undefined_variable" in captured  # the NameError got translated


def test_run_subcommand_missing_script_reports_detected_error(capsys, monkeypatch):
    """`explain-error run nonexistent.py` must not crash the CLI; it should
    surface a translated/handled error instead."""
    from error_translator.cli import main

    monkeypatch.setattr(sys, "argv", ["explain-error", "run", "definitely_missing_script.py"])
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)

    main()  # must not raise

    captured = capsys.readouterr().out
    assert "No such file" in captured or "can't open file" in captured or "Execution Error" in captured
