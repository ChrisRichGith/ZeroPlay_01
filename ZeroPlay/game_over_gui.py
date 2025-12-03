# game_over_gui.py
"""
Defines the custom Game Over window with a tombstone image.
"""
import tkinter as tk
from tkinter import ttk
from utils import center_window

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None

class GameOverWindow(tk.Toplevel):
    """A Toplevel window to display the game over message and image."""

    def __init__(self, parent, player, on_close_callback):
        """Initializes the game over window."""
        super().__init__(parent)
        self.title("Game Over")
        self.transient(parent)
        self.grab_set()
        self.on_close_callback = on_close_callback

        self.create_widgets(player)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_widgets(self, player):
        """Creates and places the widgets for the window."""
        container = ttk.Frame(self, padding="10")
        container.pack(fill="both", expand=True)

        # Tombstone Image
        self.tombstone_photo = None  # Keep a reference
        if Image and ImageTk:
            try:
                img = Image.open("assets/grabstein.png")
                img.thumbnail((200, 300))
                self.tombstone_photo = ImageTk.PhotoImage(img)
                image_label = ttk.Label(container, image=self.tombstone_photo)
                image_label.pack(pady=(10, 10))
            except FileNotFoundError:
                # Fallback if image is missing
                ttk.Label(container, text="[Grabstein Bild nicht gefunden]").pack(pady=(10,10))

        # Game Over Text
        message = f"Ruhe in Frieden, {player.name}.\n\nDu hast Level {player.level} erreicht."
        message_label = ttk.Label(container, text=message, font=("Helvetica", 12), justify=tk.CENTER)
        message_label.pack(pady=(0, 15))

        # OK Button
        ok_button = ttk.Button(container, text="OK", command=self.on_close)
        ok_button.pack(pady=(0, 10))

        # Center the window over its parent
        center_window(self, self.master.winfo_toplevel())

    def on_close(self):
        """Handles the closing of the window."""
        self.destroy()
        if self.on_close_callback:
            self.on_close_callback()
