# class_selection_frame.py
"""
Defines the GUI Frame for the class selection scene.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from game_data import CLASSES
from translations import get_text

class ClassSelectionFrame(ttk.Frame):
    """Manages the class selection frame."""

    def __init__(self, parent, callbacks, language="de"):
        super().__init__(parent)
        self.callbacks = callbacks
        self.language = language
        self.player_name = ""
        self.selected_class = "Krieger"
        self.create_widgets()
        self.class_listbox.select_set(0)
        self.show_class_info()

    def _(self, key):
        """Alias for get_text for shorter calls."""
        return get_text(self.language, key)

    def create_widgets(self):
        """Creates the widgets for the class selection frame."""
        center_frame = ttk.Frame(self, padding=20)
        center_frame.pack(expand=True)

        ttk.Label(center_frame, text=self._("class_selection_title"), font=("Helvetica", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 20))

        name_frame = ttk.Frame(center_frame)
        name_frame.grid(row=1, column=0, columnspan=2, pady=10)
        ttk.Label(name_frame, text=self._("enter_name")).pack(side=tk.LEFT, padx=5)
        self.name_entry = ttk.Entry(name_frame, width=30)
        self.name_entry.pack(side=tk.LEFT)

        content_frame = ttk.Frame(center_frame)
        content_frame.grid(row=2, column=0, columnspan=2, sticky="nsew")
        content_frame.columnconfigure(0, weight=1, uniform="group1")
        content_frame.columnconfigure(1, weight=1, uniform="group1")
        content_frame.rowconfigure(0, weight=1)

        left_frame = ttk.LabelFrame(content_frame, text=self._("select_class"), padding=10)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left_frame.rowconfigure(0, weight=1)
        left_frame.columnconfigure(0, weight=1)

        self.class_listbox = tk.Listbox(left_frame, exportselection=False, height=len(CLASSES))
        self.class_map = {"Krieger": "warrior", "Magier": "mage", "Schurke": "rogue"}
        for class_name in CLASSES.keys():
            self.class_listbox.insert(tk.END, self._(self.class_map.get(class_name, "")))
        self.class_listbox.grid(row=0, column=0, sticky="nsew")
        self.class_listbox.bind('<<ListboxSelect>>', self.show_class_info)

        right_frame = ttk.Frame(content_frame)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        right_frame.rowconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)
        right_frame.columnconfigure(0, weight=1)

        self.image_label = ttk.Label(right_frame, anchor=tk.CENTER)
        self.image_label.grid(row=0, column=0, sticky="nsew")
        self.character_photo = None

        self.info_frame = ttk.LabelFrame(right_frame, text="Info", padding="10")
        self.info_frame.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        self.desc_label = ttk.Label(self.info_frame, text="", wraplength=380, justify=tk.LEFT)
        self.desc_label.pack(anchor=tk.W, pady=5)
        self.attr_label = ttk.Label(self.info_frame, text="", font=("Courier", 10), justify=tk.LEFT)
        self.attr_label.pack(anchor=tk.W, pady=5)

        button_frame = ttk.Frame(center_frame)
        button_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(20, 0))
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        back_button = ttk.Button(button_frame, text=self._("back"), command=self.callbacks['back'])
        back_button.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        self.confirm_button = ttk.Button(button_frame, text=self._("confirm"), command=self.confirm, state=tk.DISABLED)
        self.confirm_button.grid(row=0, column=1, sticky="ew", padx=(5, 0))

    def show_class_info(self, event=None):
        selected_indices = self.class_listbox.curselection()
        if not selected_indices: return

        # Map selected index back to original class name
        original_class_name = list(CLASSES.keys())[selected_indices[0]]
        self.selected_class = original_class_name

        class_data = CLASSES[original_class_name]
        self.desc_label.config(text=self._(original_class_name.lower() + "_desc"))

        attr_text = f"{self._('attributes')}:\n"
        stat_map = {"Stärke": "strength", "Agilität": "agility", "Intelligenz": "intelligence", "Glück": "luck"}
        for stat, value in class_data["attributes"].items():
            translated_stat = self._(stat_map.get(stat, stat))
            attr_text += f"  - {translated_stat:<12}: {value}\n"
        self.attr_label.config(text=attr_text)
        self.confirm_button.config(state=tk.NORMAL)

        try:
            img_path = class_data.get("image_path")
            if img_path:
                img = Image.open(img_path)
                img.thumbnail((250, 350))
                self.character_photo = ImageTk.PhotoImage(img)
                self.image_label.config(image=self.character_photo, text="")
            else:
                self.image_label.config(image="", text="No image available")
        except Exception as e:
            self.image_label.config(image="", text=f"Image error:\n{e}")

    def confirm(self):
        self.player_name = self.name_entry.get().strip()
        if not self.player_name:
            messagebox.showwarning(self._("error"), self._("enter_name"), parent=self)
            return
        if not self.selected_class:
            messagebox.showwarning(self._("error"), self._("select_class"), parent=self)
            return
        if self.callbacks['confirm']:
            self.callbacks['confirm'](self.player_name, self.selected_class)
