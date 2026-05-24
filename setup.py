import sys
import os
from setuptools import setup, Extension

try:
    # Print the stylish banner on installation
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    from error_translator.banner import print_install_banner
    print_install_banner()
except Exception:
    pass

# Windows (MSVC) uses /O2, Linux/Mac (GCC/Clang) uses -O3
compile_args = ['/O2'] if sys.platform == 'win32' else ['-O3']

fast_matcher_module = Extension(
    'error_translator.fast_matcher',
    sources=['src/error_translator/ext/fast_matcher.c'],
    extra_compile_args=compile_args
)

setup(
    ext_modules=[fast_matcher_module]
)
