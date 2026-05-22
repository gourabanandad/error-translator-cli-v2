"""
Auto-translator hook module.

When imported, this module automatically overrides the default Python exception handler 
(sys.excepthook). Instead of a standard traceback, it intercepts any unhandled exception, 
translates it, and prints a user-friendly explanation using the CLI output formatting.
"""
import sys
import traceback
from .core import translate_error
from .ui import print_result

def magic_hook(exc_type, exc_value, tb):
    """
    Custom exception hook that intercepts unhandled Python exceptions before
    they are printed to the terminal. It formats the standard traceback,
    translates the error into human-readable advice, and prints it using
    the rich UI components.
    
    Args:
        exc_type: The type of the exception (e.g., ValueError, NameError).
        exc_value: The exception instance itself.
        tb: The traceback object containing the call stack.
    """
    # 1. Convert the raw crash data into a standard traceback string
    tb_lines = traceback.format_exception(exc_type, exc_value, tb)
    tb_string = "".join(tb_lines)
    
    # 2. Pass the standard traceback through our translation engine
    result = translate_error(tb_string)
    
    # 3. Print our beautiful colorized output instead of the default Python crash
    print_result(result)

# Replace Python's default sys.excepthook with our custom translation hook.
# Any unhandled exception will now automatically be intercepted and translated.
sys.excepthook = magic_hook