# Real-World Examples Catalog

This catalog demonstrates how **Error Translator** transforms raw, confusing Python stack traces into clear, actionable advice.

---

## 1. Type & Value Errors

### Scenario 1.1: Incompatible String and Integer Concatenation (`TypeError`)

**The Bug:** Attempting to add an integer directly to a string using the `+` operator.

#### Raw Python Traceback:
```text
Traceback (most recent call last):
  File "app.py", line 14, in <module>
    total = "Users: " + 42
TypeError: can only concatenate str (not "int") to str
```

#### Error Translator Output:
```text
┌─ Detected Error ─────────────────────────────────────────────────────────────┐
│ TypeError: can only concatenate str (not "int") to str                       │
├─ Location ───────────────────────────────────────────────────────────────────┤
│ File: app.py  |  Line: 14                                                    │
├─ Code Context ───────────────────────────────────────────────────────────────┤
│ 14 │ total = "Users: " + 42                                                  │
├─ Explanation ────────────────────────────────────────────────────────────────┤
│ You are trying to add a string to a int, which Python cannot do.             │
├─ Suggested Fix ──────────────────────────────────────────────────────────────┤
│ Convert the int to a string first using str() before concatenating.          │
└──────────────────────────────────────────────────────────────────────────────┘
```

#### JSON Payload:
```json
{
  "explanation": "You are trying to add a string to a int, which Python cannot do.",
  "fix": "Convert the int to a string first using str() before concatenating.",
  "ast_insight": null,
  "matched_error": "TypeError: can only concatenate str (not \"int\") to str",
  "file": "app.py",
  "line": "14",
  "code": "total = \"Users: \" + 42"
}
```

---

### Scenario 1.2: Converting Float String to Integer (`ValueError`)

**The Bug:** Passing a decimal string like `'42.5'` directly to `int()`.

#### Raw Python Traceback:
```text
Traceback (most recent call last):
  File "parser.py", line 8, in parse_age
    age = int(raw_input)
ValueError: invalid literal for int() with base 10: '42.5'
```

#### Error Translator Output:
```text
┌─ Detected Error ─────────────────────────────────────────────────────────────┐
│ ValueError: invalid literal for int() with base 10: '42.5'                   │
├─ Location ───────────────────────────────────────────────────────────────────┤
│ File: parser.py  |  Line: 8                                                  │
├─ Code Context ───────────────────────────────────────────────────────────────┤
│ 8 │ age = int(raw_input)                                                     │
├─ Explanation ────────────────────────────────────────────────────────────────┤
│ You are trying to convert the string '42.5' to an integer, but it contains a  │
│ decimal point, so it's not a valid whole number.                             │
├─ Suggested Fix ──────────────────────────────────────────────────────────────┤
│ If you need to keep decimals, use float(). If truncating, convert to float    │
│ first: int(float('42.5')).                                                   │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

### Scenario 1.3: Subscripting a NoneType Object (`TypeError`)

**The Bug:** Attempting to access an index or key on a function return value that returned `None`.

#### Raw Python Traceback:
```text
Traceback (most recent call last):
  File "fetcher.py", line 22, in get_user_name
    first_name = user_record["name"]
TypeError: 'NoneType' object is not subscriptable
```

#### Error Translator Output:
```text
┌─ Detected Error ─────────────────────────────────────────────────────────────┐
│ TypeError: 'NoneType' object is not subscriptable                            │
├─ Location ───────────────────────────────────────────────────────────────────┤
│ File: fetcher.py  |  Line: 22                                                │
├─ Code Context ───────────────────────────────────────────────────────────────┤
│ 22 │ first_name = user_record["name"]                                        │
├─ Explanation ────────────────────────────────────────────────────────────────┤
│ You are trying to access an item from a variable that is None.               │
├─ Suggested Fix ──────────────────────────────────────────────────────────────┤
│ Check why the variable evaluated to None before accessing its elements or    │
│ add an 'if var is not None:' guard.                                          │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Variable Scope & Typo Lookups

### Scenario 2.1: Variable Name Typo with AST Scoped Suggestion (`NameError`)

**The Bug:** Calling a misspelled variable `usr_count` where `user_count` was defined within the local function scope.

#### Raw Python Traceback:
```text
Traceback (most recent call last):
  File "analytics.py", line 32, in compute_metrics
    active_users = usr_count + 10
NameError: name 'usr_count' is not defined
```

