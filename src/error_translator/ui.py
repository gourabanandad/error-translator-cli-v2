"""
UI Module for the Error Translator CLI.
Provides terminal formatting, layout, and presentation logic using Rich.
"""
import json
from importlib.metadata import version as get_version, PackageNotFoundError
from rich.console import Console, Group
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text
from rich.table import Table
from rich import box
from rich.align import Align

# Attempt to load the application version
try:
    VERSION = get_version("error-translator-cli-v2")
except PackageNotFoundError:
    VERSION = "unknown (not installed via pip)"

# Initialize the global rich console for styled terminal output
console = Console()

def _print_title_banner():
    """Prints a simple text title banner for the CLI."""
    simple_title = Text("Error Translator CLI V2", style="bold bright_magenta")
    
    banner_panel = Panel(
        Align.center(simple_title),
        box=box.DOUBLE_EDGE,
        border_style="bright_magenta",
        title="[bold yellow]⚡ Fatal to Fabulous ⚡[/bold yellow]", 
        subtitle="[italic bold bright_white] ⇆ Offline Python Traceback Explainer V2 ⇆ [/italic bold bright_white]",
        padding=(1, 4)
    )

    console.print(banner_panel)
    console.print()

def print_about():
    """Prints a polished 'about' view using rich components, showcasing features and metadata."""
    _print_title_banner()

    meta = Table.grid(padding=(0, 1))
    meta.add_column(style="bold white", justify="right")
    meta.add_column(style="green")
    meta.add_row("Version", VERSION)
    meta.add_row("Author", "Gourabananda Datta")
    meta.add_row("Repository", "https://github.com/gourabanandad/error-translator-cli-v2")
    console.print(Panel(meta, title="[bold cyan]Project[/]", border_style="cyan", expand=False))

    features = Text()
    features.append("• Offline and fast translation\n", style="white")
    features.append("• Human-readable explanations\n", style="white")
    features.append("• Actionable fix suggestions\n", style="white")
    features.append("• Optional AST-level insight", style="white")
    console.print(Panel(features, title="[bold green]Features[/]", border_style="green", expand=False))

    examples = Text()
    examples.append("explain-error run your_script.py\n", style="bold cyan")
    examples.append("explain-error \"TypeError: ...\"\n", style="bold cyan")
    examples.append("cat error.log | explain-error", style="bold cyan")
    console.print(Panel(examples, title="[bold yellow]Quick Start[/]", border_style="yellow", expand=False))

def print_help():
    """Print polished 'help' view using rich components, showcasing features, usage, and documentation."""
    _print_title_banner()
    
    cli_table = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan")
    cli_table.add_column("Command / Usage", style="bold yellow", width=42)
    cli_table.add_column("Description", style="white")
    cli_table.add_row("explain-error run <script_path>", "Execute a Python script, intercept, and translate tracebacks.")
    cli_table.add_row("explain-error \"<traceback_text>\"", "Translate a raw traceback string passed as an argument.")
    cli_table.add_row("cat error.log | explain-error", "Translate tracebacks piped via standard input (stdin).")
    
    console.print(Panel(cli_table, title="[bold cyan]1. Command Line Interface (CLI) Usage[/]", border_style="cyan", expand=False))

    python_info = Text()
    python_info.append("A) Global Exception Hook\n", style="bold magenta")
    python_info.append("Import this module at the top of your script to automatically capture and translate all unhandled exceptions:\n", style="dim white")
    python_info.append("    import error_translator.auto\n\n", style="bold white")
    python_info.append("B) Programmatic Translation API\n", style="bold magenta")
    python_info.append("Translate exception string programmatically within your codebase:\n", style="dim white")
    python_info.append("    from error_translator import translate_error\n", style="bold white")
    python_info.append("    result = translate_error(traceback_text)", style="bold white")
    
    console.print(Panel(python_info, title="[bold magenta]2. Python Library Integration[/]", border_style="magenta", expand=False))

    fastapi_info = Text()
    fastapi_info.append("Run the local HTTP REST API and interactive Web UI dashboard:\n", style="dim white")
    fastapi_info.append("    uvicorn error_translator.api.server:app --host 127.0.0.1 --port 8000\n\n", style="bold yellow")
    fastapi_info.append("Exposes:\n", style="dim white")
    fastapi_info.append("  • GET  /        -> Interactive Web UI dashboard\n", style="white")
    fastapi_info.append("  • POST /translate -> REST endpoint for remote traceback translation", style="white")
    
    console.print(Panel(fastapi_info, title="[bold yellow]3. Local Web UI & API Service[/]", border_style="yellow", expand=False))

    options_table = Table(box=box.SIMPLE, show_header=True, header_style="bold green")
    options_table.add_column("Flag", style="bold green", width=25)
    options_table.add_column("Description", style="white")
    options_table.add_row("-h, --help", "Display this detailed help documentation dashboard.")
    options_table.add_row("-a, --about", "Show developer, version, and project details.")
    options_table.add_row("-v, --version", "Show the current version.")
    options_table.add_row("--json", "Output response in structured JSON format.")
    
    console.print(Panel(options_table, title="[bold green]4. CLI Options & Flags[/]", border_style="green", expand=False))

    links_table = Table.grid(padding=(0, 2))
    links_table.add_column(style="bold white", justify="right")
    links_table.add_column(style="cyan")
    links_table.add_row("Official Docs", "https://gourabanandad.github.io/error-translator-cli-v2/")
    links_table.add_row("GitHub Repository", "https://github.com/gourabanandad/error-translator-cli-v2")
    links_table.add_row("PyPI Package", "https://pypi.org/project/error-translator-cli-v2/")
    
    console.print(Panel(links_table, title="[bold blue]5. Documentation & Resources[/]", border_style="blue", expand=False))

