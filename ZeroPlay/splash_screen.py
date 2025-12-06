# splash_screen.py
"""
Defines the Splash Screen for language selection and game introduction.
"""
import tkinter as tk
from tkinter import ttk
from translations import get_text

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
        self.lang_label = ttk.Label(lang_frame, text="")
        self.lang_label.pack(side=tk.LEFT, padx=5)
        de_radio = ttk.Radiobutton(lang_frame, text="Deutsch", variable=self.selected_lang, value="de")
        de_radio.pack(side=tk.LEFT)
        en_radio = ttk.Radiobutton(lang_frame, text="English", variable=self.selected_lang, value="en")
        en_radio.pack(side=tk.LEFT, padx=10)

        # Introduction Text
        self.intro_frame = ttk.Frame(container, padding=10)
        self.intro_frame.pack(pady=20)
        self.title_label = ttk.Label(self.intro_frame, text="", font=("Helvetica", 14, "bold"))
        self.title_label.pack(anchor="w", pady=(0, 10))
        self.objective_title_label = ttk.Label(self.intro_frame, text="", font=("Helvetica", 12, "underline"))
        self.objective_title_label.pack(anchor="w")
        self.objective_text_label = ttk.Label(self.intro_frame, text="", justify=tk.LEFT, wraplength=600)
        self.objective_text_label.pack(anchor="w", pady=(5, 15))
        self.controls_title_label = ttk.Label(self.intro_frame, text="", font=("Helvetica", 12, "underline"))
        self.controls_title_label.pack(anchor="w")
        self.controls_text_label = ttk.Label(self.intro_frame, text="", justify=tk.LEFT, wraplength=600)
        self.controls_text_label.pack(anchor="w", pady=(5, 0))

        # Continue Button
        self.continue_button = ttk.Button(
            container,
            text="",
            command=lambda: self.callbacks['continue'](self.selected_lang.get())
        )
        self.continue_button.pack(pady=10)

    def update_text(self, *args):
        """Updates the UI text based on the selected language."""
        lang = self.selected_lang.get()
        self.lang_label.config(text=get_text(lang, "language"))
        self.title_label.config(text=get_text(lang, "splash_title"))
        self.objective_title_label.config(text=get_text(lang, "splash_objective_title"))
        self.objective_text_label.config(text=get_text(lang, "splash_objective_text"))
        self.controls_title_label.config(text=get_text(lang, "splash_controls_title"))
        self.controls_text_label.config(text=get_text(lang, "splash_controls_text"))
        self.continue_button.config(text=get_text(lang, "continue"))
