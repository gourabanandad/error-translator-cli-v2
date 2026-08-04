import argparse
import json
import os

from google import genai  # Nuevo SDK

# ANSI Colors
CYAN = '\033[96m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
MAGENTA = '\033[95m'
RED = '\033[91m'
RESET = '\033[0m'

# Configure Gemini API
api_key = os.environ.get("GEMINI_API_KEY")
client = None
if api_key:
    client = genai.Client(api_key=api_key)
else:
    print(f"{YELLOW}Warning: GEMINI_API_KEY environment variable not set.{RESET}")
    print("Please set it to use the AI auto-generation feature.\n")

def load_json(filepath):
    if os.path.exists(filepath):
        with open(filepath, encoding='utf-8') as f:
            return json.load(f)
    return None

def save_json(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def ask_ai_for_rule(error_name, description):
    """Asks Gemini to generate the regex and explanations."""
    if not client:
        return None
    print(f"{MAGENTA}Asking AI for: {error_name}{RESET}")
    prompt = f"""
    You are an expert Python developer building an error translation tool.
    I need a regex pattern, a simple explanation, and a suggested fix for this Python error:
    
    Error Name: {error_name}
    Official Description: {description}
    
    Return ONLY a valid JSON object with exactly these three keys. Do not include markdown formatting or backticks.
    {{
        "pattern": "The regex pattern to match this error string in a traceback (escape special characters)",
        "explanation": "A beginner-friendly explanation of why this happens.",
        "fix": "Actionable advice on how to fix it."
    }}
    """
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        clean_text = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_text)
    except Exception as e:
        print(f"{RED}AI Generation failed for {error_name}: {e}{RESET}")
        return None

def rule_exists(pattern, existing_patterns):
    return pattern in existing_patterns

def process_error(scraped_error, existing_patterns, auto_mode=False, dry_run=False):
    error_name = scraped_error["error_name"]
    if any(error_name in pat for pat in existing_patterns):
        return None  # Already exists

    print(f"{YELLOW}Missing Rule for: {error_name}{RESET}")
    print(f"Description: {scraped_error['official_description']}\n")

    ai_draft = ask_ai_for_rule(error_name, scraped_error['official_description'])

    if ai_draft and rule_exists(ai_draft["pattern"], existing_patterns):
        print(f"{YELLOW}AI generated pattern already exists. Skipping.{RESET}")
        return None

    if auto_mode:
        if ai_draft:
            print(f"{GREEN}Auto-accepting AI draft.{RESET}")
            return ai_draft
        else:
            print(f"{RED}No AI draft available. Skipping (auto mode).{RESET}")
            return None
    else:
        # Interactive mode
        if ai_draft:
            print(f"{CYAN}--- AI Generated Draft ---{RESET}")
            print(f"Pattern:     {ai_draft.get('pattern', '')}")
            print(f"Explanation: {ai_draft.get('explanation', '')}")
            print(f"Fix:         {ai_draft.get('fix', '')}")
            print(f"{CYAN}--------------------------{RESET}\n")
            choice = input("Accept AI draft? (y/n/edit/quit): ").strip().lower()
        else:
            choice = input("No AI draft available. Add manually? (y/n/quit): ").strip().lower()

        if choice == 'quit':
            return 'quit'
        elif choice == 'y' and ai_draft:
            return ai_draft
        elif choice == 'edit' or (choice == 'y' and not ai_draft):
            print("\n" + "-"*40)
            pattern = input(f"1. Pattern (AI suggested: {ai_draft.get('pattern', '') if ai_draft else ''}): ") or (ai_draft['pattern'] if ai_draft else '')
            explanation = input(f"2. Explanation (AI suggested: {ai_draft.get('explanation', '') if ai_draft else ''}): ") or (ai_draft['explanation'] if ai_draft else '')
            fix = input(f"3. Fix (AI suggested: {ai_draft.get('fix', '') if ai_draft else ''}): ") or (ai_draft['fix'] if ai_draft else '')
            return {
                "pattern": pattern,
                "explanation": explanation,
                "fix": fix
            }
        else:
            return None

def main():
    parser = argparse.ArgumentParser(description="AI-Powered Rule Builder for Error Translator")
    parser.add_argument("--auto", action="store_true", help="Run in automatic mode (accept all AI drafts without prompting)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be added without actually modifying rules.json")
    args = parser.parse_args()

    print(f"{CYAN}===  AI-Powered Rule Builder ==={RESET}")
    if args.auto:
        print(f"{GREEN}Running in AUTOMATIC mode{RESET}")
    if args.dry_run:
        print(f"{YELLOW}DRY RUN - No changes will be saved{RESET}\n")

    rules_data = load_json('error_translator/rules.json')
    scraped_data = load_json('scraped_errors_database.json')

    if not rules_data or not scraped_data:
        print("Error: Could not find databases.")
        return

    existing_patterns = [rule["pattern"] for rule in rules_data["rules"]]
    added_rules = []
    skipped = 0
    quit_early = False

    for scraped_error in scraped_data:
        result = process_error(scraped_error, existing_patterns, auto_mode=args.auto, dry_run=args.dry_run)
        if result == 'quit':
            quit_early = True
            break
        elif isinstance(result, dict):
            added_rules.append(result)
            existing_patterns.append(result["pattern"])
            print(f"{GREEN}✓ Rule added: {result['pattern']}{RESET}\n")
        elif result is None:
            skipped += 1

    print(f"\n{CYAN}=== Summary ==={RESET}")
    print(f"New rules to add: {len(added_rules)}")
    print(f"Skipped/Existing: {skipped}")
    if quit_early:
        print("Process interrupted by user.")

    if added_rules and not args.dry_run:
        rules_data["rules"].extend(added_rules)
        save_json('error_translator/rules.json', rules_data)
        print(f"{GREEN}Successfully saved {len(added_rules)} new rules to rules.json!{RESET}")
    elif args.dry_run:
        print("Dry run completed. No files were modified.")
    else:
        print("No new rules added.")

if __name__ == "__main__":
    main()
