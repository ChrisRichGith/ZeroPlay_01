# class_selection_gui.py
"""
Defines the GUI for the class selection window.
"""
import tkinter as tk
from tkinter import ttk
from game_data import CLASSES

class ClassSelectionWindow:
    """Manages the class selection GUI window."""

    def __init__(self, parent):
        """
        Initializes the class selection window.
        """
        self.parent = parent
        self.selected_class = None

        self.window = tk.Toplevel(parent)
        self.window.title("Klassenauswahl")
        self.window.geometry("400x350")
        self.window.resizable(False, False)

        self.window.protocol("WM_DELETE_WINDOW", self.cancel)
        self.window.transient(parent)
        self.window.grab_set()

        self.create_widgets()
        self.window.wait_window()

    def create_widgets(self):
        """Creates the widgets for the class selection window."""
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Wähle deine Klasse:", font=("Helvetica", 14)).pack(pady=(0, 10))

        self.class_var = tk.StringVar()

        for class_name in CLASSES.keys():
            rb = ttk.Radiobutton(main_frame, text=class_name, variable=self.class_var, value=class_name, command=self.show_class_info)
            rb.pack(anchor=tk.W, padx=10)

        self.info_frame = ttk.LabelFrame(main_frame, text="Klasseninfo", padding="10")
        self.info_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.desc_label = ttk.Label(self.info_frame, text="", wraplength=350)
        self.desc_label.pack(anchor=tk.W, pady=5)

        self.attr_label = ttk.Label(self.info_frame, text="", font=("Courier", 10))
        self.attr_label.pack(anchor=tk.W, pady=5)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0))

        self.ok_button = ttk.Button(button_frame, text="Bestätigen", command=self.confirm, state=tk.DISABLED)
        self.ok_button.pack(side=tk.RIGHT)

        cancel_button = ttk.Button(button_frame, text="Abbrechen", command=self.cancel)
        cancel_button.pack(side=tk.RIGHT, padx=(0, 10))

    def show_class_info(self):
        """Displays information about the selected class."""
        class_name = self.class_var.get()
        if class_name:
            class_data = CLASSES[class_name]
            self.desc_label.config(text=class_data["description"])

            attr_text = "Start-Attribute:\n"
            for stat, value in class_data["attributes"].items():
                attr_text += f"  - {stat:<12}: {value}\n"
            self.attr_label.config(text=attr_text)

            self.ok_button.config(state=tk.NORMAL)

    def confirm(self):
        """Confirms the selection and closes the window."""
        self.selected_class = self.class_var.get()
        self.window.destroy()

    def cancel(self):
        """Cancels the selection and closes the window."""
        self.selected_class = None
        self.window.destroy()

def choose_class(parent):
    """Opens the class selection window and returns the chosen class name."""
    selection_dialog = ClassSelectionWindow(parent)
    return selection_dialog.selected_class
