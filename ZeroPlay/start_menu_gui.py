# start_menu_gui.py
"""
Defines the GUI Frame for the main start menu.
"""
import tkinter as tk
from tkinter import ttk
from save_load_system import get_save_files
from utils import format_currency
from translations import get_text
from save_load_system import get_save_files, load_game

class StartMenu(ttk.Frame):
    """Manages the start menu frame."""

    def __init__(self, parent, callbacks, language="de"):
        super().__init__(parent)
        self.callbacks = callbacks
        self.language = language
        self.selected_save = None
        self._setup_vars()
        self.create_widgets()

    def _(self, key):
        """Alias for get_text for shorter calls."""
        return get_text(self.language, key)

    def _setup_vars(self):
        """Sets up StringVars for the preview display."""
        self.preview_name_var = tk.StringVar(value=f"{self._('name')}: -")
        self.preview_level_var = tk.StringVar(value=f"{self._('level')}: -")
        self.preview_gold_var = tk.StringVar(value=f"{self._('gold')}: -")
        self.preview_stats_vars = {
            'Stärke': tk.StringVar(value=f"{self._('strength')}: -"),
            'Intelligenz': tk.StringVar(value=f"{self._('intelligence')}: -"),
            'Glück': tk.StringVar(value=f"{self._('luck')}: -"),
        }

    def create_widgets(self):
        self.master.title(self._('start_menu_title'))

        center_frame = ttk.Frame(self, padding=20)
        center_frame.pack(expand=True)

        ttk.Label(center_frame, text="Chronicle of the Idle Hero", font=("Helvetica", 20, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 20))

        load_frame = ttk.LabelFrame(center_frame, text=self._('load_save'), padding=10)
        load_frame.grid(row=1, column=0, sticky="ns", padx=(0, 10))

        self.save_listbox = tk.Listbox(load_frame, height=10)
        self.save_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(load_frame, orient=tk.VERTICAL, command=self.save_listbox.yview)
        self.save_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.populate_save_list()
        self.save_listbox.bind('<<ListboxSelect>>', self.on_select)

        right_column_frame = ttk.Frame(center_frame)
        right_column_frame.grid(row=1, column=1, sticky="ns", padx=(10, 0))

        preview_frame = ttk.LabelFrame(right_column_frame, text=self._('preview'), padding=10)
        preview_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(preview_frame, textvariable=self.preview_name_var).pack(anchor=tk.W)
        ttk.Label(preview_frame, textvariable=self.preview_level_var).pack(anchor=tk.W)
        ttk.Label(preview_frame, textvariable=self.preview_gold_var).pack(anchor=tk.W, pady=(0, 10))
        for stat_key in ['Stärke', 'Intelligenz', 'Glück']:
            ttk.Label(preview_frame, textvariable=self.preview_stats_vars[stat_key]).pack(anchor=tk.W)

        button_frame = ttk.Frame(right_column_frame, padding=(0, 10, 0, 0))
        button_frame.pack(fill=tk.X, pady=(10,0))
        button_frame.columnconfigure((0, 1), weight=1)

        self.load_button = ttk.Button(button_frame, text=self._('load'), command=self.load_game, state=tk.DISABLED)
        self.load_button.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        new_game_button = ttk.Button(button_frame, text=self._('new_game'), command=self.callbacks['new'])
        new_game_button.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        highscore_button = ttk.Button(button_frame, text=self._('highscores'), command=self.callbacks.get('highscores', lambda: None))
        highscore_button.grid(row=1, column=0, sticky="ew", padx=(0, 5), pady=(5,0))
        quit_button = ttk.Button(button_frame, text=self._('quit'), command=self.callbacks['quit'])
        quit_button.grid(row=1, column=1, sticky="ew", padx=(5, 0), pady=(5,0))

        intro_label = ttk.Label(center_frame, text=self._('start_menu_intro'), justify=tk.CENTER, style="TSecondary.TLabel")
        intro_label.grid(row=2, column=0, columnspan=2, pady=(20, 0))

    def populate_save_list(self):
        self.save_listbox.delete(0, tk.END)
        for save_name in get_save_files():
            self.save_listbox.insert(tk.END, save_name)

    def on_select(self, event=None):
        if not self.save_listbox.curselection():
            self.load_button.config(state=tk.DISABLED)
            self.selected_save = None
            self.clear_preview()
            return
        self.load_button.config(state=tk.NORMAL)
        self.selected_save = self.save_listbox.get(self.save_listbox.curselection())
        char = load_game(self.selected_save)
        if char:
            self.preview_name_var.set(f"{self._('name')}: {char.name} ({char.klasse})")
            self.preview_level_var.set(f"{self._('level')}: {char.level}")
            self.preview_gold_var.set(f"{self._('gold')}: {format_currency(char.copper)}")
            self.preview_stats_vars['Stärke'].set(f"{self._('strength')}: {char.attributes.get('Stärke', 0)}")
            self.preview_stats_vars['Intelligenz'].set(f"{self._('intelligence')}: {char.attributes.get('Intelligenz', 0)}")
            self.preview_stats_vars['Glück'].set(f"{self._('luck')}: {char.attributes.get('Glück', 0)}")
        else:
            self.clear_preview()

    def clear_preview(self):
        self.preview_name_var.set(f"{self._('name')}: -")
        self.preview_level_var.set(f"{self._('level')}: -")
        self.preview_gold_var.set(f"{self._('gold')}: -")
        self.preview_stats_vars['Stärke'].set(f"{self._('strength')}: -")
        self.preview_stats_vars['Intelligenz'].set(f"{self._('intelligence')}: -")
        self.preview_stats_vars['Glück'].set(f"{self._('luck')}: -")

    def load_game(self):
        if self.selected_save and self.callbacks['load']:
            self.callbacks['load'](self.selected_save)
