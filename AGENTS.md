# AGENTS.md — Development Guidelines for AI & Coding Agents

This document defines the architectural conventions, testing requirements, workflow commands, and code quality standards for AI assistants and automated coding agents contributing to **Error Translator CLI v2**.

---

## 1. Project Overview

**Error Translator** is a local-first, deterministic Python traceback analyzer and exception diagnostics engine. It intercepts Python error strings, inspects source files via `linecache`, performs scoped Abstract Syntax Tree (AST) lexical analysis for typo detection, and produces structured diagnostic panels with actionable remediation advice.

### Key Capabilities
- **Deterministic Regex Rule Engine**: 56+ rules covering 26+ Python standard exception classes (`rules.json`).
- **Dual Matching Engine**: Native C extension (`fast_matcher.c`) with transparent pure-Python fallback (`re.search`).
- **Lexical-Scope AST Intelligence**: Scoped symbol harvesting (`ScopedSymbolCollector`) bounded by function/class lines to prevent false-positive suggestions.
- **Multiple Integration Surfaces**:
  - CLI: `explain-error` (supports `run`, `interactive`, raw strings, and stdin piping).
  - Global Exception Hook: `error_translator.auto` (`sys.excepthook`).
  - Jupyter / IPython Extension: `%load_ext error_translator.jupyter`.
  - Programmatic API: `error_translator.core.translate_error`.
  - REST Microservice: FastAPI application in `error_translator.api.server`.

---

## 2. Directory Layout & Component Responsibilities

```text
error-translator-cli-v2/
├── src/
│   └── error_translator/
│       ├── __init__.py          # Public API exports (translate_error, load_ipython_extension)
│       ├── core.py              # Orchestrates parser, dual-engine matching, and AST dispatch
│       ├── parser.py            # Extracts file paths, line numbers, and linecache source code
│       ├── rules.py             # JSON loading, lru_cache, and regex pre-compilation
│       ├── rules.json           # Declarative translation database (regex patterns, templates)
│       ├── cli.py               # CLI entry point (explain-error) & interactive REPL loop
│       ├── runner.py            # Subprocess runner for `explain-error run <script.py>`
│       ├── ui.py                # Rich terminal UI components and JSON formatting
│       ├── auto.py              # Global sys.excepthook auto-interceptor module
│       ├── jupyter.py           # IPython notebook extension (%load_ext)
│       ├── ast/
│       │   ├── ast_engine.py    # ScopedSymbolCollector & difflib fuzzy typo matcher
│       │   └── ast_handlers.py  # AST_REGISTRY error strategy router
│       ├── api/
│       │   ├── server.py        # FastAPI REST API endpoints (/translate, /translate/batch)
│       │   └── static/          # Static HTML/CSS assets for Web Dashboard
│       └── ext/
│           └── fast_matcher.c   # Optional CPython C extension for native regex acceleration
├── tests/                       # Complete pytest suite (50+ tests)
│   ├── conftest.py              # Pytest fixtures
│   ├── test_ast.py              # AST scoping and symbol collection tests
│   ├── test_cli.py              # CLI flags, argument routing, and runner tests
│   ├── test_core.py             # Core translation engine and regex rule tests
│   ├── test_jupyter.py          # Jupyter extension tests
│   └── test_server.py           # FastAPI endpoint tests
├── scripts/
│   ├── scraper.py               # Standard library error pattern scraper
│   ├── builder.py               # Rule synthesis assistant
│   └── scraped_errors_database.json
├── docs/                        # MkDocs Material documentation source files
├── pyproject.toml               # PEP 621 metadata, dependencies & tool configs
├── setup.py                     # Optional C extension build configuration
└── mkdocs.yml                   # MkDocs documentation site configuration
```

---

## 3. Tooling & Development Workflow

### Dependency Management
The project uses `uv` as the primary package and project manager, with compatibility for standard `pip` and `venv`.

