"""
Command Line Interface (CLI) module for the Error Translator.

This module provides the terminal entry point (`explain-error`). It parses arguments,
handles standard input streams, and orchestrates the translation process.
"""
import argparse
import sys
from pathlib import Path

from .core import translate_error
from .runner import run_script
from .ui import VERSION, console, print_about, print_help, print_execution_error, print_result, print_result_json, print_version


def check_first_run(as_json: bool):
    """Check if this is the first time the CLI is being run by the user."""
    # Do not show welcome banner if outputting JSON or part of a pipeline
    if as_json or not sys.stdout.isatty():
        return

    config_dir = Path.home() / ".config" / "error-translator"
    flag_file = config_dir / ".initialized"

    if not flag_file.exists():
        try:
            config_dir.mkdir(parents=True, exist_ok=True)
            flag_file.touch()

            from .banner import print_install_banner
            print_install_banner()

            from rich.panel import Panel
            console.print(Panel(
                "[white]This tool automatically intercepts confusing Python errors and translates them into plain English.[/white]\n\n"
                "To get started, run:\n"
                "  [bold cyan]explain-error --help[/bold cyan]",
                title="[bold green]Welcome to Error Translator CLI V2![/bold green]",
                border_style="green",
                expand=False
            ))
            console.print()
        except OSError:
            # Can't write the ~/.config flag file (read-only home, etc.).
            # Not fatal — just skip the welcome banner.
            pass

def run_interactive_session(as_json: bool = False):
    """
    Start a REPL-style loop that repeatedly reads error text from the user
    and prints the translation, without having to re-invoke the CLI each time.

    Entry format:
        - A single line (e.g. a raw exception message) is submitted immediately
          on Enter.
        - A pasted multi-line traceback keeps being read until a blank line
          or EOF (Ctrl+D / Ctrl+Z) is received, then it is submitted as one block.
        - Typing "exit" or "quit" (case-insensitive), or pressing Ctrl+C / Ctrl+D
          at the prompt, ends the session.
    """
    emit = print_result_json if as_json else print_result

    if not as_json:
        from rich.panel import Panel
        console.print(Panel(
            "[white]Paste a Python error message or full traceback below.[/white]\n"
            "Press [bold]Enter[/bold] on a blank line (or [bold]Ctrl+D[/bold]) to submit it.\n"
            "Type [bold]exit[/bold] or [bold]quit[/bold] to leave, or press [bold]Ctrl+C[/bold] anytime.",
            title="[bold green]Interactive Mode[/bold green]",
            border_style="green",
            expand=False,
        ))

    while True:
        try:
            first_line = input("Enter error: ")
        except (EOFError, KeyboardInterrupt):
            console.print()
            break

        stripped = first_line.strip()
        if stripped.lower() in ("exit", "quit"):
            break
        if not stripped:
            # Ignore accidental blank submissions at the top of the prompt.
            continue

        # Keep collecting lines so a pasted multi-line traceback is treated
        # as a single error instead of one error per line.
        lines = [first_line]
        interrupted = False
        while True:
            try:
                line = input()
            except EOFError:
                break
            except KeyboardInterrupt:
                interrupted = True
                break
            if line.strip() == "":
                break
            lines.append(line)

        if interrupted:
            console.print()
            break

        error_text = "\n".join(lines)
        try:
            result = translate_error(error_text)
        except Exception as exc:
            # Never let a malformed paste or an engine bug kill the whole session.
            print_execution_error("interactive input", str(exc), as_json, "Translation Error")
        else:
            emit(result)

    if not as_json:
        console.print("[dim]Exiting interactive mode.[/dim]")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="explain-error",
        description="Error Translator — Turn cryptic Python tracebacks into clear, actionable advice.",
        epilog="""
Examples:
  explain-error run my_script.py
  explain-error "NameError: name 'usr_count' is not defined"
  cat error.log | explain-error
  explain-error interactive
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False
    )

    parser.add_argument("-a", "--about", action="store_true", help="Display information about the tool.")
    parser.add_argument("-v", "--version", action="store_true", help="Show the current version of the tool.")
    parser.add_argument("--json", action="store_true", dest="as_json", help="Output the translated error as a JSON object.")
    parser.add_argument("-h", "--help", action="store_true", help="Help user through documentation.")
    parser.add_argument("args", nargs="*", help="Positional arguments.")

    parsed_args = parser.parse_args()

    # Check for first run before executing commands
    check_first_run(getattr(parsed_args, "as_json", False))

    # Handle meta-flags
    if parsed_args.about:
        print_about()
        sys.exit(0)

    if parsed_args.version:
        print_version()
        sys.exit(0)

    if parsed_args.help:
        console.print(f"Error Translator CLI Version: [bold green]{VERSION}[/]")
        print_help()
        sys.exit(0)

    # Choose output strategy
    emit = print_result_json if parsed_args.as_json else print_result

    # Handle piped input (e.g. `cat error.log | explain-error`)
    if not sys.stdin.isatty():
        error_input = sys.stdin.read()
        if error_input.strip():
            emit(translate_error(error_input))
            return

    # Provide help if no arguments are passed
    if not parsed_args.args:
        print_help()
        sys.exit(1)

    # Detect the "run <script.py>" sub-command
    if parsed_args.args[0] == "run" and len(parsed_args.args) > 1:
        script_name = parsed_args.args[1]
        run_script(script_name, as_json=parsed_args.as_json)
    elif parsed_args.args[0] == "interactive":
        run_interactive_session(as_json=parsed_args.as_json)
    else:
        # Otherwise, treat the entire string of arguments as a raw traceback text
        if len(parsed_args.args) == 1:
            try:
                path = Path(parsed_args.args[0])
                if path.is_file():
                    if path.suffix == ".py":
                        run_script(str(path), as_json=parsed_args.as_json)
                        return
                    else:
                        error_input = path.read_text(encoding="utf-8")
                        if error_input.strip():
                            emit(translate_error(error_input))
                            return
            except Exception:
                pass

        error_input = " ".join(parsed_args.args)
        emit(translate_error(error_input))

if __name__ == "__main__":
    main()
