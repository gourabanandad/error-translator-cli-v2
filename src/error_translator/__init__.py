"""
Error Translator
Turn cryptic Python tracebacks into clear, actionable advice.
"""

from .core import translate_error
from .jupyter import load_ipython_extension

__all__ = ["load_ipython_extension", "translate_error"]
