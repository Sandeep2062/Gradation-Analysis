import pyperclip

def copy_to_clipboard(values):
    """Copy a list of values to clipboard as formatted text"""
    text = "\n".join([f"{value:.2f}" for value in values])
    pyperclip.copy(text)