"""
Installation banner module for Error Translator CLI.
This module prints a stylish banner to the terminal during installation.
"""

def print_install_banner():
    """Prints a stylish banner using ANSI escape codes for colors."""
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    YELLOW = '\033[93m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

    error_art = r"""
███████╗██████╗ ██████╗  ██████╗ ██████╗
██╔════╝██╔══██╗██╔══██╗██╔═══██╗██╔══██╗
█████╗  ██████╔╝██████╔╝██║   ██║██████╔╝
██╔══╝  ██╔══██╗██╔══██╗██║   ██║██╔══██╗
███████╗██║  ██║██║  ██║╚██████╔╝██║  ██║
╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝
"""

    translator_art = r"""
████████╗██████╗  █████╗ ███╗   ██╗███████╗██╗      █████╗ ████████╗ ██████╗ ██████╗
╚══██╔══╝██╔══██╗██╔══██╗████╗  ██║██╔════╝██║     ██╔══██╗╚══██╔══╝██╔═══██╗██╔══██╗
   ██║   ██████╔╝███████║██╔██╗ ██║███████╗██║     ███████║   ██║   ██║   ██║██████╔╝
   ██║   ██╔══██╗██╔══██║██║╚██╗██║╚════██║██║     ██╔══██║   ██║   ██║   ██║██╔══██╗
   ██║   ██║  ██║██║  ██║██║ ╚████║███████║███████╗██║  ██║   ██║   ╚██████╔╝██║  ██║
   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝╚══════╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝
"""

    cli_v2_art = r"""
 ██████╗██╗     ██╗    ██╗   ██╗██████╗
██╔════╝██║     ██║    ██║   ██║╚════██╗
██║     ██║     ██║    ██║   ██║ █████╔╝
██║     ██║     ██║    ╚██╗ ██╔╝██╔═══╝
╚██████╗███████╗██║     ╚████╔╝ ███████╗
 ╚═════╝╚══════╝╚═╝      ╚═══╝  ╚══════╝
"""
    
    print(f"\n{BOLD}{RED}{error_art.strip()}{RESET}")
    print(f"{BOLD}{BLUE}{translator_art.strip()}{RESET}")
    print(f"{BOLD}{CYAN}{cli_v2_art.strip()}{RESET}")
    print(f"\n{BOLD}{MAGENTA}================================================================================{RESET}")
    print(f"{BOLD}{YELLOW}⚡ Fatal to Fabulous ⚡{RESET}")
    print(f"{BOLD}{WHITE} ⇆ Offline Python Traceback Explainer V2 ⇆ {RESET}")
    print(f"{BOLD}{MAGENTA}================================================================================{RESET}\n")

if __name__ == "__main__":
    print_install_banner()
