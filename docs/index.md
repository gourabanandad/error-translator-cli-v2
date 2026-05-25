# Error Translator

<div align="left">
  <a href="https://pypi.org/project/error-translator-cli-v2/"><img alt="PyPI Version" src="https://img.shields.io/pypi/v/error-translator-cli-v2.svg"></a>
  <a href="https://pypi.org/project/error-translator-cli-v2/"><img alt="Python 3.9+" src="https://img.shields.io/badge/python-3.9%2B-blue.svg"></a>
  <a href="https://github.com/gourabanandad/error-translator-cli-v2"><img alt="License" src="https://img.shields.io/github/license/gourabanandad/error-translator-cli-v2.svg"></a>
  <a href="https://github.com/gourabanandad/error-translator-cli-v2/actions/workflows/ci.yml"><img alt="Build Status" src="https://img.shields.io/github/actions/workflow/status/gourabanandad/error-translator-cli-v2/ci.yml?branch=master&label=build"></a>
</div>

<br>

![Error Translator CLI V2 demo banner](assets/images/banner.png)

<br>

Error Translator parses raw Python tracebacks and converts them into readable explanations with actionable fixes. It uses a deterministic, offline regex-matching engine that powers the CLI, Python API, auto-hook mode, and a FastAPI service with a bundled web UI.

For faster matching on supported platforms, the engine can also use an optional C extension (`fast_matcher`) and automatically falls back to pure Python when the extension is unavailable.

If this project is useful to you, support it with a GitHub star: https://github.com/gourabanandad/error-translator-cli-v2

Quick links:

- GitHub Repository: https://github.com/gourabanandad/error-translator-cli-v2
- PyPI Package: https://pypi.org/project/error-translator-cli-v2/
- Issues / Feature Requests: https://github.com/gourabanandad/error-translator-cli-v2/issues

## Demonstration

### Raw Traceback Input

```text
Traceback (most recent call last):
  File "app.py", line 14, in <module>
    total = "Users: " + 42
TypeError: can only concatenate str (not "int") to str
```

### Engine Translation Output

```markdown
### Detected Error
TypeError: can only concatenate str (not "int") to str

### Location
app.py (line 14)

### Code Context
total = "Users: " + 42

### Explanation
You are trying to add a string to an int, which Python cannot do.

### Suggested Fix
Convert the int to a string first using str() before concatenating.
```

The CLI renders this output with a polished Rich terminal layout (rounded panels, clear section titles, and syntax-highlighted code context).

## Core Design Principles

- **Privacy-First (Offline)**: Your stack traces and source code snippets never leave your machine. The regex and AST engines operate entirely locally.
- **Deterministic Matching**: Regex rules are compiled once and reused, so outputs stay consistent for the same error text.

## The Tooling Ecosystem

The core deterministic engine is exported transparently across four major interfaces:

1. **Automatic Integration Hook**: Catch uncaught exceptions locally in your scripts.
2. **Command-Line Interface (CLI)**: Translate active scripts, raw strings, or standard log streams automatically.
3. **Python Native API**: Directly integrate `error_translator.core.translate_error` into your internal system workflows.
4. **FastAPI Protocol**: Export translations externally over REST HTTP protocols via the `error_translator.api.server` module (`/translate`, `/health`, `/`).

## Developer Quickstart

To install Error Translator globally via your package manager:

```bash
pip install error-translator-cli-v2
```

We recommend navigating to the [**Contributing Guidelines**](CONTRIBUTING.md) to familiarize yourself with adding and extending deterministic rules using our automated Rule Builder tools.
