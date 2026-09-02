import traceback

from error_translator.core import translate_error

try:
    from IPython.core.ultratb import AutoFormattedTB
    from IPython.display import Markdown, display
except ImportError:
    # If they somehow import this outside of Jupyter, fail gracefully
    AutoFormattedTB = None


def custom_exc(shell, etype, evalue, tb, tb_offset=None):
    """
    Custom IPython exception handler. Displays the standard traceback,
    followed by a structured Markdown diagnostic summary.
    """
    # 1. Print standard Jupyter traceback
    shell.showtraceback((etype, evalue, tb), tb_offset=tb_offset)

    # 2. Extract raw traceback text
    if AutoFormattedTB:
        tb_formatter = AutoFormattedTB(mode="plain", theme_name="NoColor")
        raw_traceback = tb_formatter.text(etype, evalue, tb)
    else:
        raw_traceback = "".join(traceback.format_exception(etype, evalue, tb))

    # 3. Translate error
    translation = translate_error(raw_traceback)

    explanation = translation.get("explanation", "Unable to translate this error.")
    fix = translation.get("fix", "No remediation suggestion available.")
    detected_error = translation.get("matched_error", "Unknown error")
    ast_insight = translation.get("ast_insight")

    # Print summary to stdout
    print(f"Error: {explanation}")
    print(f"Fix: {fix}")

    # Build Markdown diagnostic panel for notebook UI
    md_text = "---\n"
    md_text += "### Error Translator Diagnostic\n\n"
    md_text += f"**Detected Error:** `{detected_error}`\n\n"
    md_text += f"**Explanation:** {explanation}\n\n"
    md_text += f"**Suggested Fix:** {fix}\n\n"

    if ast_insight:
        md_text += f"**AST Insight:** {ast_insight}\n\n"

    md_text += "---\n"

    try:
        display(Markdown(md_text))
    except NameError:
        pass


def load_ipython_extension(ipython):
    """
    Loads the Error Translator extension in an IPython/Jupyter environment.

    Usage:
        %load_ext error_translator.jupyter
        %reload_ext error_translator.jupyter
        %unload_ext error_translator.jupyter
    """
    ipython.set_custom_exc((Exception,), custom_exc)

    try:
        display(
            Markdown(
                "> **Error Translator active.** Unhandled cell exceptions will be translated automatically."
            )
        )
    except NameError:
        print("Error Translator active.")


def unload_ipython_extension(ipython):
    """Unloads the extension and restores default Jupyter behavior."""
    ipython.set_custom_exc((), None)
    print("Error Translator disabled.")
