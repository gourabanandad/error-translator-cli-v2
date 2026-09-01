import os
import sys

from setuptools import Extension, setup

try:
    # Print the stylish banner on installation
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    from error_translator.banner import print_install_banner
    print_install_banner()
except Exception:
    pass

# Windows (MSVC) uses /O2, Linux/Mac (GCC/Clang) uses -O3
compile_args = ['/O2'] if sys.platform == 'win32' else ['-O3']

ext_modules = []
try:
    fast_matcher_module = Extension(
        'error_translator.fast_matcher',
        sources=['src/error_translator/ext/fast_matcher.c'],
        extra_compile_args=compile_args,
        optional=True,
    )
    ext_modules = [fast_matcher_module]

except Exception:
    # C extension is optional — the pure-Python fallback in core.py handles it.
    ext_modules = []

setup(
    ext_modules=ext_modules
)
