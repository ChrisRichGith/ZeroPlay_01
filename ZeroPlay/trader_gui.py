# trader_gui.py
"""
Defines the GUI for the Trader window.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from utils import format_currency, center_window

class TraderWindow:
    """Manages the trader GUI window."""

    def __init__(self, parent, player, trader, on_close_callback):
        """
        Initializes the trader window.

        Args:
            parent: The parent window (main GUI).
            player (Character): The player character instance.
            trader (Trader): The trader instance.
            on_close_callback: A function to call when the window is closed.
        """
        self.parent = parent
        self.player = player
        self.trader = trader
        self.on_close_callback = on_close_callback

        # Create a Toplevel window that exists on top of the main window
        self.window = tk.Toplevel(parent)
        self.window.title("Händler")
        self.window.minsize(600, 500)

        # Ensure closing the window calls our custom function
        self.window.protocol("WM_DELETE_WINDOW", self.close_window)

        # Grab focus
        self.window.transient(parent)
        self.window.grab_set()

        self._setup_vars()
        self.create_widgets()
        self.update_display()

        # Center the window over its parent
        center_window(self.window, self.parent.winfo_toplevel())

    def _setup_vars(self):
        """Sets up tkinter StringVars for the trader window."""
        self.player_copper_var = tk.StringVar()
        self.upgrade_cost_var = tk.StringVar()

    def create_widgets(self):
        """Creates the widgets for the trader window."""
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Top frame for player gold and upgrade button
        top_frame = ttk.Frame(main_frame)
        top_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        ttk.Label(top_frame, text="Deine Münzen:").pack(side=tk.LEFT)
        ttk.Label(top_frame, textvariable=self.player_copper_var).pack(side=tk.LEFT, padx=5)

        self.upgrade_button = ttk.Button(top_frame, text="Inventar erweitern", command=self.buy_upgrade)
        self.upgrade_button.pack(side=tk.RIGHT)
        ttk.Label(top_frame, textvariable=self.upgrade_cost_var).pack(side=tk.RIGHT, padx=5)

        # Paned Window for buy/sell sections
        paned_window = ttk.PanedWindow(main_frame, orient=tk.VERTICAL)
        paned_window.grid(row=1, column=0, sticky="nsew")

        # --- Sell Frame ---
        sell_frame = ttk.LabelFrame(paned_window, text="Dein Inventar (Verkaufen)", padding="10")
        paned_window.add(sell_frame, weight=1)
        sell_frame.rowconfigure(0, weight=1)
        sell_frame.columnconfigure(0, weight=1)
        self.sell_listbox = tk.Listbox(sell_frame, bg="#2B2B2B", fg="white", selectbackground="#0078D7")
        self.sell_listbox.grid(row=0, column=0, sticky="nsew")
        sell_scrollbar = ttk.Scrollbar(sell_frame, orient=tk.VERTICAL, command=self.sell_listbox.yview)
        self.sell_listbox.config(yscrollcommand=sell_scrollbar.set)
        sell_scrollbar.grid(row=0, column=1, sticky="ns")

        # --- Buy Frame ---
        buy_frame = ttk.LabelFrame(paned_window, text="Händler-Angebot (Kaufen)", padding="10")
        paned_window.add(buy_frame, weight=1)
        buy_frame.rowconfigure(0, weight=1)
        buy_frame.columnconfigure(0, weight=1)
        self.buy_listbox = tk.Listbox(buy_frame, bg="#2B2B2B", fg="white", selectbackground="#0078D7")
        self.buy_listbox.grid(row=0, column=0, sticky="nsew")
        buy_scrollbar = ttk.Scrollbar(buy_frame, orient=tk.VERTICAL, command=self.buy_listbox.yview)
        self.buy_listbox.config(yscrollcommand=buy_scrollbar.set)
        buy_scrollbar.grid(row=0, column=1, sticky="ns")
        self.buy_listbox.bind('<Double-1>', self.on_item_double_click)

        # Bottom frame for action buttons
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        bottom_frame.columnconfigure(0, weight=1)
        bottom_frame.columnconfigure(1, weight=1)

        sell_buttons_frame = ttk.Frame(bottom_frame)
        sell_buttons_frame.grid(row=0, column=0, sticky="ew")
        self.sell_button = ttk.Button(sell_buttons_frame, text="Verkaufen", command=self.sell_item)
        self.sell_button.pack(fill=tk.X, expand=True, side=tk.LEFT, padx=(0, 5))
        self.sell_all_button = ttk.Button(sell_buttons_frame, text="Schrott verkaufen", command=self.sell_all_non_upgrades)
        self.sell_all_button.pack(fill=tk.X, expand=True, side=tk.LEFT)

        self.buy_button = ttk.Button(bottom_frame, text="Kaufen", command=self.buy_item)
        self.buy_button.grid(row=0, column=1, sticky="ew", padx=(10, 0))

    def update_display(self):
        """Updates all display elements in the trader window."""
        self.player_copper_var.set(format_currency(self.player.copper))
        self.upgrade_cost_var.set(f"Kosten: {format_currency(self.trader.get_upgrade_cost())}")

        self.sell_listbox.delete(0, tk.END)
        for item in self.player.inventory:
            self.sell_listbox.insert(tk.END, str(item))

        # Update buy listbox with class and level-appropriate potions
        self.buy_listbox.delete(0, tk.END)
        self.potions_for_sale = self.trader.get_potions_for_sale(self.player)
        for item in self.potions_for_sale:
            self.buy_listbox.insert(tk.END, str(item))

        # Disable button if player can't afford it
        can_afford_upgrade = self.player.copper >= self.trader.get_upgrade_cost()
        self.upgrade_button.config(state=tk.NORMAL if can_afford_upgrade else tk.DISABLED)

    def sell_item(self):
        """Sells the selected item."""
        selected_indices = self.sell_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Verkaufen", "Bitte wähle einen Gegenstand zum Verkaufen aus.", parent=self.window)
            return

        item_index = selected_indices[0]
        item_name = self.player.inventory[item_index].name
        item_value = self.player.inventory[item_index].value

        sold = self.trader.sell_item(self.player, item_index)
        if sold:
            # messagebox.showinfo("Verkauft!", f"'{item_name}' für {item_value} Gold verkauft.", parent=self.window)
            self.update_display()

    def sell_all_non_upgrades(self):
        """Sells all non-upgrade items and shows a summary."""
        items_sold, copper_gained = self.trader.sell_all_non_upgrades(self.player)

        if items_sold > 0:
            messagebox.showinfo("Alles verkauft",
                                f"{items_sold} Gegenstand/Gegenstände für insgesamt {format_currency(copper_gained)} verkauft.",
                                parent=self.window)
            self.update_display()
        else:
            messagebox.showinfo("Nichts zu verkaufen",
                                "Du hast keine Gegenstände, die kein Upgrade sind.",
                                parent=self.window)

    def buy_upgrade(self):
        """Buys an inventory upgrade."""
        cost = self.trader.get_upgrade_cost()

        # Check if the feature is about to be unlocked
        was_below_50 = self.player.max_inventory_size < 50

        upgraded = self.trader.buy_inventory_upgrade(self.player)

        if upgraded:
            messagebox.showinfo("Upgrade erfolgreich!", f"Inventar für {format_currency(cost)} erweitert!", parent=self.window)
            self.update_display()

            # Show the one-time notification if the threshold was crossed
            if was_below_50 and self.player.max_inventory_size >= 50 and not self.player.autosell_unlocked_notified:
                self.player.autosell_unlocked_notified = True
                messagebox.showinfo(
                    "Feature freigeschaltet!",
                    "Du hast 50+ Inventarplätze!\n\n"
                    "Gegenstände, die kein Upgrade für dich sind, werden ab jetzt beim Aufheben automatisch verkauft.",
                    parent=self.window
                )
        else:
            messagebox.showerror("Nicht genug Münzen", "Du kannst dir dieses Upgrade nicht leisten.", parent=self.window)

    def buy_item(self):
        """Buys the selected item from the trader."""
        selected_indices = self.buy_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Kaufen", "Bitte wähle einen Gegenstand zum Kaufen aus.", parent=self.window)
            return

        item_index = selected_indices[0]
        item_to_buy = self.potions_for_sale[item_index]

        success, message = self.trader.buy_item(self.player, item_to_buy)

        if success:
            self.update_display()
        else:
            messagebox.showerror("Kauf fehlgeschlagen", message, parent=self.window)

    def on_item_double_click(self, event=None):
        """Handles double-click to buy an item."""
        self.buy_item()

    def close_window(self):
        """Handles the window closing event."""
        self.on_close_callback() # Notify the main GUI
        self.window.destroy()
