# game_over_gui.py
"""
Defines the custom Game Over window with a tombstone image.
"""
import tkinter as tk
from tkinter import ttk
from utils import center_window
from translations import get_text

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None

class GameOverWindow(tk.Toplevel):
    """A Toplevel window to display the game over message and image."""

    def __init__(self, parent, player, on_close_callback, death_by_boss=False, language="de"):
        """Initializes the game over window."""
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()
        self.on_close_callback = on_close_callback
        self.language = language

        if death_by_boss:
            self.title(self._("rebirth_title"))
            self.create_rebirth_widgets(player)
        else:
            self.title(self._("game_over_title"))
            self.create_death_widgets(player)

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        center_window(self, self.master.winfo_toplevel())

    def _(self, key):
        """Alias for get_text for shorter calls."""
        return get_text(self.language, key)

    def create_death_widgets(self, player):
        """Creates and places the widgets for a permanent death."""
        container = ttk.Frame(self, padding="10")
        container.pack(fill="both", expand=True)

        self.tombstone_photo = None
        if Image and ImageTk:
            try:
                img = Image.open("assets/grabstein.png")
                img.thumbnail((200, 300))
                self.tombstone_photo = ImageTk.PhotoImage(img)
                image_label = ttk.Label(container, image=self.tombstone_photo)
                image_label.pack(pady=(10, 10))
            except FileNotFoundError:
                ttk.Label(container, text=self._("tombstone_not_found_placeholder")).pack(pady=(10,10))

        message = self._("game_over_quest_text").format(name=player.name)
        message_label = ttk.Label(container, text=message, font=("Helvetica", 12), justify=tk.CENTER)
        message_label.pack(pady=(0, 15))

        ok_button = ttk.Button(container, text=self._("ok"), command=self.on_close)
        ok_button.pack(pady=(0, 10))

    def create_rebirth_widgets(self, player):
        """Creates and places the widgets for a rebirth."""
        container = ttk.Frame(self, padding="10")
        container.pack(fill="both", expand=True)

        self.rebirth_photo = None
        if Image and ImageTk:
            try:
                img = Image.open("assets/bosses/boss_phoenix.png")
                img.thumbnail((250, 250))
                self.rebirth_photo = ImageTk.PhotoImage(img)
                image_label = ttk.Label(container, image=self.rebirth_photo)
                image_label.pack(pady=(10, 10))
            except FileNotFoundError:
                 ttk.Label(container, text=self._("rebirth_image_not_found_placeholder")).pack(pady=(10,10))

        message = self._("game_over_rebirth_text").format(name=player.name)
        message_label = ttk.Label(container, text=message, font=("Helvetica", 12), justify=tk.CENTER)
        message_label.pack(pady=(0, 15))

        ok_button = ttk.Button(container, text=self._("ok"), command=self.on_close)
        ok_button.pack(pady=(0, 10))

    def on_close(self):
        """Handles the closing of the window."""
        self.destroy()
        if self.on_close_callback:
            self.on_close_callback()
