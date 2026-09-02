"""
Auto-translator hook module.

When imported, this module sets a custom sys.excepthook handler to intercept
unhandled exceptions, translate the traceback into structured advice, and render
it before process termination.
"""

import sys
import traceback

from .core import translate_error
from .ui import print_result


def exception_hook(exc_type, exc_value, tb):
    """
    Custom exception hook that intercepts unhandled Python exceptions.
    Formats the traceback, translates the error into actionable advice,
    and displays the diagnostic panel.

    Args:
        exc_type: The type of the exception.
        exc_value: The exception instance.
        tb: The traceback object containing the call stack.
    """
    tb_lines = traceback.format_exception(exc_type, exc_value, tb)
    tb_string = "".join(tb_lines)
    result = translate_error(tb_string)
    print_result(result)


# Alias for backward compatibility if referenced internally
magic_hook = exception_hook

# Override default exception handler
sys.excepthook = exception_hook
