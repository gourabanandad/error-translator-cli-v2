"""
Script execution module.
Responsible for running target Python scripts and intercepting their output.
"""
import sys
import subprocess
from .core import translate_error
from .ui import print_result, print_result_json, print_execution_error

def run_script(script_name: str, *, as_json: bool = False):
    """
    Run a target Python script and dynamically intercept/translate traceback output if it fails.
    
    Args:
        script_name (str): The script to run.
        as_json (bool): Whether to output the error translation in JSON format instead of Rich UI.
    """
    try:
        # Run the script and capture stdout and stderr
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            # Script succeeded, just print its normal output
            print(result.stdout, end="")
        else:
            # Script failed, print partial stdout and translate the error output
            if result.stdout:
                print(result.stdout, end="")

            translation = translate_error(result.stderr)
            if as_json:
                print_result_json(translation)
            else:
                print_result(translation)

    except FileNotFoundError:
        # Handling the case where the provided script doesn't exist
        print_execution_error(
            script_name, 
            f"Could not find script '{script_name}'", 
            as_json, 
            "Execution Error"
        )
    except Exception as exc:
        # Catch-all for unexpected runtime issues with the sub-process
        print_execution_error(
            script_name, 
            str(exc), 
            as_json, 
            "Runtime Error"
        )
