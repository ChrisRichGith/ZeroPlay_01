# utils.py
"""
Contains utility functions for the game, such as currency formatting.
"""

def format_currency(copper_amount):
    """
    Converts a total copper amount into a formatted string (gold, silver, copper).
    100 copper = 1 silver
    100 silver = 1 gold
    """
    if copper_amount == 0:
        return "0c"

    gold = copper_amount // 10000
    silver = (copper_amount % 10000) // 100
    copper = copper_amount % 100

    parts = []
    if gold > 0:
        parts.append(f"{gold}🪙")
    if silver > 0:
        parts.append(f"{silver}💿")
    if copper > 0:
        parts.append(f"{copper}🟤")

    return " ".join(parts)

def center_window(window, parent):
    """
    Centers a tkinter window over its parent window, handling multi-monitor setups.

    Args:
        window: The tkinter window (Toplevel) to center.
        parent: The parent window.
    """
    window.update_idletasks()

    # Get dimensions of the popup window
    width = window.winfo_width()
    height = window.winfo_height()

    # Get the position and dimensions of the parent window
    parent_x = parent.winfo_x()
    parent_y = parent.winfo_y()
    parent_width = parent.winfo_width()
    parent_height = parent.winfo_height()

    # Calculate the center position relative to the parent
    x = parent_x + (parent_width // 2) - (width // 2)
    y = parent_y + (parent_height // 2) - (height // 2)

    # Set the geometry of the popup window to place it correctly
    window.geometry(f'{width}x{height}+{x}+{y}')
