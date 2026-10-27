"""Inspect import candidates without importing modules named by a traceback."""

import ast
import difflib
import math
import sys
from pathlib import Path
from types import ModuleType
from typing import Optional

_MATH_NAMES = frozenset(vars(math))


class _ModuleBindings(ast.NodeVisitor):
    """Collect possible module bindings, excluding function/class locals."""

    def __init__(self):
        self.names: set[str] = set()

    def visit(self, node):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            self.names.add(node.name)
            return
        if isinstance(
            node, (ast.Lambda, ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)
        ):
            return
        super().visit(node)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store):
            self.names.add(node.id)

    def visit_Import(self, node):
        for alias in node.names:
            self.names.add(alias.asname or alias.name.split(".")[0])

    def visit_ImportFrom(self, node):
        for alias in node.names:
            if alias.name != "*":
                self.names.add(alias.asname or alias.name)


def _local_module_names(file_path: str, parts: list[str]) -> Optional[set[str]]:
    """Return None if absent, or an empty set for a local target we cannot inspect."""
    if not isinstance(file_path, str):
        return None
    try:
        source = Path(file_path).resolve()
        if not source.is_file():
            return None
        roots = [source.parent]
        package_root = source.parent
        while (package_root / "__init__.py").is_file():
            if package_root.parent == package_root:
                break
            package_root = package_root.parent
        if package_root != roots[0]:
            roots.append(package_root)

        for root in roots:
            target = root.joinpath(*parts)
            for candidate in (target / "__init__.py", target.with_suffix(".py")):
                if not candidate.is_file():
                    continue
                resolved = candidate.resolve()
                if not resolved.is_relative_to(root):
                    return set()
                tree = ast.parse(resolved.read_text(encoding="utf-8"))
                collector = _ModuleBindings()
                collector.visit(tree)
                return collector.names
    except (OSError, ValueError, SyntaxError, UnicodeDecodeError, RecursionError):
        return set()
    return None


def get_import_suggestion(file_path: str, module_name: str, missing_name: str) -> Optional[str]:
    """Suggest an exported name using local source or an already loaded module."""
    if not isinstance(module_name, str) or not isinstance(missing_name, str):
        return None
    parts = module_name.split(".")
    if not all(part.isidentifier() for part in parts) or not missing_name.isidentifier():
        return None

    names = _local_module_names(file_path, parts)
    if names is None:
        if module_name == "math":
            names = _MATH_NAMES
        else:
            module = sys.modules.get(module_name)
            # Subclasses and lazy/proxy objects may execute hooks on attribute access.
            if type(module) is not ModuleType:
                return None
            names = vars(module)
    pool = {name for name in names if isinstance(name, str) and name.isidentifier()}
    if missing_name in pool:
        return None
    # This cutoff scores names in the target module. ast_engine.py uses 0.6
    # for symbols in the crashing file; review both when tuning similarity.
    matches = difflib.get_close_matches(missing_name, sorted(pool), n=1, cutoff=0.5)
    return matches[0] if matches else None