#### Error Translator Output:
```text
┌─ Detected Error ─────────────────────────────────────────────────────────────┐
│ NameError: name 'usr_count' is not defined                                   │
├─ Location ───────────────────────────────────────────────────────────────────┤
│ File: analytics.py  |  Line: 32                                              │
├─ Code Context ───────────────────────────────────────────────────────────────┤
│ 32 │ active_users = usr_count + 10                                           │
├─ Explanation ────────────────────────────────────────────────────────────────┤
│ You tried to use a variable or function named 'usr_count', but Python doesn't │
│ recognize it in the current scope.                                           │
├─ Suggested Fix ──────────────────────────────────────────────────────────────┤
│ Check if 'usr_count' is spelled correctly, or define/import it first.        │
├─ AST Insight ────────────────────────────────────────────────────────────────┤
│ Did you mean 'user_count'? There appears to be a typo.                       │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

### Scenario 2.2: Calling a Method on the Wrong Data Type (`AttributeError`)

**The Bug:** Attempting to call `.append()` on an integer or integer variable.

#### Raw Python Traceback:
```text
Traceback (most recent call last):
  File "processor.py", line 9, in accumulate
    score.append(100)
AttributeError: 'int' object has no attribute 'append'
```

#### Error Translator Output:
```text
┌─ Detected Error ─────────────────────────────────────────────────────────────┐
│ AttributeError: 'int' object has no attribute 'append'                       │
├─ Location ───────────────────────────────────────────────────────────────────┤
│ File: processor.py  |  Line: 9                                               │
├─ Code Context ───────────────────────────────────────────────────────────────┤
│ 9 │ score.append(100)                                                        │
├─ Explanation ────────────────────────────────────────────────────────────────┤
│ You are trying to call .append() on an integer. .append() is a method for    │
│ lists.                                                                       │
├─ Suggested Fix ──────────────────────────────────────────────────────────────┤
│ If you meant to collect multiple values, initialize a list: score = [].      │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Collections & Mappings

### Scenario 3.1: Accessing an Out-of-Bounds List Index (`IndexError`)

**The Bug:** Accessing position 5 in a list with only 3 elements.

#### Raw Python Traceback:
```text
Traceback (most recent call last):
  File "pipeline.py", line 18, in get_item
    target = items[5]
IndexError: list index out of range
```

#### Error Translator Output:
```text
┌─ Detected Error ─────────────────────────────────────────────────────────────┐
│ IndexError: list index out of range                                          │
├─ Location ───────────────────────────────────────────────────────────────────┤
│ File: pipeline.py  |  Line: 18                                               │
├─ Code Context ───────────────────────────────────────────────────────────────┤
│ 18 │ target = items[5]                                                       │
├─ Explanation ────────────────────────────────────────────────────────────────┤
│ You are trying to access an item in a list at a position that doesn't exist. │
├─ Suggested Fix ──────────────────────────────────────────────────────────────┤
│ Check the length of your list using len(). Python lists start counting at 0! │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

### Scenario 3.2: Missing Dictionary Key (`KeyError`)

**The Bug:** Querying a key `'auth_token'` on a dictionary that does not contain it.

#### Raw Python Traceback:
```text
Traceback (most recent call last):
  File "auth.py", line 12, in validate_headers
    token = headers['auth_token']
KeyError: 'auth_token'
```

#### Error Translator Output:
```text
┌─ Detected Error ─────────────────────────────────────────────────────────────┐
│ KeyError: 'auth_token'                                                       │
├─ Location ───────────────────────────────────────────────────────────────────┤
│ File: auth.py  |  Line: 12                                                   │
├─ Code Context ───────────────────────────────────────────────────────────────┤
│ 12 │ token = headers['auth_token']                                           │
├─ Explanation ────────────────────────────────────────────────────────────────┤
│ You tried to look up a key named 'auth_token' in a dictionary, but that key  │
│ doesn't exist.                                                               │
├─ Suggested Fix ──────────────────────────────────────────────────────────────┤
│ Check for typos, or use headers.get('auth_token') to safely retrieve it.    │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Syntax & Indentation

### Scenario 4.1: Missing Indented Block (`IndentationError`)

**The Bug:** Declaring a function or loop without indenting the nested statement body.

#### Raw Python Traceback:
```text
Traceback (most recent call last):
  File "server.py", line 5
    def start_worker():
    print("Starting...")
IndentationError: expected an indented block
```

#### Error Translator Output:
```text
┌─ Detected Error ─────────────────────────────────────────────────────────────┐
│ IndentationError: expected an indented block                                 │
├─ Location ───────────────────────────────────────────────────────────────────┤
│ File: server.py  |  Line: 5                                                  │
├─ Code Context ───────────────────────────────────────────────────────────────┤
│ 5 │ print("Starting...")                                                     │
├─ Explanation ────────────────────────────────────────────────────────────────┤
│ Python expected indented code after a statement like 'def', 'if', 'for', or  │
│ 'while', but didn't find it.                                                 │
├─ Suggested Fix ──────────────────────────────────────────────────────────────┤
│ Add indentation (usually 4 spaces) to the lines following the colon.         │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Modules & Package Imports

### Scenario 5.1: Missing Third-Party Dependency (`ModuleNotFoundError`)

**The Bug:** Importing a package that is not installed in the active virtual environment.

#### Raw Python Traceback:
```text
Traceback (most recent call last):
  File "crawler.py", line 1, in <module>
    import requests
