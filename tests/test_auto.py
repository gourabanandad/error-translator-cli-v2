import importlib
import sys

import error_translator.auto
from error_translator.auto import exception_hook


def get_exception_info():
    try:
        raise ValueError("boom")
    except ValueError:
        return sys.exc_info()


def test_original_traceback_preserved(capsys):
    exc_type, exc_value, tb = get_exception_info()
    exception_hook(exc_type, exc_value, tb)

    captured = capsys.readouterr()
    assert "Traceback" in captured.err
    assert "ValueError: boom" in captured.err

    # We just need to check if some UI elements from translation are in stdout
    # The original translation UI typically uses rich panels and rules.
    assert len(captured.out.strip()) > 0


def test_keyboardinterrupt_bypass(monkeypatch, capsys):
    called = []

    def mock_excepthook(*args, **kwargs):
        called.append(True)

    monkeypatch.setattr(sys, "__excepthook__", mock_excepthook)

    exception_hook(KeyboardInterrupt, KeyboardInterrupt(), None)

    assert len(called) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_systemexit_bypass(monkeypatch, capsys):
    called = []

    def mock_excepthook(*args, **kwargs):
        called.append(True)

    monkeypatch.setattr(sys, "__excepthook__", mock_excepthook)

    exception_hook(SystemExit, SystemExit(3), None)

    assert len(called) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_translation_failure_safety(monkeypatch, capsys):
    def mock_translate_error(*args, **kwargs):
        raise RuntimeError("Mock failure")

    monkeypatch.setattr(error_translator.auto, "translate_error", mock_translate_error)

    exc_type, exc_value, tb = get_exception_info()

    # Should not raise exception
    exception_hook(exc_type, exc_value, tb)

    captured = capsys.readouterr()
    assert "Traceback" in captured.err
    assert "ValueError: boom" in captured.err
    assert captured.out == ""


def test_regression_sys_excepthook_set():
    original_hook = sys.excepthook
    try:
        # Reset the hook
        sys.excepthook = sys.__excepthook__

        # Reloading the module triggers the module-level assignment
        importlib.reload(error_translator.auto)

        # It should now be set to our hook
        assert sys.excepthook == error_translator.auto.exception_hook
    finally:
        sys.excepthook = original_hook
