# Architectural Overview

Error Translator is built around one deterministic engine in `error_translator/core.py`, supported by modular components for parsing and rule management. The same engine powers the CLI, auto-hook mode, Python imports, and the FastAPI service.

## Core Translation Pipeline

Each translation request follows this sequence:

1. **Load and cache rule data** via `error_translator/rules.py` from `src/error_translator/rules.json`.
2. **Extract traceback location** (`file`, `line`) using `error_translator/parser.py`.
3. **Read source context line** using `linecache` in `parser.py` when file and line are available.
4. **Match the last error line** against pre-compiled regex patterns.
    - First attempt uses the optional C extension matcher (`error_translator.fast_matcher.match_loop`).
    - If the extension is unavailable, the engine falls back to the pure Python loop.
5. **Format output fields** (`explanation`, `fix`, and metadata).
6. **Optionally attach `ast_insight`** for registered error types.

If no pattern matches, the `default` rule is returned.

## Implementation Surfaces

The same engine is exposed through:

1. **CLI** (`error_translator/cli.py` acting as an entry point, orchestrating `runner.py` and `ui.py`):
    - `explain-error run script.py`
    - `explain-error "<error text>"`
    - `cat error.log | explain-error`
2. **Auto hook** (`error_translator/auto.py`): import once to override `sys.excepthook`.
3. **Python API**: `from error_translator.core import translate_error`.
4. **FastAPI service** (`error_translator/api/server.py`):
    - `POST /translate`
    - `GET /health`
    - `GET /` serves the bundled static UI (if present)

## AST Insight Notes

`ast_insight` is optional and routed via `AST_REGISTRY` in `error_translator/ast_handlers.py`.

Current handlers are lightweight placeholders and return suggestion strings for supported error classes (`NameError`, `AttributeError`, `ImportError`). They do not yet perform full file AST traversal.

## Runtime Contract

`translate_error(...)` always returns a dictionary with these fields:

- `explanation`
- `fix`

And typically includes:

- `matched_error`
- `file` (or `Unknown File`)
- `line` (or `Unknown Line`)
- `code` (empty string if unavailable)
- `ast_insight` (only when available)

## Extension Strategy

For most contributions, follow this order:

1. Add or improve a regex rule in `src/error_translator/rules.json`.
2. Add tests in `tests/test_core.py`.
3. Add/update handler behavior in `error_translator/ast_handlers.py` only when regex alone is insufficient.
4. Update `error_translator/core.py` only for shared pipeline behavior.

## Optional Native Acceleration

The optional C extension source lives at `src/error_translator/ext/fast_matcher.c` and is built via `setup_ext.py`.

When built successfully, core translation uses native code for the rule scan loop.
When not built, behavior remains identical because the Python loop is used automatically.