ModuleNotFoundError: No module named 'requests'
```

#### Error Translator Output:
```text
┌─ Detected Error ─────────────────────────────────────────────────────────────┐
│ ModuleNotFoundError: No module named 'requests'                              │
├─ Location ───────────────────────────────────────────────────────────────────┤
│ File: crawler.py  |  Line: 1                                                 │
├─ Code Context ───────────────────────────────────────────────────────────────┤
│ 1 │ import requests                                                          │
├─ Explanation ────────────────────────────────────────────────────────────────┤
│ Python is trying to import a package named 'requests', but it isn't          │
│ installed in your current environment.                                       │
├─ Suggested Fix ──────────────────────────────────────────────────────────────┤
│ Open your terminal and run: pip install requests                             │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Filesystem & OS Operations

### Scenario 6.1: Non-Existent File Path (`FileNotFoundError`)

**The Bug:** Opening a relative path that does not exist in the current working directory.

#### Raw Python Traceback:
```text
Traceback (most recent call last):
  File "loader.py", line 4, in <module>
    with open('data.csv', 'r') as f:
FileNotFoundError: [Errno 2] No such file or directory: 'data.csv'
```

#### Error Translator Output:
```text
┌─ Detected Error ─────────────────────────────────────────────────────────────┐
│ FileNotFoundError: [Errno 2] No such file or directory: 'data.csv'           │
├─ Location ───────────────────────────────────────────────────────────────────┤
│ File: loader.py  |  Line: 4                                                  │
├─ Code Context ───────────────────────────────────────────────────────────────┤
│ 4 │ with open('data.csv', 'r') as f:                                         │
├─ Explanation ────────────────────────────────────────────────────────────────┤
│ Python cannot find the file 'data.csv' in the current working directory.     │
├─ Suggested Fix ──────────────────────────────────────────────────────────────┤
│ Verify the file path and name. Use os.path.exists() before opening or        │
│ provide an absolute path.                                                    │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. Arithmetic & Math

### Scenario 7.1: Zero Division (`ZeroDivisionError`)

**The Bug:** Dividing a number by a denominator that evaluates to zero.

#### Raw Python Traceback:
```text
Traceback (most recent call last):
  File "math_util.py", line 7, in calculate_ratio
    return total / count
ZeroDivisionError: division by zero
```

#### Error Translator Output:
```text
┌─ Detected Error ─────────────────────────────────────────────────────────────┐
│ ZeroDivisionError: division by zero                                          │
├─ Location ───────────────────────────────────────────────────────────────────┤
│ File: math_util.py  |  Line: 7                                               │
├─ Code Context ───────────────────────────────────────────────────────────────┤
│ 7 │ return total / count                                                     │
├─ Explanation ────────────────────────────────────────────────────────────────┤
│ You are trying to divide a number by zero, which is mathematically           │
│ impossible.                                                                  │
├─ Suggested Fix ──────────────────────────────────────────────────────────────┤
│ Add an if-statement before the division to check if the denominator is 0.    │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 8. Runtime Limits & Recursion

### Scenario 8.1: Infinite Recursion (`RecursionError`)

**The Bug:** A recursive function without a terminating base case.

#### Raw Python Traceback:
```text
Traceback (most recent call last):
  File "factorial.py", line 5, in <module>
    run_recurse(1)
  File "factorial.py", line 2, in run_recurse
    return run_recurse(n + 1)
  ...
RecursionError: maximum recursion depth exceeded
```

#### Error Translator Output:
```text
┌─ Detected Error ─────────────────────────────────────────────────────────────┐
│ RecursionError: maximum recursion depth exceeded                             │
├─ Location ───────────────────────────────────────────────────────────────────┤
│ File: factorial.py  |  Line: 2                                               │
├─ Code Context ───────────────────────────────────────────────────────────────┤
│ 2 │ return run_recurse(n + 1)                                                │
├─ Explanation ────────────────────────────────────────────────────────────────┤
│ A function is calling itself so many times that Python's recursion limit has │
│ been reached. This usually happens when a function lacks a base case.        │
├─ Suggested Fix ──────────────────────────────────────────────────────────────┤
│ Add a base case to stop the recursion, verify parameters change each step,   │
│ or convert the recursive algorithm to an iterative loop.                     │
└──────────────────────────────────────────────────────────────────────────────┘
```