```bash
# Install all extras (dev, server, jupyter, docs)
uv sync --all-extras

# Or with pip
pip install -e ".[dev,server,jupyter,docs]"
```

### Running Tests
All tests are located in `tests/` and run using `pytest` with code coverage tracking.

```bash
# Run complete test suite
uv run pytest

# Run specific test file
uv run pytest tests/test_core.py

# Run with verbose output
uv run pytest -v
```

### Code Style & Linting
Code quality is enforced via [Ruff](https://github.com/astral-sh/ruff) configured in `pyproject.toml`.

```bash
# Check for lint violations
uv run ruff check .

# Automatically apply safe and unsafe fixes
uv run ruff check --fix --unsafe-fixes .

# Check formatting
uv run ruff format --check .

# Apply code formatting
uv run ruff format .
```

### Documentation Site
Documentation is built using [MkDocs Material](https://squidfunk.github.io/mkdocs-material/).

```bash
# Local development server with live reload
uv run mkdocs serve

# Verify strict build without warnings
uv run mkdocs build --strict
```

---

## 4. Architectural Rules for Agents

When implementing changes or adding features, agents MUST adhere to these design principles:

### A. Tone & Presentation
- **No Emojis**: Do NOT introduce emojis into source code, CLI output, error cards, docstrings, or documentation.
- **Professional Language**: Avoid marketing hype, buzzwords (e.g., "blazing-fast", "crystal-clear", "magical"), and overly verbose explanations. Maintain a direct, technical tone.
- **Structured Output**: Follow established Rich panel styling in `ui.py` for terminal output and clean Markdown for Jupyter.

### B. Exception Hygiene
- **Never Silently Swallow Exceptions**: Avoid bare `except Exception: pass`.
- **Catch Narrow Exceptions**: Explicitly handle expected failure modes (`OSError`, `ValueError`, `SyntaxError`, `UnicodeDecodeError`).
- **Fail Gracefully**: If optional subsystems fail (e.g., C extension import, AST parsing of malformed syntax), fallback to reliable defaults without crashing the parent process.

### C. Data Contracts & Schema Compatibility
- The `translate_error()` return contract in `error_translator.core` MUST always return a dictionary with the following keys:
  - `explanation` (`str`): Summary of the error cause.
  - `fix` (`str`): Actionable remediation instructions.
  - `ast_insight` (`str | None`): Scope-aware symbol suggestion or `None`.
  - `matched_error` (`str`): Exact error line extracted from traceback.
  - `file` (`str`): File path or `"Unknown File"`.
  - `line` (`str`): Line number or `"Unknown Line"`.
  - `code` (`str`): Source line extracted via `linecache` or `""`.

### D. Adding Translation Rules
1. Add new rule objects to `src/error_translator/rules.json`:
   ```json
   {
     "pattern": "TypeError: (.*) object is not callable",
     "explanation": "You tried to call a {0} as if it were a function.",
     "fix": "Check if you accidentally used parentheses '()' after a variable name instead of brackets '[]'."
   }
   ```
2. Add corresponding test cases in `tests/test_core.py`.
3. Verify that capture group indexing (`{0}`, `{1}`) matches regex group positions.

### E. Adding AST Handlers
1. Define handler functions in `src/error_translator/ast/ast_handlers.py` with the signature:
   `def handle_<error_name>(file_path: str, line_number: str, extracted_values: list) -> str | None`
2. Register the handler in `AST_REGISTRY`.
3. Add unit tests in `tests/test_ast.py`.

---

## 5. Pre-Commit Checklist for Agents

Before completing any task or opening a PR:

1. [ ] `uv run pytest` passes 100% of tests.
2. [ ] `uv run ruff check .` reports no errors or warnings.
3. [ ] `uv run ruff format --check .` confirms consistent formatting.
4. [ ] `uv run mkdocs build --strict` builds cleanly with no warnings.
5. [ ] No emojis or AI buzzwords were introduced.
