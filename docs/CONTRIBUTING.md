# Contributing to Error Translator

Thank you for your interest in contributing to **Error Translator**! 

Whether you are improving existing translation advice, adding regex patterns for obscure standard library exceptions, enhancing AST lexical diagnostics, or fixing documentation, we welcome your contributions.

---

## 1. Local Development Setup

We recommend using [uv](https://github.com/astral-sh/uv) or standard Python virtual environments.

### Option A: Setup with `uv` (Recommended / Fastest)

```bash
# Clone the repository
git clone https://github.com/gourabanandad/error-translator-cli-v2.git
cd error-translator-cli-v2

# Create environment and install all dependencies (dev, server, jupyter, docs)
uv sync --all-extras

# Run the test suite
uv run pytest
```

### Option B: Setup with Standard `venv` and `pip`

```bash
# Clone repository
git clone https://github.com/gourabanandad/error-translator-cli-v2.git
cd error-translator-cli-v2

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate       # On Windows: .venv\Scripts\activate

# Install package in editable mode with all optional dependencies
pip install -e ".[dev,server,jupyter,docs]"

# Verify test suite
pytest
```

---

## 2. Project Directory Layout

```text
error-translator-cli-v2/
├── src/
│   └── error_translator/
│       ├── __init__.py          # Package exports (translate_error, load_ipython_extension)
│       ├── core.py              # Orchestrates parsing, dual-engine matching, and AST dispatch
│       ├── parser.py            # Extracts file paths, lines, and linecache source context
│       ├── rules.py             # Rule JSON caching and regex pre-compilation
│       ├── rules.json           # Declarative translation database (56+ rules)
│       ├── cli.py               # CLI entry point (explain-error) & interactive REPL
│       ├── runner.py            # Subprocess runner for `explain-error run`
│       ├── ui.py                # Rich terminal UI components and JSON formatting
│       ├── auto.py              # sys.excepthook auto-interceptor module
│       ├── jupyter.py           # IPython notebook extension (%load_ext)
│       ├── ast/
│       │   ├── ast_engine.py    # ScopedSymbolCollector & difflib typo matcher
│       │   └── ast_handlers.py  # AST_REGISTRY error strategy router
│       ├── api/
│       │   ├── server.py        # FastAPI REST API & endpoints
│       │   └── static/          # Static HTML/CSS assets for Web Dashboard
│       └── ext/
│           └── fast_matcher.c   # Optional CPython C extension for native speed
├── tests/                       # Complete pytest suite (50+ tests)
├── scripts/
│   ├── scraper.py               # Standard library error pattern scraper
│   └── builder.py               # Gemini-powered interactive rule generator
├── docs/                        # MkDocs Material documentation source files
├── pyproject.toml               # PEP 621 metadata, dependencies & tool configs
└── mkdocs.yml                   # MkDocs documentation site configuration
```

---

## 3. Authoring Translation Rules (`rules.json`)

Most contributions involve enhancing or adding error translation rules. All rules live declaratively in `src/error_translator/rules.json`.

### Schema Specification:

```json
{
  "pattern": "TypeError: can only concatenate str \\(not \"(.*)\"\\) to str",
  "explanation": "You are trying to add a string to a {0}, which Python cannot do.",
  "fix": "Convert the {0} to a string first using str() before concatenating."
}
```

### Key Guidelines for Rules:

1. **Regex Escaping**: Escape parentheses `\\(`, `\\)`, brackets `\\[`, `\\]`, and special regex characters.
2. **Dynamic Captures**: Use `(.*)` or specific groups like `'([^']*)'` to capture variable names, types, or function signatures from the exception string.
3. **Template Formatting**: Use `{0}`, `{1}`, `{2}` in `explanation` and `fix` to dynamically inject captured variables.
4. **Tone & Style**:
   - **Accessible**: Write in clear, encouraging, plain English without unnecessary academic jargon.
   - **Actionable**: Always provide a concrete code pattern or remedy in the `fix` field.

---

## 4. Rule Synthesis Tooling

If you have a Google Gemini API key, you can utilize the automated rule-building toolchain:

### Step 1: Scrape Reference Error Patterns
```bash
python scripts/scraper.py
```
*(Populates `scripts/scraped_errors_database.json` with standard library exceptions).*

### Step 2: Run the Interactive Rule Synthesizer
```bash
# Export your Gemini API key
export GEMINI_API_KEY="your_api_key_here"   # PowerShell: $env:GEMINI_API_KEY="key"

# Run interactive generator
python scripts/builder.py
```

The builder:
1. Identifies missing patterns in `rules.json`.
2. Queries the model for pattern matching rules and structured explanations.
3. Prompts you interactively in the terminal to **[A]ccept**, **[E]dit**, or **[S]kip** each proposed rule.

---

## 5. Adding AST Diagnostic Handlers

When regular expressions alone cannot provide deep enough insight (e.g., detecting misspelled local variables), add an AST handler:

1. Open `src/error_translator/ast/ast_handlers.py`.
2. Write a handler function accepting `(file_path: str, line_number: str, extracted_values: list)`:
   ```python
   def handle_my_error(file_path: str, line_number: str, extracted_values: list) -> str:
       target_word = extracted_values[0] if extracted_values else ""
       suggestion = get_ast_suggestions(file_path, line_number, target_word, "MyError")
       if suggestion:
           return f"Did you mean '{suggestion}'?"
       return "Review definition and spelling in the active scope."
   ```
3. Register your handler in `AST_REGISTRY`:
   ```python
   AST_REGISTRY["MyError"] = handle_my_error
   ```
4. Add comprehensive unit tests in `tests/test_ast.py`.

---

## 6. Code Style & Quality Standards

We enforce high code quality standards:

- **Linting & Formatting**: We use [Ruff](https://github.com/astral-sh/ruff).
  ```bash
  uv run ruff check .
  uv run ruff format --check .
  ```
- **Type Annotations**: Use modern Python 3.9+ type hints (`list[str]`, `dict[str, Any]`, `tuple[str, str]`).
- **Exception Handling**: Avoid bare `except Exception: pass`. Catch specific errors (`OSError`, `ValueError`, `SyntaxError`, `UnicodeDecodeError`).
- **Tests**: Ensure 100% of existing tests pass, and write new tests covering your additions.
  ```bash
  uv run pytest --cov=error_translator --cov-report=term-missing
  ```

---

## 7. Documentation Testing

To preview the documentation site locally:

```bash
uv run mkdocs serve
```
Open `http://127.0.0.1:8000` to inspect live changes with auto-reloading.

To verify a strict build without warnings:
```bash
uv run mkdocs build --strict
```

---

## 8. Pull Request Checklist

Before opening your pull request, please verify:

- [ ] All tests pass cleanly (`pytest`).
- [ ] New rules or features include corresponding test cases in `tests/`.
- [ ] Code passes Ruff linting (`ruff check .`).
- [ ] Documentation site builds without warnings (`mkdocs build --strict`).
- [ ] Your PR description includes a brief summary of changes along with a sample raw traceback and translated output.

Thank you for helping make Python debugging friendly and accessible for everyone!


