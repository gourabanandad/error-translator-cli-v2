"""
Rule management module.
Responsible for loading and compiling regex-based error translation rules.
"""
import json
import os
import re
from functools import lru_cache

@lru_cache(maxsize=1)
def load_rules():
    """
    Load the error translation rules from the 'rules.json' file.
    The rules dictate how Python tracebacks map to human-readable explanations.
    This function is cached so we only read the file once per runtime.
    
    Returns:
        dict: Parsed JSON data containing "rules" and "default".
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, "rules.json")

    with open(json_path, "r", encoding="utf-8") as file:
        return json.load(file)

@lru_cache(maxsize=1)
def compiled_rules():
    """
    Pre-compile the regular expressions for each rule defined in 'rules.json'.
    Compiling regex patterns once avoids redundant compilation during every
    error translation request, significantly speeding up the matching process.
    
    Returns:
        list of tuples: Each tuple is (compiled_regex, rule_dict).
    """
    data = load_rules()
    compiled = []
    for rule in data["rules"]:
        compiled.append((re.compile(rule["pattern"]), rule))
    return compiled
