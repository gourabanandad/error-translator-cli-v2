# Real-World Input → Output Examples

Here are some examples of raw tracebacks and their translated output using Error Translator.

Note: file/line/code context is only available when the input includes traceback location lines like `File "...", line N`.
Note: the CLI prints a Rich panel UI; examples below use normalized plain text labels for readability.

### Example A: Type mismatch

Input traceback:

```text
Traceback (most recent call last):
  File "app.py", line 14, in <module>
    total = "Users: " + 42
TypeError: can only concatenate str (not "int") to str
```

Translated output:

```text
Detected Error:
TypeError: can only concatenate str (not "int") to str

Location: app.py (Line 14)

   |
   |  total = "Users: " + 42
   |

Explanation:
You are trying to add a string to an int, which Python cannot do.

Suggested Fix:
Convert the int to a string first using str() before concatenating.
```

### Example B: Missing variable typo

Input error line:

```text
NameError: name 'usr_count' is not defined
```

Translated output:

```text
Detected Error:
NameError: name 'usr_count' is not defined

Location: Unknown File (Line Unknown Line)

Explanation:
You tried to use a variable or function named 'usr_count', but Python doesn't recognize it.

Suggested Fix:
Check if 'usr_count' is spelled correctly, or ensure you defined/imported it before using it.
```

### Example C: Index out of range

Input traceback:

```text
Traceback (most recent call last):
  File "script.py", line 3, in <module>
    print(items[5])
IndexError: list index out of range
```

Translated output:


```text
Detected Error:
IndexError: list index out of range

Location: script.py (Line 3)

   |
   |  print(items[5])
   |

Explanation:
You tried to access an index (position 5) that doesn't exist in the list.

Suggested Fix:
Check the length of the list using len(items) - 1 to find the last valid index.
```

### Example D: Key not found in dictionary

Input error line:

```text
KeyError: 'age'
```

Translated output:

```text
Detected Error:
KeyError: 'age'

Location: Unknown File (Line Unknown Line)

Explanation:
You tried to access a dictionary key ('age') that doesn't exist.

Suggested Fix:
Use dict.get('age', default_value) to safely retrieve the key with a fallback,
or ensure the key is set before accessing it.
```

### Example E: Division by zero

Input error line:

```text
ZeroDivisionError: division by zero
```

Translated output:

```text
Detected Error:
ZeroDivisionError: division by zero

Location: Unknown File (Line Unknown Line)

Explanation:
You attempted to divide a number by zero, which is mathematically undefined.

Suggested Fix:
Add a condition to check if the denominator is zero before performing division.
```

### Example F: File not found

Input traceback:

```text
Traceback (most recent call last):
  File "reader.py", line 2, in <module>
    with open('data.csv', 'r') as f:
FileNotFoundError: [Errno 2] No such file or directory: 'data.csv'
```

Translated output:

```text
Detected Error:
FileNotFoundError: [Errno 2] No such file or directory: 'data.csv'

Location: reader.py (Line 2)

   |
   |  with open('data.csv', 'r') as f:
   |

Explanation:
Python cannot find the file 'data.csv' in the current working directory.

Suggested Fix:
Verify the file path and name. Use os.path.exists() to check before opening,
or provide an absolute path.
```

### Example G: Attribute error on wrong type

Input error line:

```text
AttributeError: 'int' object has no attribute 'append'
```

Translated output:

```text
Detected Error:
AttributeError: 'int' object has no attribute 'append'

Location: Unknown File (Line Unknown Line)

Explanation:
You are trying to call .append() on an integer. .append() is a method for lists.

Suggested Fix:
If you meant to collect multiple values, initialize a list instead (my_list = []).
If you're working with a single integer, review what operation you intended.
```

### Example H: Import module not found

Input error line:

```text
ModuleNotFoundError: No module named 'requests'
```

Translated output:

```text
Detected Error:
ModuleNotFoundError: No module named 'requests'

Location: Unknown File (Line Unknown Line)

Explanation:
Python cannot find the 'requests' module. It is not part of the standard library
and needs to be installed separately or you have a typo in the module name.

Suggested Fix:
Install the missing package using pip: pip install requests.
If the module is your own file, check the import path and file location.
```

