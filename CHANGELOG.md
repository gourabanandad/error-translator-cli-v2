# Changelog

All notable changes to **Error Translator CLI v2** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.1.0] - 2026-08-04

### Fixed

- **C extension is now optional.** `pip install error-translator-cli-v2` no longer hard-fails on machines without a C compiler. The pure-Python fallback in `core.py` handles matching when `fast_matcher` is unavailable.
- **`fast_matcher.c` exception leak.** The C extension's `match_loop` now calls `PyErr_Clear()` before `continue` when a regex `search` call raises, preventing a pending exception from leaking into the next iteration.
- **`print_execution_error` import restored in `cli.py`.** The interactive mode error-reporting path was broken when a previous ruff auto-fix dropped the import; it is now back and the corresponding test passes again.
- **Bare `except Exception: pass` blocks narrowed.** The catch-all handlers in `parser.py`, `ast_engine.py`, and `cli.py` now catch specific exception types (`OSError`, `ValueError`, `SyntaxError`, `UnicodeDecodeError`) instead of silently swallowing all errors.
- **`requirements.txt` no longer pins phantom dependencies.** `protobuf` and `beautifulsoup4` were listed but never imported; the file now installs the project via `-e .[dev,server,docs]` so there is a single source of truth for dependencies.
- **Dependabot is now functional.** The `package-ecosystem` was an empty string (invalid); it is now `"pip"` with `directory: "/"`, so Dependabot will actually run.

### Changed

- **`server.py` modernized.** Replaced the deprecated `from typing import List` with the builtin `list[str]`, supported on Python 3.9+.
- **`SECURITY.md` supported-versions table updated.** Now reflects 3.x (supported), 2.x (security fixes only), and <2.0.0 (unsupported) instead of the stale "1.x" entries.
- **`__init__.py` `__all__` sorted alphabetically** (`load_ipython_extension`, `translate_error`).
- **`runner.py` documents `check=False`.** The `subprocess.run` call now explicitly passes `check=False` with a comment explaining the manual `returncode` check, so future refactors don't accidentally drop it.
- **Ruff lint configuration added.** `pyproject.toml` now includes a `[tool.ruff]` section with `line-length = 100`, `target-version = "py39"`, and rule selection covering pycodestyle, pyflakes, isort, pyupgrade, flake8-bugbear, and more.

### Removed

- **`test.ipynb`** — scratch notebook removed from the repository root.
- **`.coverage`** — test coverage database no longer tracked.
- **`site/`** — built MkDocs output (4 MB) no longer tracked; `.gitignore` updated.
- **`dist_validate_deps/`** — stale wheel artifact no longer tracked; `.gitignore` updated.

## [3.0.6] - 2026-07-16

### Added

- Interactive REPL mode for `explain-error` — paste single-line errors or multi-line tracebacks, translate them one after another without re-invoking the CLI.
- `--json` flag support for interactive mode, emitting one JSON object per entry and skipping the decorative Rich panel.
- Multi-line paste handling in interactive mode: a pasted traceback is treated as a single translation, not one per line.
- Graceful handling of `Ctrl+C` (KeyboardInterrupt) and `Ctrl+D` (EOF) during interactive sessions.
- Interactive session survives engine bugs — if `translate_error()` raises, the error is reported via the execution-error panel and the session continues.
- `run` sub-command: `explain-error run script.py` executes a Python script and translates any traceback it produces.
- Piped stdin support: `cat error.log | explain-error` reads the traceback from stdin.
- First-run welcome banner shown once via `~/.config/error-translator/.initialized` flag.

### Changed

- `check_first_run` suppresses the welcome banner when output is piped or `--json` is used.
- Enhanced test suite with 43 tests covering core engine, CLI flags, interactive mode, AST scoping, and Jupyter extension.

## [3.0.5] - 2026-07-10

### Added

- FastAPI server with `/translate`, `/translate/batch`, `/health` endpoints and a static web UI dashboard.
- `asyncio.to_thread` batch translation for concurrent processing of multiple tracebacks.
- Pydantic request models (`ErrorRequest`, `BatchErrorRequest`) for API input validation.

### Changed

- `server.py` served at root (`GET /`) returns the interactive web UI `index.html`.
- Static files (CSS) mounted at `/static`.

## [3.0.4] - 2026-07-05

### Added

- Jupyter notebook integration via `%load_ext error_translator.jupyter`.
- `custom_exc` handler renders translated explanations as Markdown inside notebook cells.
- `load_ipython_extension` / `unload_ipython_extension` for Jupyter magic commands.
- Auto-hook module `error_translator.auto` — `import error_translator.auto` replaces `sys.excepthook` to intercept all unhandled exceptions.

### Changed

- `ScopedSymbolCollector` AST visitor now respects lexical scope using `lineno` / `end_lineno`, so suggestions only include symbols visible at the crash line.
- AST handlers registered via `AST_REGISTRY` dictionary for extensible error-type dispatch.

## [3.0.3] - 2026-06-28

### Added

- C extension `fast_matcher.c` for accelerated regex rule matching, bypassing the Python loop.
- `C_EXTENSION_AVAILABLE` flag in `core.py` with automatic fallback to the pure-Python matching loop.
- `lru_cache` on `load_rules()` and `compiled_rules()` to avoid re-reading `rules.json` on every call.

### Changed

- Pre-compiled regex patterns stored as `(compiled_pattern, rule_dict)` tuples for fast iteration.
- `cibuildwheel` matrix added to CI for building wheels on Ubuntu, Windows, and macOS.

## [3.0.2] - 2026-06-20

### Added

- `rules.json` expanded to 56 rules covering 26 Python error types.
- `difflib.get_close_matches` integration in `ast_engine.py` for "Did you mean?" suggestions on `NameError` and `AttributeError`.

### Changed

- `extract_location` regex now handles both single-quoted and double-quoted file paths in tracebacks.
- `extract_code_context` uses `linecache.getline` to read the exact crashing line of source code.

## [3.0.1] - 2026-06-15

### Added

- Rich-based terminal UI with multi-panel layout: Detected Error, Location, Code Context, Explanation, Suggested Fix, and AST Insight.
- `--about` flag showing project metadata, features, and quick-start examples.
- `--help` flag rendering a polished help dashboard instead of plain argparse output.
- `--version` flag.

### Changed

- `ui.py` extracted as a dedicated presentation module.
- `banner.py` added for ANSI-art install banner.

## [3.0.0] - 2026-06-10

### Added

- Complete rewrite of the error translation engine with a modular architecture: `parser.py`, `rules.py`, `core.py`, `cli.py`, `ui.py`.
- Rule-based regex matching engine driven by `rules.json`.
- `explain-error` CLI entry point via `pyproject.toml` `[project.scripts]`.
- PyPI package `error-translator-cli-v2` with MIT license.
- MkDocs Material documentation site with Architecture, Features, Examples, and Contributing pages.
- GitHub Actions CI/CD pipeline running tests on Python 3.9–3.12 and publishing wheels on release.
- `CODE_OF_CONDUCT.md`, `SECURITY.md`, `CONTRIBUTING.md`.
- Dependabot, FUNDING.yml, bug report issue template.

### Changed

- Migrated from a monolithic script to a `src/`-layout Python package.
- Switched from `setup.cfg` to `pyproject.toml` (PEP 621) for project metadata.
