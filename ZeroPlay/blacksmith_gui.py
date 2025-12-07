# blacksmith_gui.py
"""
Defines the GUI for the Blacksmith.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from blacksmith import Blacksmith
from utils import center_window
from game_data import RARITIES
from translations import get_text

class BlacksmithWindow(tk.Toplevel):
    """Manages the blacksmith interaction window."""

    def __init__(self, parent, player, on_close_callback, language="de"):
        super().__init__(parent)
        self.language = language
        self.title(self._("visit_blacksmith"))
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
        center_window(self, self.master.winfo_toplevel())

    def _(self, key):
        """Alias for get_text for shorter calls."""
        return get_text(self.language, key)

    def create_widgets(self):
        """Creates and places all widgets for the blacksmith window."""
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

        equip_frame = ttk.LabelFrame(main_frame, text=self._("equipment"), padding="10")
        equip_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        equip_frame.rowconfigure(0, weight=1)
        equip_frame.columnconfigure(0, weight=1)

        self.equip_listbox = tk.Listbox(equip_frame)
        self.equip_listbox.grid(row=0, column=0, sticky="nsew")
        self.equip_listbox.bind('<<ListboxSelect>>', self.on_item_select)

        details_frame = ttk.LabelFrame(main_frame, text=self._("blacksmith_upgrade"), padding="10")
        details_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

        self.item_name_label = ttk.Label(details_frame, text=self._("select_item_prompt"), font=("", 12, "bold"))
        self.item_name_label.pack(pady=5)

        self.current_stats_label = ttk.Label(details_frame, text=self._("current_stats"))
        self.current_stats_label.pack(pady=5, anchor="w")

        self.next_stats_label = ttk.Label(details_frame, text=self._("next_level"))
        self.next_stats_label.pack(pady=5, anchor="w")

        self.cost_label = ttk.Label(details_frame, text=self._("cost"))
        self.cost_label.pack(pady=10, anchor="w")

        self.upgrade_button = ttk.Button(details_frame, text=self._("upgrade_button"), command=self.upgrade_item, state=tk.DISABLED)
        self.upgrade_button.pack(pady=20, fill=tk.X, ipady=5)

        self.player_resources_label = ttk.Label(details_frame, text=self._("your_resources"))
        self.player_resources_label.pack(side=tk.BOTTOM, pady=10)

    def update_display(self):
        """Updates all displayed information."""
        self.equip_listbox.delete(0, tk.END)
        self.slot_map = {}
        for i, (slot, item) in enumerate(self.player.equipment.items()):
            display_slot = self._(slot.lower())
            self.slot_map[i] = slot
            if item:
                self.equip_listbox.insert(tk.END, f"[{display_slot}] {item.name}")
            else:
                self.equip_listbox.insert(tk.END, f"[{display_slot}] {self._('empty_slot')}")

        resources_text_list = [self._("your_resources")]
        for name, amount in self.player.resources.items():
            resource_key = f"resource_{name.lower().replace(' ', '_')}"
            translated_name = self._(resource_key)
            resources_text_list.append(f"{translated_name}: {amount}")
        self.player_resources_label.config(text="\n".join(resources_text_list))
        self.update_details()

    def on_item_select(self, event=None):
        """Handles the selection of an item in the listbox."""
        selected_indices = self.equip_listbox.curselection()
        if not selected_indices:
            self.selected_item = None
            return
        selected_slot_name = self.slot_map.get(selected_indices[0])
        self.selected_item = self.player.equipment.get(selected_slot_name)
        self.update_details()

    def update_details(self):
        """Updates the details section for the selected item."""
        if not self.selected_item:
            self.item_name_label.config(text=self._("select_item_prompt"))
            self.current_stats_label.config(text=self._("current_stats"))
            self.next_stats_label.config(text=self._("next_level"))
            self.cost_label.config(text=self._("cost"))
            self.upgrade_button.config(state=tk.DISABLED)
            return

        max_upgrades = RARITIES[self.selected_item.rarity].get("max_upgrades", 0)
        upgrade_level_text = f"+{self.selected_item.upgrade_level} / +{max_upgrades}"
        self.item_name_label.config(text=f"{self.selected_item.name} ({upgrade_level_text})")

        stats_text = self._("current_stats") + "\n" + "\n".join([f"  {self._(stat.lower())}: {val}" for stat, val in self.selected_item.stats_boost.items()])
        self.current_stats_label.config(text=stats_text)

        if self.selected_item.upgrade_level >= max_upgrades:
            max_stats_text = self._("current_stats") + f" ({self._('max_stat_indicator')}):\n" + "\n".join([f"  {self._(stat.lower())}: {val} ({self._('max_stat_indicator')})" for stat, val in self.selected_item.stats_boost.items()])
            self.current_stats_label.config(text=max_stats_text)
            self.next_stats_label.config(text=self._("max_level_reached"))
            self.cost_label.config(text="")
            self.upgrade_button.config(state=tk.DISABLED)
            return

        next_level_stats = {stat: val + 1 for stat, val in self.selected_item.stats_boost.items()}
        next_stats_text = f"{self._('next_level')} (+{self.selected_item.upgrade_level + 1}):\n" + "\n".join([f"  {self._(stat.lower())}: {val}" for stat, val in next_level_stats.items()])
        self.next_stats_label.config(text=next_stats_text)

        cost = self.blacksmith.get_upgrade_cost(self.selected_item)
        cost_text_list = [self._("cost")]
        for name, amount in cost.items():
            resource_key = f"resource_{name.lower().replace(' ', '_')}"
            translated_name = self._(resource_key)
            cost_text_list.append(f"  {translated_name}: {amount}")
        self.cost_label.config(text="\n".join(cost_text_list))

        if self.blacksmith.can_afford_upgrade(self.player.resources, cost):
            self.upgrade_button.config(state=tk.NORMAL)
        else:
            self.upgrade_button.config(state=tk.DISABLED)

    def upgrade_item(self):
        """Handles the item upgrade logic."""
        if not self.selected_item: return
        success, message = self.blacksmith.upgrade_item(self.player, self.selected_item)
        self.update_display()
        if success:
            messagebox.showinfo(self._("upgrade_success_title"), message, parent=self)
        else:
            messagebox.showwarning(self._("error"), message, parent=self)

    def on_close(self):
        """Called when the window is closed."""
        self.on_close_callback()
        self.destroy()
