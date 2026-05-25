"""
Command Line Interface (CLI) module for the Error Translator.

This module provides the terminal entry point (`explain-error`). It parses arguments,
handles standard input streams, and orchestrates the translation process.
"""
import argparse
import sys
from pathlib import Path
from .core import translate_error
from .ui import print_about, print_help, print_result, print_result_json, VERSION, console
from .runner import run_script

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
        except Exception:
            pass

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
        console.print(f"Error Translator CLI Version: [bold green]{VERSION}[/]")
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
    else:
        # Otherwise, treat the entire string of arguments as a raw traceback text
        error_input = " ".join(parsed_args.args)
        emit(translate_error(error_input))

if __name__ == "__main__":
    main()