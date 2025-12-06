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

    def __init__(self, parent, player, on_close_callback, death_by_boss=False):
        """Initializes the game over window."""
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()
        self.on_close_callback = on_close_callback

        # Set title and widgets based on the cause of death
        if death_by_boss:
            self.title("Wiedergeburt!")
            self.create_rebirth_widgets(player)
        else:
            self.title("Game Over")
            self.create_death_widgets(player)

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        # Center the window over its parent
        center_window(self, self.master.winfo_toplevel())

    def create_death_widgets(self, player):
        """Creates and places the widgets for a permanent death."""
        container = ttk.Frame(self, padding="10")
        container.pack(fill="both", expand=True)

        # Tombstone Image
        self.tombstone_photo = None
        if Image and ImageTk:
            try:
                img = Image.open("assets/grabstein.png")
                img.thumbnail((200, 300))
                self.tombstone_photo = ImageTk.PhotoImage(img)
                image_label = ttk.Label(container, image=self.tombstone_photo)
                image_label.pack(pady=(10, 10))
            except FileNotFoundError:
                ttk.Label(container, text="[Grabstein Bild nicht gefunden]").pack(pady=(10,10))

        message = f"Ruhe in Frieden, {player.name}.\n\nDu bist bei einer Quest gestorben und dein Charakter wurde gelöscht."
        message_label = ttk.Label(container, text=message, font=("Helvetica", 12), justify=tk.CENTER)
        message_label.pack(pady=(0, 15))

        ok_button = ttk.Button(container, text="OK", command=self.on_close)
        ok_button.pack(pady=(0, 10))

    def create_rebirth_widgets(self, player):
        """Creates and places the widgets for a rebirth."""
        container = ttk.Frame(self, padding="10")
        container.pack(fill="both", expand=True)

        # Phoenix Image (or some other symbol of rebirth)
        self.rebirth_photo = None
        if Image and ImageTk:
            try:
                # Assuming a phoenix or similar rebirth image exists
                img = Image.open("assets/bosses/boss_phoenix.png")
                img.thumbnail((250, 250))
                self.rebirth_photo = ImageTk.PhotoImage(img)
                image_label = ttk.Label(container, image=self.rebirth_photo)
                image_label.pack(pady=(10, 10))
            except FileNotFoundError:
                 ttk.Label(container, text="[Bild der Wiedergeburt nicht gefunden]").pack(pady=(10,10))

        message = (f"{player.name} wurde von einem Boss besiegt!\n\n"
                   "Durch die Niederlage bist du stärker geworden.\n"
                   "Du wirst auf Level 1 zurückgesetzt, aber deine Basisattribute wurden permanent verbessert!")
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