def print_result(result: dict):
    """Print the translated error output in a polished, professional, multi-panel layout."""
    console.print()

    if result.get("error") and not result.get("matched_error"):
        message = result.get("message", "An unexpected error occurred.")
        console.print(Panel(f"[bold red]{message}[/]", title="[bold red]Error[/]", border_style="red", box=box.ROUNDED, expand=False))
        return

    error_title = result.get("matched_error", "Unknown Error")
    console.print(Panel(f"[bold white]{error_title}[/]", title="[bold red]Detected Error[/]", border_style="red", box=box.ROUNDED, expand=False))

    file_name = result.get("file")
    line_no = result.get("line", "?")
    if file_name and file_name != "Unknown File":
        console.print(Panel(f"[bold yellow]File:[/] [bold white]{file_name}\n[bold yellow]Line:[/] [bold white]{line_no}", title="[bold yellow]Location[/]", border_style="yellow", box=box.ROUNDED, expand=False))

    if result.get("code"):
        try:
            start_line = int(line_no)
        except (TypeError, ValueError):
            start_line = 1

        syntax = Syntax(result["code"], "python", theme="monokai", line_numbers=True, start_line=start_line, word_wrap=True)
        console.print(Panel(syntax, title="[bold blue]Code Context[/]", border_style="blue", box=box.ROUNDED))

    explanation = result.get("explanation", "No explanation available.")
    console.print(Panel(f"[bold white]{explanation}[/]", title="[bold cyan]Explanation[/]", border_style="cyan", box=box.ROUNDED, expand=False))

    fix = result.get("fix", "No suggested fix available.")
    console.print(Panel(f"[bold white]{fix}[/]", title="[bold green]Suggested Fix[/]",  border_style="green", box=box.ROUNDED, expand=False))

    if result.get("ast_insight"):
        console.print(Panel(f"[bold white]{result['ast_insight']}[/]", title="[bold magenta]AST Insight[/]", border_style="magenta", box=box.ROUNDED, expand=False))

def print_result_json(result: dict):
    """Prints the translated error as a single-line JSON object on stdout."""
    print(json.dumps(result, ensure_ascii=False))

def print_execution_error(script_name: str, message: str, as_json: bool, error_type: str = "Execution Error"):
    """Prints an execution error when running a script fails."""
    if as_json:
        print(json.dumps({"error": error_type.lower().replace(" ", "_"), "message": message}))
    else:
        console.print(Panel(f"[bold red]{message}[/]", title=f"[bold red]{error_type}[/]", border_style="red", box=box.ROUNDED, expand=False))
