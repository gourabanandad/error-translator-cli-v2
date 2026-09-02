import ast
import difflib
import os


class ScopedSymbolCollector(ast.NodeVisitor):
    """
    Walks the Abstract Syntax Tree (AST) of the target Python file.
    It collects variables, functions, classes, and attributes defined in the code.

    Crucially, it respects lexical scope by using the crash line number.
    It will only descend into function or class bodies if the crash actually
    happened inside them, preventing it from suggesting variables from unrelated scopes.
    """

    def __init__(self, target_line: int):
        self.target_line = target_line
        self.names = set()  # Variables (e.g., local/global variable assignments)
        self.attributes = set()  # Object attributes/methods (e.g., obj.method_name)
        self.classes = set()  # Class names defined in the scope
        self.functions = set()  # Function names defined in the scope
        self.imports = set()  # Imported modules or aliases

    def visit_Name(self, node):
        """Collects variable names when they are assigned (Store context)."""
        if isinstance(node.ctx, ast.Store):
            self.names.add(node.id)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        """
        Collects the function name into the current scope.
        Only visits the function's internal body if the error line is within it.
        """
        # The function's name is always added to the enclosing scope
        self.names.add(node.name)
        self.functions.add(node.name)

        # SCOPING LOGIC: Only visit the body if the crash happened INSIDE this function
        if hasattr(node, "lineno") and hasattr(node, "end_lineno"):
            if node.lineno <= self.target_line <= node.end_lineno:
                self.generic_visit(node)
        else:
            self.generic_visit(node)

    def visit_ClassDef(self, node):
        """
        Collects the class name into the current scope.
        Only visits the class's internal body if the error line is within it.
        """
        # The class name is always added to the enclosing scope
        self.names.add(node.name)
        self.classes.add(node.name)

        # SCOPING LOGIC: Only visit the body if the crash happened INSIDE this class
        if hasattr(node, "lineno") and hasattr(node, "end_lineno"):
            if node.lineno <= self.target_line <= node.end_lineno:
                self.generic_visit(node)
        else:
            self.generic_visit(node)

    def visit_Attribute(self, node):
        """Collects attribute accesses (e.g., node.attr)."""
        self.attributes.add(node.attr)
        self.generic_visit(node)

    def visit_Import(self, node):
        """Collects basic import names or aliases."""
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.imports.add(name)
            self.names.add(name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        """Collects specific names imported from a module."""
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.imports.add(name)
            self.names.add(name)
        self.generic_visit(node)


def get_ast_suggestions(filepath: str, line_number: str, target_word: str, error_type: str) -> str:
    """
    Parses a Python file into an AST, extracts available symbols for the crashing scope,
    and uses string matching (difflib) to find the closest suggestion to a misspelled word.

    Args:
        filepath: Absolute path to the Python file that crashed.
        line_number: The line number where the error was thrown.
        target_word: The misspelled variable, attribute, or import.
        error_type: The type of error (NameError, AttributeError, etc.) to determine the pool of words.

    Returns:
        str: The suggested correct spelling, or None if no close match is found.
    """
    if not os.path.exists(filepath) or filepath == "Unknown File":
        return None

    try:
        target_line = int(line_number) if line_number.isdigit() else 0

        # Read the crashing source file
        with open(filepath, encoding="utf-8") as f:
            source_code = f.read()

        # Parse it into an Abstract Syntax Tree
        tree = ast.parse(source_code)

        # Walk the tree and collect symbols visible at the target line
        collector = ScopedSymbolCollector(target_line)
        collector.visit(tree)

        # Determine the search pool based on the type of error
        pool = set()
        if error_type == "NameError":
            pool = collector.names | collector.functions | collector.classes
        elif error_type == "AttributeError":
            pool = collector.attributes | collector.functions
        elif error_type in ("ImportError", "ModuleNotFoundError"):
            pool = collector.classes | collector.functions | collector.names | collector.imports

        # Use difflib to find the most similar symbol in the pool
        # Cutoff=0.6 means the suggestion must be at least 60% similar to the target word
        matches = difflib.get_close_matches(target_word, pool, n=1, cutoff=0.6)

        if matches:
            return matches[0]
        return None

    except (SyntaxError, UnicodeDecodeError, OSError, ValueError):
        # If parsing or processing fails (e.g., SyntaxError in the file), fail gracefully
        return None