### Example I: Indentation mismatch

Input traceback:

```text
Traceback (most recent call last):
  File "script.py", line 5
    print("Hello")
        ^
IndentationError: expected an indented block
```

Translated output:

```text
Detected Error:
IndentationError: expected an indented block

Location: script.py (Line 5)

   |
   |  print("Hello")
   |

Explanation:
Python uses indentation to define blocks of code. You likely forgot to indent
after a statement that expects a nested block (e.g., after if, for, def).

Suggested Fix:
Add consistent spaces or tabs to the line after the colon. Use 4 spaces per level.
```

### Example J: Value conversion error

Input error line:

```text
ValueError: invalid literal for int() with base 10: '42.5'
```

Translated output:

```text
Detected Error:
ValueError: invalid literal for int() with base 10: '42.5'

Location: Unknown File (Line Unknown Line)

Explanation:
You are trying to convert the string '42.5' to an integer, but it contains a
decimal point, so it's not a valid whole number.

Suggested Fix:
If you need to keep the fractional part, use float() instead of int().
If you want to truncate, convert to float first then to int: int(float('42.5')).
```

### Example K: Recursion limit exceeded

Input traceback:

```text
Traceback (most recent call last):
  File "recursive.py", line 4, in <module>
    infinite()
  File "recursive.py", line 2, in infinite
    return infinite()
  File "recursive.py", line 2, in infinite
    return infinite()
  ...
RecursionError: maximum recursion depth exceeded
```

Translated output:

```text
Detected Error:
RecursionError: maximum recursion depth exceeded

Location: recursive.py (Line 2)

   |
   |  return infinite()
   |

Explanation:
A function is calling itself so many times that Python's recursion limit has been reached. This usually happens when a recursive function lacks a proper base case or stop condition.

Suggested Fix:
Add a base case to stop the recursion. Check that the function arguments change in each call to eventually reach the base case. If deep recursion is intentional, you can increase the limit with sys.setrecursionlimit(), but restructuring the code to use iteration is often safer.
```

## Using Error Translator in Jupyter Notebooks

Error Translator integrates seamlessly with Jupyter notebooks and JupyterLab environments, allowing you to debug interactively with clear, actionable error explanations.

### Setup

Load the extension in any Jupyter notebook cell:

```python
%load_ext error_translator.jupyter
```

This command registers Error Translator as a custom exception handler. Any unhandled exception in subsequent cells will automatically be translated and displayed in a user-friendly format.

### Example Jupyter Usage

**Cell 1:**
```python
%load_ext error_translator.jupyter
```

**Cell 2:**
```python
# This will trigger an unhandled exception
data = {"name": "Alice", "age": 30}
print(data["email"])  # KeyError: 'email'
```

**Output:**

The notebook displays:
1. **Standard Jupyter traceback** (showing the actual error location and stack)
2. **Error Translator panel** with:
   - **Detected Error**: The error type and message
   - **Explanation**: Clear description of what went wrong
   - **Suggested Fix**: Actionable steps to resolve the issue
   - **AST Insight** (if available): Code-specific hints based on the context

```text
Traceback (most recent call last):
  File "<ipython-input-2-...>", line 3, in <module>
    print(data["email"])
KeyError: 'email'

---
### Error Translator Insight

**Detected Error:** KeyError: 'email'

**Explanation:** You tried to access a dictionary key ('email') that doesn't exist.

**Suggested Fix:** Use dict.get('email', default_value) to safely retrieve the key with a fallback, or ensure the key is set before accessing it.

---
```

### Advantages in Jupyter

- **No Code Changes Required**: Just load the extension and debug naturally.
- **Visual Formatting**: Errors are presented in clean Markdown panels alongside your notebook.
- **Offline & Fast**: All translations happen locally without network latency.
- **Interactive Debugging**: Understand errors immediately without leaving your notebook environment.
