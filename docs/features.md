# Features & Integrations Guide

**Error Translator** provides a unified, deterministic translation engine accessible across multiple interfaces. Whether you are debugging locally in your terminal, writing code in Jupyter notebooks, building microservices with FastAPI, or automating CI/CD pipelines, Error Translator seamlessly integrates into your workflow.

---

## 1. Command-Line Interface (CLI)

The CLI tool (`explain-error`) is the primary entry point for terminal-based debugging. It provides a polished terminal interface using [Rich](https://github.com/Textualize/rich), with rounded panels, syntax highlighting, and distinct diagnostic sections.

```text
Usage: explain-error [OPTIONS] [COMMAND / ARGS]...
```

### CLI Command Modes

#### A. Execute a Target Python Script (`run`)
Run a target Python script directly through the translator. If the script succeeds, standard output is displayed normally. If an unhandled exception occurs, standard error is intercepted, parsed, and translated:

```bash
explain-error run path/to/script.py
```

*Shorthand syntax (direct `.py` file detection):*
```bash
explain-error path/to/script.py
```

#### B. Translate Raw Error Text
Pass raw exception text directly from your clipboard or terminal history:

```bash
explain-error "TypeError: can only concatenate str (not 'int') to str"
```

#### C. Pipe Logs via Standard Input (Stdin)
Stream traceback data from log files, CI runners, or Docker containers into the translator:

```bash
# Pipe from a file
cat crash.log | explain-error

# Pipe from Docker container logs
docker logs backend-container 2>&1 | explain-error

# Pipe from Python execution
python buggy_app.py 2>&1 | explain-error
```

#### D. Direct File Argument Detection
If you pass a `.log` or text file as an argument, Error Translator automatically reads and translates the exception contained inside:

```bash
explain-error server_error.log
```

---

### CLI Flags & Options

| Flag | Name | Description |
| :--- | :--- | :--- |
| `--json` | **JSON Mode** | Outputs translations as single-line JSON objects instead of Rich UI panels. |
| `-a`, `--about` | **About View** | Displays author information, environment details, Python version, and C-extension status. |
| `-v`, `--version` | **Version Info** | Prints version strings and native acceleration diagnostics. |
| `-h`, `--help` | **Help Dashboard** | Renders a styled help reference table and documentation links. |

#### Machine-Readable Automation (`--json`)

The `--json` flag works across all input modes. It formats the output as a clean, single-line JSON payload suitable for parsing with `jq`, log aggregators (e.g., Datadog, ELK), or automated test suites:

```bash
explain-error --json "KeyError: 'auth_token'"
```

**JSON Output Example:**
```json
{
  "explanation": "You tried to look up a key named 'auth_token' in a dictionary, but that key doesn't exist.",
  "fix": "Check for typos in the key name, or use the .get('auth_token') method to safely access dictionary values.",
  "ast_insight": null,
  "matched_error": "KeyError: 'auth_token'",
  "file": "Unknown File",
  "line": "Unknown Line",
  "code": ""
}
```

```bash
# Extract only the recommended fix using jq:
explain-error --json "KeyError: 'auth_token'" | jq -r .fix
```

---

## 2. Interactive REPL Mode

The interactive mode (`explain-error interactive`) provides a persistent debugging environment where you can paste multiple single-line errors or multi-line tracebacks without restarting the CLI.

```bash
explain-error interactive
```

```text
┌─ Interactive Mode ───────────────────────────────────────────────────────────┐
│ Paste a Python error message or full traceback below.                         │
│ Press Enter on a blank line (or Ctrl+D) to submit it.                        │
│ Type exit or quit to leave, or press Ctrl+C anytime.                         │
└──────────────────────────────────────────────────────────────────────────────┘
Enter error:
```

### Key Capabilities of Interactive Mode:

- **Smart Multi-Line Buffering**: Paste an entire 20-line traceback into the terminal. Error Translator buffers the lines and processes the entire traceback as a single error once an empty line or EOF is encountered.
- **Single-Line Immediate Execution**: Entering a single error line (e.g., `ZeroDivisionError: division by zero`) and pressing Enter immediately translates it.
- **Fault-Tolerant Engine**: If a malformed traceback or edge case occurs, the interactive session catches the exception, surfaces a warning panel, and keeps the REPL active.
- **JSON Support**: Start the REPL with `explain-error interactive --json` to receive structured JSON objects after each submission.
- **Navigation Shortcuts**: Type `exit`, `quit`, or press `Ctrl+C` / `Ctrl+D` to gracefully exit the session.

---

## 3. Automatic Import Hook (`error_translator.auto`)

For hands-free debugging during local development, import `error_translator.auto` at the top of your main entry point. This overrides Python's default exception handler (`sys.excepthook`).

When an unhandled exception occurs, Error Translator intercepts the crash, extracts the location and code context, and prints the translated Rich diagnostic card before the program terminates.

### Usage Example

```python
# main.py
import error_translator.auto


def process_data():
    items = ["apple", "banana"]
    print(items[5])  # IndexError


if __name__ == "__main__":
    process_data()
```

### Execution Output:

```text
$ python main.py

┌─ Detected Error ─────────────────────────────────────────────────────────────┐
│ IndexError: list index out of range                                          │
├─ Location ───────────────────────────────────────────────────────────────────┤
│ File: main.py  |  Line: 6                                                    │
├─ Code Context ───────────────────────────────────────────────────────────────┤
│ 6 │ print(items[5])                                                          │
├─ Explanation ────────────────────────────────────────────────────────────────┤
│ You are trying to access an item in a list at a position that doesn't exist. │
├─ Suggested Fix ──────────────────────────────────────────────────────────────┤
│ Check the length of your list using len(). Python lists are 0-indexed!       │
└──────────────────────────────────────────────────────────────────────────────┘
```

!!! tip "Production Best Practice"
    Import hooks are ideal for local development, debugging environments, and staging builds. For production services, consider combining the [Programmatic Python API](#6-programmatic-python-api) with your structured logging pipeline.

---

## 4. Jupyter Notebook & Lab Magic

Error Translator includes full support for interactive computing environments like Jupyter Notebooks, JupyterLab, Google Colab, and VS Code Notebooks via the `%load_ext` mechanism.

### Setup & Activation

In your first notebook cell, load the extension:

```python
%load_ext error_translator.jupyter
```

*To reload or unload:*
```python
%reload_ext error_translator.jupyter
%unload_ext error_translator.jupyter
```

### In-Cell Crash Interception

Once loaded, any unhandled exception in subsequent notebook cells automatically triggers the translator:

```python
# Cell 2
user_record = {"username": "gourab", "role": "admin"}
print(user_record["email_address"])
```

### Dual-View Display

When a cell crashes, the extension renders:
1. **Standard Jupyter Traceback**: Preserves original line numbers, cell references, and call hierarchies.
2. **Error Translator Markdown Card**: A formatted Markdown banner displaying the detected error, plain-English explanation, concrete fix, and AST suggestions.

---

## 5. FastAPI Microservice & Web Dashboard

For distributed systems, team-wide error triage, or web-based tools, Error Translator bundles a complete [FastAPI](https://fastapi.tiangolo.com/) service with single and batch translation endpoints and a built-in static dashboard.

### Starting the Server

Install server dependencies and launch Uvicorn:

```bash
pip install "error-translator-cli-v2[server]"
uvicorn error_translator.api.server:app --host 127.0.0.1 --port 8000 --reload
```

### Web UI Dashboard (`GET /`)
Navigate to `http://127.0.0.1:8000/` in any modern web browser to access the interactive web interface. Paste tracebacks directly into the UI to inspect formatted translations in real-time.

---

### REST API Endpoints

#### 1. Single Translation (`POST /translate`)

Translates a single Python traceback string.

- **Request URL**: `http://127.0.0.1:8000/translate`
- **Request Body**:
  ```json
  {
    "traceback_setting": "TypeError: unsupported operand type(s) for +: 'int' and 'str'"
  }
  ```

- **cURL Example**:
  ```bash
  curl -X POST http://127.0.0.1:8000/translate \
    -H "Content-Type: application/json" \
    -d '{"traceback_setting": "TypeError: unsupported operand type(s) for +: '\''int'\'' and '\''str'\''"}'
  ```

- **Response Payload**:
  ```json
  {
    "translate_error": {
      "explanation": "You are trying to add two incompatible types: a int and a str.",
      "fix": "Ensure both sides of the '+' are the same type (e.g., both numbers or both strings).",
      "ast_insight": null,
      "matched_error": "TypeError: unsupported operand type(s) for +: 'int' and 'str'",
      "file": "Unknown File",
      "line": "Unknown Line",
      "code": ""
    },
    "status": "ok"
  }
  ```

---

#### 2. Batch Translation (`POST /translate/batch`)

Translates multiple tracebacks in parallel using Python's `asyncio.to_thread` worker pool. Designed for processing high-throughput server error logs.

- **Request URL**: `http://127.0.0.1:8000/translate/batch`
- **Request Body**:
  ```json
  {
    "tracebacks": [
      "KeyError: 'session_id'",
      "ZeroDivisionError: division by zero",
      "IndexError: list index out of range"
    ]
  }
  ```

- **cURL Example**:
  ```bash
  curl -X POST http://127.0.0.1:8000/translate/batch \
    -H "Content-Type: application/json" \
    -d '{"tracebacks": ["KeyError: \"session_id\"", "ZeroDivisionError: division by zero"]}'
  ```

- **Response Payload**:
  ```json
  {
    "translations": [
      {
        "explanation": "You tried to look up a key named 'session_id' in a dictionary, but that key doesn't exist.",
        "fix": "Check for typos in the key name, or use the .get('session_id') method to safely access dictionary values.",
        "ast_insight": null,
        "matched_error": "KeyError: 'session_id'",
        "file": "Unknown File",
        "line": "Unknown Line",
        "code": ""
      },
      {
        "explanation": "You are trying to divide a number by zero, which is mathematically impossible.",
        "fix": "Add an if-statement before the division to check if the denominator is 0.",
        "ast_insight": null,
        "matched_error": "ZeroDivisionError: division by zero",
        "file": "Unknown File",
        "line": "Unknown Line",
        "code": ""
      }
    ],
    "status": "ok"
  }
  ```

---

#### 3. Health Check (`GET /health`)

Returns service health status for Kubernetes liveness/readiness probes or uptime monitors.

- **Request**: `GET http://127.0.0.1:8000/health`
- **Response**: `{"status": "ok"}`

---

## 6. Programmatic Python API

Embed translation capabilities directly into custom tools, developer scripts, or test frameworks using the `translate_error` function.

```python
from error_translator import translate_error

traceback_text = """
Traceback (most recent call last):
  File "data_pipeline.py", line 45, in load_config
    api_key = config["api_ky"]
KeyError: 'api_ky'
"""

result = translate_error(traceback_text)
```

### Result Dictionary Contract

The returned dictionary conforms to the following schema:

| Field | Type | Presence | Description |
| :--- | :--- | :--- | :--- |
| `explanation` | `str` | Always | Plain-English summary of what caused the exception. |
| `fix` | `str` | Always | Actionable steps or code patterns to resolve the issue. |
| `matched_error` | `str` | Always | The extracted final error line from the traceback. |
| `file` | `str` | Always | Source file path (`Unknown File` if not found in traceback). |
| `line` | `str` | Always | Offending line number (`Unknown Line` if not found). |
| `code` | `str` | Always | Code snippet from the source file (empty string if unavailable). |
| `ast_insight` | `str \| None` | Optional | Contextual AST suggestions (e.g. typos, missing imports). |

### Integration Recipes

=== "Custom Logging Handler"
    ```python
    import logging
    from error_translator import translate_error


    class HumanFriendlyErrorHandler(logging.Handler):
        def emit(self, record):
            if record.exc_text:
                translation = translate_error(record.exc_text)
                print(f"[ERROR EXPLAINED] {translation['explanation']}")
                print(f"[SUGGESTED FIX]   {translation['fix']}")


    logger = logging.getLogger("app")
    logger.addHandler(HumanFriendlyErrorHandler())
    ```

=== "Pytest Failure Hook (`conftest.py`)"
    ```python
    import pytest
    from error_translator import translate_error


    def pytest_exception_interact(node, call, report):
        if report.failed and call.excinfo:
            tb_str = str(call.excinfo.getrepr())
            translation = translate_error(tb_str)
            print("\n" + "=" * 60)
            print(f"FAILED TEST: {node.name}")
            print(f"EXPLANATION: {translation['explanation']}")
            print(f"FIX:         {translation['fix']}")
            print("=" * 60)
    ```

---

## 7. AST-Powered Scoped Diagnostic Engine

Beyond simple regular expressions, Error Translator includes an **Abstract Syntax Tree (AST) inspection engine** located in `error_translator/ast/ast_engine.py`.

### How It Works:

1. **Source File Parsing**: When a traceback includes a valid source file path and line number, the file is parsed into a Python AST.
2. **Lexical Scope Boundary Detection (`ScopedSymbolCollector`)**: The visitor inspects AST nodes while tracking `lineno` and `end_lineno` boundaries. It only descends into function or class bodies if the crash line occurred *inside* that specific block. This prevents variables from unrelated scopes from being suggested.
3. **Symbol Harvesting**: Collects variables, function definitions, class names, imports, and accessed attributes in the active scope.
4. **Fuzzy Typo Resolution**: Uses `difflib.get_close_matches` with a `0.6` similarity threshold to find the most likely intended symbol.

```python
# Example: If a user types 'usr_cnt' inside a function where 'user_count' is defined:
# AST insight output:
"Did you mean 'user_count'? There appears to be a typo."
```

### Supported AST Handlers:

- **`NameError`**: Detects misspelled variables and functions within the current lexical scope.
- **`AttributeError`**: Identifies misspelled methods or object attributes.
- **`ImportError` / `ModuleNotFoundError`**: Suggests correctly-spelled classes or functions from available imports.

---

## 8. Dual-Engine Performance & C Extension

To maximize throughput when processing large volumes of stack traces, Error Translator utilizes a **hybrid dual-engine architecture**:

```text
┌─────────────────────────────────────────────────────────────┐
│                   Error Translation Engine                  │
├──────────────────────────────┬──────────────────────────────┤
│  Primary: Native C Extension │  Fallback: Pure Python Loop  │
│      (fast_matcher.c)        │         (re.search)          │
│   • Direct PyObject matching │   • Pre-compiled patterns    │
│   • Sub-millisecond scan     │   • 100% platform compatible │
│   • Automatic memory safety  │   • Zero external dependencies│
└──────────────────────────────┴──────────────────────────────┘
```

- **Compiled C Speed**: When compiled via CPython (`setup.py`), the `fast_matcher` module scans rule tables natively in C without Python bytecode dispatch overhead.
- **Seamless Portability**: If a C compiler is unavailable during `pip install`, the installation succeeds without errors, and the engine automatically falls back to pre-compiled regex objects in Python with **100% identical outputs**.
