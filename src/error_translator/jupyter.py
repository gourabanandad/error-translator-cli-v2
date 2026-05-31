import traceback
from error_translator.core import translate_error

try:
    from IPython.display import display, Markdown
    from IPython.terminal.interactiveshell import TerminalInteractiveShell
    from IPython.core.ultratb import AutoFormattedTB
except ImportError:
    # If they somehow import this outside of Jupyter, fail gracefully
    AutoFormattedTB = None
    pass

def custom_exc(shell, etype, evalue, tb, tb_offset=None):
    """
    This function intercepts the crash, prints the standard traceback, 
    and then renders our translated explanation in Markdown.
    """
    # 1. Print the standard Jupyter traceback so they still see exactly where it crashed
    shell.showtraceback((etype, evalue, tb), tb_offset=tb_offset)
    
    # 2. Extract the raw traceback string for our engine using AutoFormattedTB
    if AutoFormattedTB:
        tb_formatter = AutoFormattedTB(mode='plain', theme_name='NoColor')
        raw_traceback = tb_formatter.text(etype, evalue, tb)
    else:
        raw_traceback = "".join(traceback.format_exception(etype, evalue, tb))
    
    # 3. Feed it to the Error Translator engine
    translation = translate_error(raw_traceback)
    
    # 4. Extract insights
    explanation = translation.get("explanation", "We couldn't translate this error.")
    fix = translation.get("fix", "No fix available.")
    detected_error = translation.get("matched_error", "No code context available.")
    ast_insight = translation.get("ast_insight")
    
    # 5. Print the translation to stdout
    print(f"Error: {explanation}")
    print(f"Fix: {fix}")
    
    # 6. Build a beautiful Markdown output for Jupyter
    md_text = f"---\n"
    md_text += f"### Error Translator Insight\n\n"
    md_text += f"**Detected Error:** {detected_error}\n\n"
    md_text += f"**Explanation:** {explanation}\n\n"
    md_text += f"**Suggested Fix:** {fix}\n\n"
    
    if ast_insight:
        md_text += f"\n**AST Insight:** {ast_insight}\n"
        
    md_text += "---\n"
    
    # 7. Render it directly inside the notebook cell (if in Jupyter)
    try:
        display(Markdown(md_text))
    except NameError:
        # Not in Jupyter environment
        pass


def load_ipython_extension(ipython):
    """
    Loads the Jupyter extension. 
    Usage in Jupyter: %load_ext error_translator.jupyter
    """
    # Hijack the default exception handler
    ipython.set_custom_exc((Exception,), custom_exc)
    
    # Print a nice success message (if in Jupyter)
    try:
        display(Markdown("> **Error Translator loaded!** Any unhandled crashes in this notebook will now be translated."))
    except NameError:
        # Not in Jupyter environment
        print("Error Translator loaded!")


def unload_ipython_extension(ipython):
    """Unloads the extension and restores default Jupyter behavior."""
    ipython.set_custom_exc(tuple(), None)
    print("Error Translator disabled.")