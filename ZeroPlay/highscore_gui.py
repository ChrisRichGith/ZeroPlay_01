# highscore_gui.py
"""
Defines the GUI window for displaying high scores.
"""
import tkinter as tk
from tkinter import ttk
from highscore_manager import load_highscores
from utils import center_window, format_currency
from translations import get_text

class HighscoreWindow(tk.Toplevel):
    """A Toplevel window to display the high score list."""

    def __init__(self, parent, language="de"):
        """Initializes the high score window."""
        super().__init__(parent)
        self.language = language
        self.title(self._("highscores"))
        self.transient(parent)
        self.grab_set()

        self.create_widgets()
        self.populate_scores()

        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def _(self, key):
        """Alias for get_text for shorter calls."""
        return get_text(self.language, key)

    def create_widgets(self):
        """Creates and places the widgets for the window."""
        container = ttk.Frame(self, padding="10")
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)

        # Define the columns for the Treeview
        columns = ("name", "level", "rebirths", "bosses", "resources", "best_equipment", "copper")
        self.tree = ttk.Treeview(container, columns=columns, show="headings")

        # Define headings
        self.tree.heading("name", text=self._("name"))
        self.tree.heading("level", text=self._("level"))
        self.tree.heading("rebirths", text=self._("rebirths"))
        self.tree.heading("bosses", text=self._("bosses_defeated"))
        self.tree.heading("resources", text=self._("resources"))
        self.tree.heading("best_equipment", text=self._("equipment"))
        self.tree.heading("copper", text=self._("gold"))

        # Configure column widths
        self.tree.column("name", width=120)
        self.tree.column("level", width=50, anchor="center")
        self.tree.column("rebirths", width=100, anchor="center")
        self.tree.column("bosses", width=100, anchor="center")
        self.tree.column("resources", width=200)
        self.tree.column("best_equipment", width=300)
        self.tree.column("copper", width=100, anchor="e")

        self.tree.grid(row=0, column=0, sticky="nsew")

        # Add a scrollbar
        scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Close button
        close_button = ttk.Button(container, text=self._("close"), command=self.destroy)
        close_button.grid(row=1, column=0, columnspan=2, pady=(10, 0))

        center_window(self, self.master.winfo_toplevel())

    def populate_scores(self):
        """Loads scores and inserts them into the Treeview."""
        scores = load_highscores()
        for score in scores:
            copper_formatted = format_currency(score.get("copper", 0))

            resources_dict = score.get("resources", {})
            resources_str = ", ".join(f"{name}: {amount}" for name, amount in resources_dict.items())
            if not resources_str:
                resources_str = "N/A"

            player_name = score.get("name", "")
            if score.get("cheat_activated", False):
                player_name += f" ({self._('cheat_activated')})"

            best_equipment = (
                f"{self._('weapon')}: {score.get('best_weapon', 'N/A')}, "
                f"{self._('head')}: {score.get('best_head', 'N/A')}, "
                f"{self._('chest')}: {score.get('best_chest', 'N/A')}"
            )
            self.tree.insert("", tk.END, values=(
                player_name,
                score.get("level", 0),
                score.get("rebirths", 0),
                score.get("bosses_defeated", 0),
                resources_str,
                best_equipment,
                copper_formatted
            ))
