# splash_screen.py
"""
Defines the Splash Screen for language selection and game introduction.
"""
import tkinter as tk
from tkinter import ttk

class SplashScreen(ttk.Frame):
    """A frame that allows language selection and shows a game introduction."""

    def __init__(self, parent, callbacks):
        """
        Initializes the splash screen.

        Args:
            parent: The parent tkinter widget.
            callbacks (dict): A dictionary of callback functions.
                              Expected keys: 'continue'.
        """
        super().__init__(parent)
        self.callbacks = callbacks
        self.selected_lang = tk.StringVar(value="de")  # Default to German

        # Introduction and controls text, will be updated by language change
        self.intro_text_de = (
            "Willkommen bei Chronicle of the Idle Hero!\n\n"
            "Ziel des Spiels:\n"
            "Werde stärker, besiege immer mächtigere Bosse und erklimme die Spitze der Highscore-Liste. "
            "Der Tod durch einen Boss ist nicht das Ende, sondern eine Wiedergeburt, die dich stärker macht. "
            "Aber sei gewarnt: Ein Scheitern bei einer normalen Quest führt zur endgültigen Löschung deines Helden!\n\n"
            "Steuerung:\n"
            "Das Spiel wird hauptsächlich mit der Maus bedient. Beginne Quests, besuche Händler und rüste Gegenstände aus, "
            "um dein Abenteuer voranzutreiben."
        )
        self.intro_text_en = (
            "Welcome to Chronicle of the Idle Hero!\n\n"
            "Objective:\n"
            "Grow stronger, defeat increasingly powerful bosses, and climb to the top of the highscore list. "
            "Death by a boss is not the end, but a rebirth that makes you stronger. "
            "But be warned: Failing a normal quest will lead to the permanent deletion of your hero!\n\n"
            "Controls:\n"
            "The game is primarily controlled with the mouse. Start quests, visit merchants, and equip items "
            "to advance your adventure."
        )

        self.create_widgets()
        self.selected_lang.trace_add("write", self.update_text)
        self.update_text() # Initial text setup

    def create_widgets(self):
        """Creates and places all the widgets in the frame."""
        container = ttk.Frame(self, padding=30)
        container.pack(expand=True)

        # Title Label
        title_label = ttk.Label(container, text="Chronicle of the Idle Hero", font=("Helvetica", 24, "bold"))
        title_label.pack(pady=(0, 20))

        # Language Selection
        lang_frame = ttk.Frame(container)
        lang_frame.pack(pady=10)
        ttk.Label(lang_frame, text="Sprache / Language:").pack(side=tk.LEFT, padx=5)
        de_radio = ttk.Radiobutton(lang_frame, text="Deutsch", variable=self.selected_lang, value="de")
        de_radio.pack(side=tk.LEFT)
        en_radio = ttk.Radiobutton(lang_frame, text="English", variable=self.selected_lang, value="en")
        en_radio.pack(side=tk.LEFT, padx=10)

        # Introduction Text
        self.intro_label = ttk.Label(container, text="", justify=tk.LEFT, wraplength=600, font=("Helvetica", 12))
        self.intro_label.pack(pady=20)

        # Continue Button
        continue_button = ttk.Button(
            container,
            text="Weiter",
            command=lambda: self.callbacks['continue'](self.selected_lang.get())
        )
        continue_button.pack(pady=10)
        self.continue_button = continue_button # Keep a reference

    def update_text(self, *args):
        """Updates the UI text based on the selected language."""
        lang = self.selected_lang.get()
        if lang == "de":
            self.intro_label.config(text=self.intro_text_de)
            self.continue_button.config(text="Weiter")
        else: # en
            self.intro_label.config(text=self.intro_text_en)
            self.continue_button.config(text="Continue")
