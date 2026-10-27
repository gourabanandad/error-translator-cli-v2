import os
import sys
import tempfile
from types import ModuleType

import pytest

from error_translator.ast.ast_engine import get_ast_suggestions
from error_translator.ast.ast_handlers import handle_import_error
from error_translator.ast.import_suggestions import get_import_suggestion
from error_translator.core import translate_error

# Use distinctly different variable names so difflib doesn't accidentally match them!
MOCK_CODE = """
global_var = 100

def func_a():
    apple_qty = 1
    # Crash happens here (line 6)
    print(appl_qty)

def func_b():
    banana_num = 2
    # Crash happens here (line 11)
    print(banan_num)
"""


@pytest.fixture
def mock_file():
    fd, path = tempfile.mkstemp(suffix=".py")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(MOCK_CODE)
    yield path
    os.remove(path)


def test_ast_scoping_func_a(mock_file):
    # Simulate a NameError crash on line 6 (inside func_a) looking for 'appl_qty'
    suggestion = get_ast_suggestions(mock_file, "6", "appl_qty", "NameError")
    assert suggestion == "apple_qty"

    # Try to access func_b's variable from func_a
    suggestion_bad = get_ast_suggestions(mock_file, "6", "banan_num", "NameError")
    assert suggestion_bad is None  # Should be completely blocked


def test_ast_scoping_func_b(mock_file):
    # Simulate a NameError crash on line 11 (inside func_b)
    suggestion = get_ast_suggestions(mock_file, "11", "banan_num", "NameError")
    assert suggestion == "banana_num"


MOCK_ASYNC_CODE = """
async def fetch_data():
    user_count = 10
    # line 4
    print(usr_count)
    return user_count

# line 8
print(usr_count)

# line 11
print(fetch_dta)
"""


@pytest.fixture
def mock_async_file():
    fd, path = tempfile.mkstemp(suffix=".py")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(MOCK_ASYNC_CODE)
    yield path
    os.remove(path)


def test_ast_scoping_async_leak(mock_async_file):
    # Leak regression: inside an async function 'user_count' is defined.
    # At module level (line 8), a crash for 'usr_count' should NOT suggest 'user_count'.
    suggestion = get_ast_suggestions(mock_async_file, "8", "usr_count", "NameError")
    assert suggestion is None


def test_ast_scoping_async_inside(mock_async_file):
    # Inside-async suggestion: inside async function, 'usr_count' should suggest 'user_count'.
    suggestion = get_ast_suggestions(mock_async_file, "4", "usr_count", "NameError")
    assert suggestion == "user_count"


def test_ast_scoping_async_name(mock_async_file):
    # Async function name in enclosing scope: module-level typo 'fetch_dta' -> 'fetch_data'
    suggestion = get_ast_suggestions(mock_async_file, "11", "fetch_dta", "NameError")
    assert suggestion == "fetch_data"


@pytest.mark.parametrize("misspelling", ["squar_root", "squrt"])
def test_import_error_math_uses_target_module(tmp_path, misspelling):
    crash = tmp_path / "crash.py"
    crash.write_text(f"{misspelling} = 1\nfrom math import {misspelling}\n", encoding="utf-8")
    result = translate_error(
        f'Traceback (most recent call last):\n  File "{crash}", line 2, in <module>\n'
        f"ImportError: cannot import name '{misspelling}' from 'math'"
    )
    assert result["ast_insight"] == "Did you mean to import 'sqrt' instead?"


def test_import_error_local_module_is_not_executed(tmp_path, monkeypatch):
    crash = tmp_path / "crash.py"
    crash.write_text("misspelled_export = 1\n", encoding="utf-8")
    sentinel = tmp_path / "executed.txt"
    target = tmp_path / "local_target.py"
    target.write_text(
        f"open({str(sentinel)!r}, 'w').write('executed')\n"
        "def correct_export():\n    hidden_local = 1\n"
        "class PublicClass:\n    hidden_attribute = 1\n"
        "async def fetch_data():\n    pass\n"
        "result_count = 1\n"
        "import xml.etree\n"
        "import os.path as filesystem\n"
        "from math import sqrt as root_function\n",
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))
    for bad_name, expected in [
        ("correct_expor", "correct_export"),
        ("PublicClas", "PublicClass"),
        ("fetch_dat", "fetch_data"),
        ("result_coun", "result_count"),
        ("xm", "xml"),
        ("filesyste", "filesystem"),
        ("root_functio", "root_function"),
    ]:
        assert get_import_suggestion(str(crash), "local_target", bad_name) == expected
    # Exact module bindings should not be suggested as typos; nested names are not exports.
    for name in ["xml", "filesystem", "root_function"]:
        assert get_import_suggestion(str(crash), "local_target", name) is None
    assert get_import_suggestion(str(crash), "local_target", "hidden_loca") is None
    assert not sentinel.exists()
    assert "local_target" not in sys.modules


