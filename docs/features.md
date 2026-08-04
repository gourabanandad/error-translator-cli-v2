# Features & Integrations

Error Translator exposes its deterministic engine across multiple interfaces to fit naturally into any development workflow.

## 1. Command-Line Interface (CLI)

The CLI provides a polished Rich terminal layout with rounded panels, clear section titles, and syntax-highlighted code context.

Run a Python script and catch any unhandled exceptions:
```bash
explain-error run script.py
```

Provide an error string directly:
```bash
explain-error "NameError: name 'usr_count' is not defined"
```

Pipe system or Docker logs into the engine:
```bash
cat error.log | explain-error
```

Start an interactive session to translate multiple errors one after another without leaving the terminal:
```bash
explain-error interactive
```
Paste a single-line error, or a full multi-line traceback followed by a blank line (or `Ctrl+D`), to submit it. Type `exit`, `quit`, or press `Ctrl+C` to leave the session.

Emit structured JSON for scripting and automation:
```bash
explain-error --json "NameError: name 'x' is not defined"
```
*(The `--json` flag works with every input mode).*

Show an about screen with project metadata and usage examples:
```bash
explain-error --about
```

## 2. Automatic Import Hook

Catch and translate unhandled exceptions globally in your Python scripts by importing the auto module. This overrides `sys.excepthook` for graceful, translated crash reporting without modifying your core logic.

```python
import error_translator.auto

def main():
    # This TypeError will automatically trigger the error translator
    total = "Users: " + 42

if __name__ == "__main__":
    main()
```

## 3. Jupyter Notebook Integration

Error Translator integrates seamlessly with Jupyter notebooks and JupyterLab environments, allowing you to debug interactively without leaving your cell.

### Setup

Load the extension in any Jupyter notebook cell:

```python
%load_ext error_translator.jupyter
```
*(You can also use `%reload_ext` or `%unload_ext` as needed).*

### Interactive Usage

Once loaded, any unhandled exception in subsequent cells will automatically be translated and displayed in a user-friendly format.

```python
# Cell 1
%load_ext error_translator.jupyter

# Cell 2
data = {"name": "Alice", "age": 30}
print(data["email"])  # KeyError: 'email'
```

The notebook will display:
1. The **standard Jupyter traceback** (to preserve the exact location context).
2. The **Error Translator panel** containing the detected error, clear explanation, suggested fix, and AST-based insights (when applicable).

## 4. FastAPI Service

Expose the core engine over HTTP via the included FastAPI server for remote translation services.

Start the built-in HTTP server:
```bash
uvicorn error_translator.api.server:app --host 127.0.0.1 --port 8000 --reload
```

Submit a traceback payload via the exposed REST API:
```bash
curl -X POST http://127.0.0.1:8000/translate \
  -H "Content-Type: application/json" \
  -d "{\"traceback_setting\":\"Traceback (most recent call last):\\n  File 'app.py', line 14, in <module>\\n    total = 'Users: ' + 42\\nTypeError: can only concatenate str (not 'int') to str\"}"
```

Additional endpoints:
- `GET /health`: Returns service status.
- `GET /`: Serves the bundled web UI from `error_translator/api/static/index.html`.

## 5. Python Native API

Directly integrate the translation pipeline into your own internal workflows or custom tools.

```python
from error_translator.core import translate_error

raw_error = "NameError: name 'x' is not defined"
result = translate_error(raw_error)

print("Explanation:", result["explanation"])
print("Fix:", result["fix"])
```

## 6. Optional Native Acceleration

For maximum performance, the engine can utilize an optional C extension (`fast_matcher`). If available on the platform, it accelerates regex rule scanning. If unavailable, it automatically falls back to the pure Python loop with zero change in behavior.

*(For instructions on building the C extension, refer to the [Architecture & Internals](ARCHITECTURE.md#optional-native-acceleration) documentation).*
