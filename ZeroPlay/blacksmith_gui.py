# blacksmith_gui.py
"""
Defines the GUI for the Blacksmith.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from blacksmith import Blacksmith
from utils import center_window
from game_data import RARITIES

class BlacksmithWindow(tk.Toplevel):
    """Manages the blacksmith interaction window."""

    def __init__(self, parent, player, on_close_callback):
        super().__init__(parent)
        self.title("Schmiede")
        self.minsize(800, 600)
        self.transient(parent)
        self.grab_set()

        self.player = player
        self.blacksmith = Blacksmith()
        self.on_close_callback = on_close_callback
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.selected_item = None

        self.create_widgets()
        self.update_display()

        # Center the window over its parent
        center_window(self, self.master.winfo_toplevel())

    def create_widgets(self):
        """Creates and places all widgets for the blacksmith window."""
        # Main frame
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(0, weight=1) # Equipment list
        main_frame.columnconfigure(1, weight=1) # Details
        main_frame.rowconfigure(0, weight=1)

        # --- Equipment List ---
        equip_frame = ttk.LabelFrame(main_frame, text="Ausrüstung", padding="10")
        equip_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        equip_frame.rowconfigure(0, weight=1)
        equip_frame.columnconfigure(0, weight=1)

        self.equip_listbox = tk.Listbox(equip_frame)
        self.equip_listbox.grid(row=0, column=0, sticky="nsew")
        self.equip_listbox.bind('<<ListboxSelect>>', self.on_item_select)

        # --- Details and Upgrade Frame ---
        details_frame = ttk.LabelFrame(main_frame, text="Verbesserung", padding="10")
        details_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

        self.item_name_label = ttk.Label(details_frame, text="Wähle einen Gegenstand", font=("", 12, "bold"))
        self.item_name_label.pack(pady=5)

        self.current_stats_label = ttk.Label(details_frame, text="Aktuelle Werte:")
        self.current_stats_label.pack(pady=5, anchor="w")

        self.next_stats_label = ttk.Label(details_frame, text="Nächste Stufe:")
        self.next_stats_label.pack(pady=5, anchor="w")

        self.cost_label = ttk.Label(details_frame, text="Kosten:")
        self.cost_label.pack(pady=10, anchor="w")

        self.upgrade_button = ttk.Button(details_frame, text="Verbessern", command=self.upgrade_item, state=tk.DISABLED)
        self.upgrade_button.pack(pady=20, fill=tk.X, ipady=5)

        self.player_resources_label = ttk.Label(details_frame, text="Deine Ressourcen:")
        self.player_resources_label.pack(side=tk.BOTTOM, pady=10)


    def update_display(self):
        """Updates all displayed information."""
        # Update equipment list
        self.equip_listbox.delete(0, tk.END)
        for slot, item in self.player.equipment.items():
            if item:
                self.equip_listbox.insert(tk.END, f"[{slot}] {item.name}")
            else:
                self.equip_listbox.insert(tk.END, f"[{slot}] Leer")

        # Update player resources display
        resources_text = "Deine Ressourcen:\n" + "\n".join([f"{name}: {amount}" for name, amount in self.player.resources.items()])
        self.player_resources_label.config(text=resources_text)

        self.update_details()

    def on_item_select(self, event=None):
        """Handles the selection of an item in the listbox."""
        selected_indices = self.equip_listbox.curselection()
        if not selected_indices:
            self.selected_item = None
            return

        selected_slot_index = selected_indices[0]
        # Map listbox index back to the equipment slot name
        slot_order = ['Kopf', 'Brust', 'Waffe'] # This should be consistent
        selected_slot_name = slot_order[selected_slot_index]

        self.selected_item = self.player.equipment.get(selected_slot_name)

        self.update_details()

    def update_details(self):
        """Updates the details section for the selected item."""
        if not self.selected_item:
            self.item_name_label.config(text="Wähle einen Gegenstand")
            self.current_stats_label.config(text="Aktuelle Werte:")
            self.next_stats_label.config(text="Nächste Stufe:")
            self.cost_label.config(text="Kosten:")
            self.upgrade_button.config(state=tk.DISABLED)
            return

        # Item selected
        max_upgrades = RARITIES[self.selected_item.rarity].get("max_upgrades", 0)
        upgrade_level_text = f"+{self.selected_item.upgrade_level} / +{max_upgrades}"
        self.item_name_label.config(text=f"{self.selected_item.name} ({upgrade_level_text})")

        # Current stats
        stats_text = "Aktuelle Werte:\n" + "\n".join([f"  {stat}: {val}" for stat, val in self.selected_item.stats_boost.items()])
        self.current_stats_label.config(text=stats_text)

        # Check if max level is reached
        if self.selected_item.upgrade_level >= max_upgrades:
            max_stats_text = "Aktuelle Werte (Max):\n" + "\n".join([f"  {stat}: {val} (Max)" for stat, val in self.selected_item.stats_boost.items()])
            self.current_stats_label.config(text=max_stats_text)
            self.next_stats_label.config(text="Maximale Stufe erreicht")
            self.cost_label.config(text="")
            self.upgrade_button.config(state=tk.DISABLED)
            return

        # Predicted next stats
        next_level_stats = {stat: val + 1 for stat, val in self.selected_item.stats_boost.items()}
        next_stats_text = f"Nächste Stufe (+{self.selected_item.upgrade_level + 1}):\n" + "\n".join([f"  {stat}: {val}" for stat, val in next_level_stats.items()])
        self.next_stats_label.config(text=next_stats_text)

        # Cost
        cost = self.blacksmith.get_upgrade_cost(self.selected_item)
        cost_text = "Kosten:\n" + "\n".join([f"  {name}: {amount}" for name, amount in cost.items()])
        self.cost_label.config(text=cost_text)

        # Check if player can afford it
        if self.blacksmith.can_afford_upgrade(self.player.resources, cost):
            self.upgrade_button.config(state=tk.NORMAL)
        else:
            self.upgrade_button.config(state=tk.DISABLED)

    def upgrade_item(self):
        """Handles the item upgrade logic."""
        if not self.selected_item:
            return

        success, message = self.blacksmith.upgrade_item(self.player, self.selected_item)

        # Refresh the display immediately after the upgrade attempt to show resource changes.
        self.update_display()

        if success:
            messagebox.showinfo("Erfolg!", message, parent=self)
        else:
            messagebox.showwarning("Fehler", message, parent=self)


    def on_close(self):
        """Called when the window is closed."""
        self.on_close_callback()
        self.destroy()