def test_import_error_finds_dotted_package_from_nested_crash(tmp_path):
    package = tmp_path / "sample_package"
    package.mkdir()
    (package / "__init__.py").write_text("package_value = 1\n", encoding="utf-8")
    (package / "exports.py").write_text("def transform_data():\n    pass\n", encoding="utf-8")
    crash = package / "crash.py"
    crash.write_text("transform_dat = 1\n", encoding="utf-8")
    assert (
        get_import_suggestion(str(crash), "sample_package.exports", "transform_dat")
        == "transform_data"
    )
    assert get_import_suggestion(str(crash), "sample_package", "package_valu") == "package_value"


def test_import_error_local_module_takes_precedence_over_loaded_module(tmp_path, monkeypatch):
    crash = tmp_path / "crash.py"
    crash.write_text("pass\n", encoding="utf-8")
    loaded = ModuleType("shadowed_target")
    loaded.__dict__["calculate_remote"] = None
    monkeypatch.setitem(sys.modules, "shadowed_target", loaded)
    (tmp_path / "shadowed_target.py").write_text("calculate_local = 1\n", encoding="utf-8")
    assert (
        get_import_suggestion(str(crash), "shadowed_target", "calculate_loca") == "calculate_local"
    )
    (tmp_path / "math.py").write_text("def square_root():\n    pass\n", encoding="utf-8")
    assert get_import_suggestion(str(crash), "math", "squar_root") == "square_root"


def test_import_error_loaded_module_does_not_call_hooks(tmp_path, monkeypatch):
    module = ModuleType("loaded_target")

    def fail_hook(*args):
        pytest.fail("Module hooks must not be called")

    module.__dict__.update(
        {"export_value": None, "__getattr__": fail_hook, "__dir__": fail_hook, 123: None}
    )
    monkeypatch.setitem(sys.modules, "loaded_target", module)
    assert (
        get_import_suggestion(str(tmp_path / "missing.py"), "loaded_target", "export_valu")
        == "export_value"
    )


def test_import_error_skips_module_subclasses_and_proxies(tmp_path, monkeypatch):
    class HookedModule(ModuleType):
        def __getattribute__(self, name):
            pytest.fail("Module subclass attributes must not be accessed")

    class Proxy:
        def __getattribute__(self, name):
            pytest.fail("Proxy attributes must not be accessed")

    for module in [HookedModule("unsafe_target"), Proxy()]:
        monkeypatch.setitem(sys.modules, "unsafe_target", module)
        assert (
            get_import_suggestion(str(tmp_path / "missing.py"), "unsafe_target", "export") is None
        )


@pytest.mark.parametrize(
    "extracted_values",
    [
        None,
        [],
        ["squrt"],
        "squrt",
        [None, "math"],
        ["squrt", None],
        ["", "math"],
        ["squrt", ""],
        ["squrt", "../math"],
        ["squrt", "math..other"],
        ["squrt", "math/other"],
    ],
)
def test_import_error_malformed_arguments_fall_back(tmp_path, extracted_values):
    assert handle_import_error(str(tmp_path / "missing.py"), "1", extracted_values) == (
        "Verify that the class/function exists in the target module and is spelled correctly."
    )


@pytest.mark.parametrize("contents", [b"def broken(:\n", b"\xff\xfe\x00"])
def test_import_error_unreadable_local_target_does_not_use_loaded_names(tmp_path, contents):
    crash = tmp_path / "crash.py"
    crash.write_text("pass\n", encoding="utf-8")
    (tmp_path / "math.py").write_bytes(contents)
    assert get_import_suggestion(str(crash), "math", "squrt") is None


@pytest.mark.parametrize("name", ["sqrt", "zzzzzzzzzzzz", "not-a-name"])
def test_import_error_no_match_or_existing_name_falls_back(tmp_path, name):
    assert get_import_suggestion(str(tmp_path / "missing.py"), "math", name) is None


def test_import_error_unknown_module_is_not_imported(tmp_path, monkeypatch):
    target = tmp_path / "unloaded_target.py"
    target.write_text("raise RuntimeError('must not execute')\n", encoding="utf-8")
    monkeypatch.syspath_prepend(str(tmp_path))
    # An importable module outside the crash file's roots must remain unloaded.
    assert get_import_suggestion("Unknown File", "unloaded_target", "export") is None
    assert "unloaded_target" not in sys.modules
