# rpg_gui.py
"""
Defines the main game GUI frame.
"""
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import random
import time
from PIL import Image, ImageTk

from boss import Boss
from character import Character
from quest import Quest
from trader import Trader
from trader_gui import TraderWindow
from blacksmith_gui import BlacksmithWindow
from boss_arena_gui import BossArenaWindow
from save_load_system import save_game
from highscore_manager import save_highscore
from utils import format_currency, center_window
from game_over_gui import GameOverWindow
from game_data import BOSS_TIERS

# Liste verfügbarer Quests
AVAILABLE_QUESTS = [
    {
        "name": "Töte alle Schleime",
        "image": "assets/quests/kill_all_slimes.jpg"
    },
    {
        "name": "Bringe dem Schmied 5 Eisenerz",
        "image": "assets/quests/bring_5_iron_ore_to_the_blacksmith.jpg"
    },
    {
        "name": "Rette eine Prinzessin aus einem anderen Schloss",
        "image": "assets/quests/save_a_princess_from_another_castle.jpg"
    },
    {
        "name": "Sammle 10 leere Flaschen für den Alchemisten",
        "image": "assets/quests/collect_10_empty_bottles_for_the_alchemist.jpg"
    },
    {
        "name": "Poliere die Rüstung des Königs (ohne Bezahlung)",
        "image": "assets/quests/polish_the_king's_armor_(unpaid).jpg"
    },
    {
        "name": "Entwirre die Kopfhörer des Barden",
        "image": "assets/quests/untangle_the_bard's_headphones.jpg"
    },
    {
        "name": "Finde das Rezept für ewige Jugend (und verliere es wieder)",
        "image": "assets/quests/find_the_recipe_for_eternal_youth_(and_lose_it_again).jpg"
    },
    {
        "name": "Bringe dem königlichen Papagei das Fluchen bei",
        "image": "assets/quests/teach_the_royal_parrot_to_curse.jpg"
    },
    {
        "name": "Zähle alle Sandkörner am Strand",
        "image": "assets/quests/count_all_the_grains_of_sand_on_the_beach.jpg"
    },
    {
        "name": "Sortiere die Bibliothek nach der Farbe der Buchrücken",
        "image": "assets/quests/sort_the_library_by_the_color_of_the_book_spines.jpg"
    },
    {
        "name": "Überzeuge einen Drachen, dass er nur ein überdimensionierter Wellensittich ist",
        "image": "assets/quests/convince_a_dragon_he's_just_an_oversized_budgie.jpg"
    },
    {
        "name": "Finde heraus, warum Goblins immer so schlechte Laune haben",
        "image": "assets/quests/find_out_why_goblins_are_always_in_a_bad_mood.jpg"
    },
    {
        "name": "Eskortiere eine sehr langsame Schildkröte über eine sehr breite Straße",
        "image": "assets/quests/escort_a_very_slow_turtle_across_a_very_wide_road.jpg"
    },
    {
        "name": "Störe eine wichtige Zeremonie durch lautes Kauen",
        "image": "assets/quests/disrupt_an_important_ceremony_by_chewing_loudly.jpg"
    }
]

class RpgGui(ttk.Frame):
    """Manages the main game GUI frame."""

    def __init__(self, parent, character, callbacks, initial_messages=None):
        """Initializes the GUI with a character object."""
        super().__init__(parent)
        self.callbacks = callbacks

        self.player = character
        self.trader = Trader()
        self.current_quest = None
        self.is_auto_questing = False
        self.game_over = False
        self.quest_loop_id = None # To hold the .after() job ID
        self.minigame_loop_id = None # To hold the .after() job ID for the minigame

        # Minigame state
        self.minigame_orbs = {}
        self.last_orb_spawn_time = 0
        self.next_orb_spawn_delay = random.uniform(2, 5)
        self.minigame_running = False # Initial state for the minigame

        # Cheat code tracking
        self.typed_string = ""
        self.cheat_buffer = ""
        self.cheat_code = "ordilogicus"
        self.master.bind("<Key>", self.handle_keypress)
        self.master.bind("<Key>", self._handle_keypress, add="+")

        self._setup_string_vars()
        self.create_widgets()
        self.update_display()

        # Display any initial messages (e.g., from rebirth unlocks)
        if initial_messages:
            for msg in initial_messages:
                self.show_unlock_message(msg)

    def show_unlock_message(self, message):
        """Shows a special message in the log for unlocks."""
        self.add_to_log(f"⭐ {message} ⭐")
        messagebox.showinfo("Meilenstein freigeschaltet!", message, parent=self)

    def handle_keypress(self, event):
        """Handles key presses for cheat codes."""
        self.typed_string += event.char.lower()
        # Keep the last 20 characters to avoid overly long strings
        self.typed_string = self.typed_string[-20:]

        if "showmethemoney" in self.typed_string:
            self.player.add_cheat_resources()
            self.set_loot_text("Cheat: +100 Eisenerz, +100 Juwel")
            self.update_display()
            self.typed_string = "" # Reset after use

    def _setup_string_vars(self):
        """Creates tkinter StringVars to link data to labels."""
        self.char_name_var = tk.StringVar()
        self.char_level_var = tk.StringVar()
        self.item_level_var = tk.StringVar()
        self.char_gold_var = tk.StringVar()
        self.stats_vars = {stat: tk.StringVar() for stat in ['Stärke', 'Intelligenz', 'Glück']}
        self.equipment_vars = {slot: tk.StringVar() for slot in ['Kopf', 'Brust', 'Waffe']}
        self.lp_label_var = tk.StringVar()
        self.mp_label_var = tk.StringVar()
        self.xp_label_var = tk.StringVar()
        self.energie_label_var = tk.StringVar()
        self.wut_label_var = tk.StringVar()

    def create_widgets(self):
        """Creates and places all the widgets in the window."""
        # Main layout grid
        self.columnconfigure(0, weight=1, uniform="char_inv_group") # Character status
        self.columnconfigure(1, weight=0) # Actions (narrow)
        self.columnconfigure(2, weight=1, uniform="char_inv_group") # Inventory
        self.rowconfigure(0, weight=1) # Top area
        self.rowconfigure(1, weight=0) # Bottom area for the log

        # Create main frames for each section
        char_frame_container = ttk.Frame(self)
        char_frame_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        actions_frame = ttk.Frame(self)
        actions_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        inventory_frame = ttk.Frame(self)
        inventory_frame.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)
        inventory_frame.rowconfigure(0, weight=1)
        inventory_frame.columnconfigure(0, weight=1)


        log_frame = ttk.Frame(self)
        log_frame.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=10, pady=(0, 10))

        # Populate the frames
        self._create_character_frame(char_frame_container)
        self._create_actions_frame(actions_frame)

        # Create and populate the notebook for equipment and inventory
        notebook = ttk.Notebook(inventory_frame)
        notebook.grid(row=0, column=0, sticky="nsew")
        equipment_tab = ttk.Frame(notebook)
        inventory_tab = ttk.Frame(notebook)
        notebook.add(equipment_tab, text='Ausrüstung')
        notebook.add(inventory_tab, text='Inventar')

        self._create_equipment_frame(equipment_tab)
        self._create_inventory_frame(inventory_tab)

        self._create_log_frame(log_frame)

    def _create_character_frame(self, parent):
        char_frame = ttk.LabelFrame(parent, text="Charakterstatus", padding="10")
        char_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10), anchor='n')
        char_frame.columnconfigure(2, weight=1) # Allow portrait column to expand

        # --- Left side: Stats ---
        labels = {"Name:": self.char_name_var, "Level:": self.char_level_var, "Item Level:": self.item_level_var, "Gold:": self.char_gold_var}
        for i, (text, var) in enumerate(labels.items()):
            ttk.Label(char_frame, text=text).grid(row=i, column=0, sticky="w")
            ttk.Label(char_frame, textvariable=var).grid(row=i, column=1, sticky="w")

        attr_frame = ttk.LabelFrame(char_frame, text="Attribute", padding="5")
        attr_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        for i, (stat, var) in enumerate(self.stats_vars.items()):
            ttk.Label(attr_frame, text=f"{stat}:").grid(row=i, column=0, sticky="w")
            ttk.Label(attr_frame, textvariable=var).grid(row=i, column=1, sticky="w", padx=5)

        # Resources Display
        resources_frame = ttk.LabelFrame(char_frame, text="Ressourcen", padding="5")
        resources_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        self.resources_label = ttk.Label(resources_frame, text="Noch keine Ressourcen gesammelt.")
        self.resources_label.pack(fill=tk.X, expand=True)


        progress_bars_data = [
            ("Lebenspunkte", "lp"),
            ("Manapunkte", "mp"),
            ("Energie", "energie"),
            ("Wut", "wut"),
            ("Erfahrung", "xp")
        ]

        for i, (text, var_name) in enumerate(progress_bars_data):
            frame = ttk.LabelFrame(char_frame, text=text, padding=5)
            # We will manage the grid position later
            setattr(self, f"{var_name}_frame", frame)

            bar = ttk.Progressbar(frame, orient='horizontal', mode='determinate')
            bar.pack(fill=tk.X, expand=True)
            label_var = getattr(self, f"{var_name}_label_var")
            ttk.Label(frame, textvariable=label_var, anchor="center").pack()
            setattr(self, f"{var_name}_bar", bar)

        # --- Right side: Portrait ---
        self.portrait_label = ttk.Label(char_frame)
        self.portrait_label.grid(row=0, column=2, rowspan=7, sticky="nsew", padx=(20, 0))

        try:
            if self.player.image_path:
                img = Image.open(self.player.image_path)
                img.thumbnail((220, 280))  # Resize image to fit
                photo_img = ImageTk.PhotoImage(img)

                self.portrait_label.config(image=photo_img)
                # Keep a reference to the image to prevent it from being garbage collected
                self.portrait_label.image = photo_img
        except FileNotFoundError:
            self.portrait_label.config(text=f"Bild nicht\ngefunden:\n{self.player.image_path}")
        except Exception as e:
            self.portrait_label.config(text=f"Fehler beim\nLaden des Bildes:\n{e}")

    def _create_actions_frame(self, parent):
        actions_frame = ttk.LabelFrame(parent, text="Aktionen", padding="10")
        actions_frame.pack(fill=tk.Y, expand=False, anchor='n')

        self.quest_button = ttk.Button(actions_frame, text="Neue Quest beginnen", command=self.start_quest)
        self.quest_button.pack(fill=tk.X, pady=5)
        self.auto_quest_button = ttk.Button(actions_frame, text="Auto-Quest starten", command=self.toggle_auto_quest)
        self.auto_quest_button.pack(fill=tk.X, pady=5)
        self.trader_button = ttk.Button(actions_frame, text="Händler besuchen", command=self.open_trader_window)
        self.trader_button.pack(fill=tk.X, pady=5)
        self.blacksmith_button = ttk.Button(actions_frame, text="Schmied besuchen", command=self.open_blacksmith_window)
        self.blacksmith_button.pack(fill=tk.X, pady=5)
        self.boss_arena_button = ttk.Button(actions_frame, text="Boss Arena", command=self.open_boss_arena_window)
        self.boss_arena_button.pack(fill=tk.X, pady=5)
        self.equip_button = ttk.Button(actions_frame, text="Gegenstand ausrüsten", command=self.equip_item)
        self.equip_button.pack(fill=tk.X, pady=5)
        self.use_button = ttk.Button(actions_frame, text="Gegenstand benutzen", command=self.use_item)
        self.use_button.pack(fill=tk.X, pady=5)
        self.progress_bar = ttk.Progressbar(actions_frame, orient='horizontal', mode='determinate', length=120)
        self.progress_bar.pack(fill=tk.X, pady=(10, 5))

        self.loot_status_text = tk.Text(actions_frame, height=2, wrap=tk.WORD, bg="lightgrey", relief="flat", fg="gray")
        self.loot_status_text.pack(fill=tk.X, pady=5)
        self.loot_status_text.config(state=tk.DISABLED)

        # Create a placeholder for the quest image to stabilize the layout
        self.placeholder_image = ImageTk.PhotoImage(Image.new('RGBA', (300, 200), (0, 0, 0, 0)))
        self.quest_image_label = ttk.Label(actions_frame, image=self.placeholder_image)
        self.quest_image_label.image = self.placeholder_image # Keep a reference
        self.quest_image_label.pack(pady=10)


        # Minigame Canvas
        minigame_frame = ttk.LabelFrame(actions_frame, text="Ressourcenjagd", padding="5")
        minigame_frame.pack(fill=tk.X, pady=(10, 0), expand=True)

        self.minigame_toggle_button = ttk.Button(minigame_frame, text="Ressourcenjagd starten", command=self.toggle_minigame)
        self.minigame_toggle_button.pack(fill=tk.X, pady=(0, 5))

        self.minigame_canvas = tk.Canvas(minigame_frame, width=240, height=300, relief="sunken", borderwidth=1)
        self.minigame_canvas.pack(expand=True, fill=tk.BOTH)
        self.minigame_canvas.bind("<Configure>", self._resize_minigame_background)

        try:
            # Load the original background image. It will be resized and drawn by the event handler.
            # Store the original PIL image to use for resizing later.
            self.minigame_bg_img_original_pil = Image.open("assets/minigame_background.png")
        except FileNotFoundError:
            self.minigame_bg_img_original_pil = None
            self.minigame_canvas.config(bg="grey") # Fallback color


    def _create_log_frame(self, parent):
        """Creates the quest log text widget."""
        log_labelframe = ttk.LabelFrame(parent, text="Log", padding="10")
        log_labelframe.pack(fill=tk.X, expand=True)

        log_labelframe.rowconfigure(0, weight=1)
        log_labelframe.columnconfigure(0, weight=1)

        self.quest_log = tk.Text(log_labelframe, height=10, wrap=tk.WORD, bg="#2B2B2B", fg="white", relief="flat")
        self.quest_log.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(log_labelframe, orient=tk.VERTICAL, command=self.quest_log.yview)
        self.quest_log.config(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.quest_log.config(state=tk.DISABLED)

    def _resize_minigame_background(self, event):
        """Resizes and redraws the minigame background image to fit the canvas."""
        if self.minigame_bg_img_original_pil:
            # Resize the original image to the new canvas size
            resized_pil = self.minigame_bg_img_original_pil.resize((event.width, event.height))
            # Convert to PhotoImage. Important: keep a reference!
            self.minigame_bg_img = ImageTk.PhotoImage(resized_pil)
            # Redraw the image on the canvas
            self.minigame_canvas.create_image(0, 0, image=self.minigame_bg_img, anchor='nw')

    def _create_equipment_frame(self, parent):
        parent.columnconfigure(1, weight=1)
        equip_frame = ttk.LabelFrame(parent, text="Angelegte Ausrüstung", padding="10")
        equip_frame.pack(fill=tk.X, padx=10, pady=10)
        for i, (slot, var) in enumerate(self.equipment_vars.items()):
            ttk.Label(equip_frame, text=f"{slot}:").grid(row=i, column=0, sticky="w")
            ttk.Label(equip_frame, textvariable=var).grid(row=i, column=1, sticky="w", padx=5)

    def _create_inventory_frame(self, parent):
        parent.rowconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)
        self.inv_frame = ttk.LabelFrame(parent, text="Rucksack", padding="10")
        self.inv_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.inv_frame.rowconfigure(0, weight=1)
        self.inv_frame.columnconfigure(0, weight=1)
        self.inventory_listbox = tk.Listbox(self.inv_frame, bg="#2B2B2B", fg="white", selectbackground="#0078D7")
        self.inventory_listbox.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(self.inv_frame, orient=tk.VERTICAL, command=self.inventory_listbox.yview)
        self.inventory_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.inventory_listbox.bind('<<ListboxSelect>>', self.update_button_states)
        self.inventory_listbox.bind('<Double-1>', self.on_item_double_click)

        self.tooltip = Tooltip(self.inventory_listbox, self.get_tooltip_text)

    def get_tooltip_text(self):
        """Callback function to get the text for the tooltip."""
        try:
            # Get the item under the mouse cursor
            _, y, _, _ = self.inventory_listbox.bbox(self.inventory_listbox.curselection()[0])
            index = self.inventory_listbox.nearest(y)
            item = self.player.inventory[index]

            # Format the text
            text = f"{item.name}\n"
            text += f"Typ: {item.item_type} ({item.slot})\n"
            text += f"Wert: {format_currency(item.value)}\n\n"
            for stat, value in item.stats_boost.items():
                text += f"{stat}: +{value}\n"
            return text.strip()
        except (IndexError, tk.TclError):
            return ""

    def update_display(self):
        self.char_name_var.set(f"{self.player.name} ({self.player.klasse})")
        self.char_level_var.set(self.player.level)
        self.item_level_var.set(self.player.get_item_level())
        self.char_gold_var.set(format_currency(self.player.copper))
        total_stats = self.player.get_total_stats()
        for stat, var in self.stats_vars.items():
            base = self.player.attributes.get(stat, 0)
            total = total_stats.get(stat, 0)
            bonus = total - base
            var.set(f"{total} ({base} {'+' if bonus >= 0 else ''}{bonus})") if bonus != 0 else var.set(total)
        for slot, var in self.equipment_vars.items():
            item = self.player.equipment.get(slot)
            var.set(item.name if item else "Leer")
        self.inv_frame.config(text=f"Inventar ({len(self.player.inventory)}/{self.player.max_inventory_size})")
        self.inventory_listbox.delete(0, tk.END)
        for i, item in enumerate(self.player.inventory):
            item_text = str(item)
            if self.player.is_upgrade(item):
                item_text = "⭐ " + item_text
            self.inventory_listbox.insert(tk.END, item_text)
            self.inventory_listbox.itemconfig(i, {'fg': item.color})

        self.lp_label_var.set(f"{self.player.current_lp} / {self.player.max_lp} LP")
        self.lp_bar['value'] = (self.player.current_lp / self.player.max_lp) * 100 if self.player.max_lp > 0 else 0
        self.mp_label_var.set(f"{self.player.current_mp} / {self.player.max_mp} MP")
        self.mp_bar['value'] = (self.player.current_mp / self.player.max_mp) * 100 if self.player.max_mp > 0 else 0
        self.xp_label_var.set(f"{self.player.xp} / {self.player.xp_to_next_level} XP")
        self.xp_bar['value'] = (self.player.xp / self.player.xp_to_next_level) * 100 if self.player.xp_to_next_level > 0 else 0

        # Dynamically display the correct resource bar based on class
        self.mp_frame.grid_remove()
        self.energie_frame.grid_remove()
        self.wut_frame.grid_remove()

        if self.player.klasse == "Schurke":
            self.energie_label_var.set(f"{self.player.current_energie} / {self.player.max_energie} Energie")
            self.energie_bar['value'] = (self.player.current_energie / self.player.max_energie) * 100 if self.player.max_energie > 0 else 0
            self.energie_frame.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(5, 0))
        elif self.player.klasse == "Krieger":
            self.wut_label_var.set(f"{self.player.current_wut} / {self.player.max_wut} Wut")
            self.wut_bar['value'] = (self.player.current_wut / self.player.max_wut) * 100 if self.player.max_wut > 0 else 0
            self.wut_frame.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(5, 0))
        else: # Default to Mana for Magier and any other future classes
            self.mp_frame.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(5, 0))

        # Place the static bars
        self.lp_frame.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(5, 0))
        self.xp_frame.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(5, 0))


        # Update resources display
        if not self.player.resources:
            self.resources_label.config(text="Noch keine Ressourcen gesammelt.")
        else:
            resources_text = "\n".join([f"{name}: {amount}" for name, amount in self.player.resources.items()])
            self.resources_label.config(text=resources_text)

        self.update_button_states()
        self.update_idletasks()

    def clear_log(self):
        """Clears the quest log."""
        self.quest_log.config(state=tk.NORMAL)
        self.quest_log.delete("1.0", tk.END)
        self.quest_log.config(state=tk.DISABLED)

    def show_paused_messagebox(self, title, message, **kwargs):
        """Shows a messagebox while pausing the quest loop."""
        self.pause_quest_loop()
        messagebox.showinfo(title, message, **kwargs)
        self.resume_quest_loop()

    def add_to_log(self, message):
        self.quest_log.config(state=tk.NORMAL)
        self.quest_log.insert(tk.END, message + "\n")
        self.quest_log.see(tk.END)
        self.quest_log.config(state=tk.DISABLED)

    def set_loot_text(self, text):
        self.loot_status_text.config(state=tk.NORMAL)
        self.loot_status_text.delete("1.0", tk.END)
        self.loot_status_text.insert("1.0", text)
        self.loot_status_text.config(state=tk.DISABLED)

    def toggle_auto_quest(self):
        self.is_auto_questing = not self.is_auto_questing
        if self.is_auto_questing:
            self.auto_quest_button.config(text="Auto-Quest stoppen")
            self.set_loot_text("Auto-Quest Modus aktiv...")
            self.start_quest()
        else:
            self.auto_quest_button.config(text="Auto-Quest starten")
            self.set_loot_text("Auto-Quest Modus gestoppt.")

    def toggle_minigame(self):
        """Starts or stops the resource hunt minigame."""
        self.minigame_running = not self.minigame_running
        if self.minigame_running:
            self.minigame_toggle_button.config(text="Ressourcenjagd beenden")
            # Reset spawn timer to spawn an orb relatively quickly
            self.last_orb_spawn_time = 0
            self.next_orb_spawn_delay = random.uniform(0.5, 1.5)
            self.run_minigame_loop() # Start the independent loop
        else:
            self.minigame_toggle_button.config(text="Ressourcenjagd starten")
            # Stop the independent loop
            if self.minigame_loop_id:
                self.master.after_cancel(self.minigame_loop_id)
                self.minigame_loop_id = None
            # Clear existing orbs
            for orb_id in list(self.minigame_orbs.keys()):
                self.minigame_canvas.delete(orb_id)
            self.minigame_orbs.clear()

    def run_minigame_loop(self):
        """The main loop for the minigame, independent of the quest loop."""
        self.update_minigame()
        self.minigame_loop_id = self.master.after(150, self.run_minigame_loop)

    def start_quest(self):
        if self.current_quest:
            if not self.is_auto_questing:
                messagebox.showwarning("Quest aktiv", "Bitte schließe erst die aktuelle Quest ab.")
            return
        if len(self.player.inventory) >= self.player.max_inventory_size:
            self.set_loot_text("Inventar voll! Auto-Quest gestoppt.")
            # Use the paused messagebox
            self.show_paused_messagebox("Inventar voll", "Dein Inventar ist voll. Besuche den Händler!")
            if self.is_auto_questing:
                self.toggle_auto_quest()
            return

        selected_quest = random.choice(AVAILABLE_QUESTS)
        quest_name = selected_quest["name"]
        quest_image_path = selected_quest["image"]

        try:
            img = Image.open(quest_image_path)
            img.thumbnail((300, 200))
            photo_img = ImageTk.PhotoImage(img)
            self.quest_image_label.config(image=photo_img)
            self.quest_image_label.image = photo_img
        except Exception as e:
            self.quest_image_label.config(image=None, text=f"Bildfehler:\n{e}")
            self.quest_image_label.image = None

        self.current_quest = Quest(quest_name)
        # Clear log for the new quest and show the first phase text
        self.clear_log()
        self.add_to_log(self.current_quest.travel_text)
        self.progress_bar['value'] = 0
        self.update_display()
        self.advance_quest()

    def update_minigame(self):
        # Stop minigame updates if it's not supposed to be running
        if not self.minigame_running:
            return

        now = time.time()
        # Remove old orbs
        orbs_to_remove = []
        for orb_id, orb_data in self.minigame_orbs.items():
            if now - orb_data['spawn_time'] > orb_data['lifespan']:
                self.minigame_canvas.delete(orb_id)
                orbs_to_remove.append(orb_id)
        for orb_id in orbs_to_remove:
            del self.minigame_orbs[orb_id]

        # Spawn new orbs
        if now - self.last_orb_spawn_time > self.next_orb_spawn_delay:
            canvas_width = self.minigame_canvas.winfo_width()
            canvas_height = self.minigame_canvas.winfo_height()

            if canvas_width > 1 and canvas_height > 1: # Ensure canvas is rendered
                x = random.randint(10, canvas_width - 10)
                y = random.randint(10, canvas_height - 10)

                # Determine resource type and symbol
                if random.random() < 0.8:
                    resource_type = "Eisenerz"
                    symbol = "🪨"
                else:
                    resource_type = "Juwel"
                    symbol = "💎"

                # Create a text item on the canvas
                orb_id = self.minigame_canvas.create_text(x, y, text=symbol, font=("", 14))

                # Bind click event
                self.minigame_canvas.tag_bind(orb_id, "<Button-1>", lambda event, o_id=orb_id: self.on_orb_click(o_id))

                self.minigame_orbs[orb_id] = {
                    'spawn_time': now,
                    'lifespan': random.uniform(2, 3),
                    'resource': resource_type
                }
                self.last_orb_spawn_time = now
                self.next_orb_spawn_delay = random.uniform(2, 5)

    def on_orb_click(self, orb_id):
        """Handles the click on a resource orb with a zoom-pulse animation."""
        if orb_id in self.minigame_orbs:
            resource_data = self.minigame_orbs.pop(orb_id)
            self.player.add_resource(resource_data['resource'], 1)

            # --- New Zoom-Pulse Animation ---
            start_time = time.time()
            duration = 0.3  # 300ms animation
            initial_font_size = 14
            max_font_size = 24

            def pulse_step():
                elapsed = time.time() - start_time
                progress = min(elapsed / duration, 1.0)

                # Go from initial to max size in the first half, then back down
                if progress < 0.5:
                    size_progress = progress * 2
                else:
                    size_progress = (1 - progress) * 2

                current_size = int(initial_font_size + (max_font_size - initial_font_size) * size_progress)

                try:
                    self.minigame_canvas.itemconfig(orb_id, font=("", current_size))
                except tk.TclError:
                    # Orb might have been deleted if another function cleared it, just stop.
                    return

                if progress < 1.0:
                    self.after(15, pulse_step)
                else:
                    # Animation finished, now delete the orb and update the UI
                    try:
                        self.minigame_canvas.delete(orb_id)
                    except tk.TclError:
                        pass # Ignore if already gone
                    self.update_display()

            pulse_step()


    def advance_quest(self):
        if self.current_quest is None: return

        old_phase = self.current_quest.phase
        event_message = self.current_quest.advance(self.player)
        new_phase = self.current_quest.phase

        # Display the static phase text only when the phase changes
        if new_phase != old_phase:
            if new_phase == "Aktion":
                self.add_to_log(self.current_quest.action_text)
            elif new_phase == "Rückkehr":
                self.add_to_log(self.current_quest.return_text)

        # Log intermittent action messages
        if event_message:
            self.add_to_log(event_message)

        if self.player.current_lp <= 0:
            self.handle_game_over(death_by_boss=False)
            return
        if self.player.current_lp / self.player.max_lp < 0.1:
            if self.is_auto_questing:
                self.toggle_auto_quest()
                messagebox.showwarning("Niedrige Lebenspunkte!", "Deine Lebenspunkte sind kritisch niedrig! Auto-Quest pausiert. Heile dich!")
        if self.current_quest.is_complete():
            gold, xp, item = self.current_quest.generate_reward(self.player)
            loot_status, received_item = self.player.add_loot(gold, item)
            level_up_info = self.player.add_xp(xp)

            loot_message = f"Loot: {format_currency(gold)}, {xp} XP"
            if received_item:
                if loot_status == "added":
                    loot_message += f" und '{received_item.name}'"
                elif loot_status == "inventory_full":
                    loot_message += f" (aber '{received_item.name}' passte nicht ins Inventar!)"
                elif loot_status == "auto_sold":
                    loot_message += f" und '{received_item.name}' (automatisch verkauft für {format_currency(received_item.value)})"
                elif loot_status == "auto_equipped":
                     # The message is already in pending_unlock_messages, just update the loot text
                    loot_message += f" und '{received_item.name}' (automatisch ausgerüstet!)"

            self.set_loot_text(loot_message)

            # Display any new messages from auto-equipping
            if self.player.pending_unlock_messages:
                for msg in self.player.pending_unlock_messages:
                    self.add_to_log(msg) # Add to log without popup
                self.player.pending_unlock_messages = []


            if level_up_info:
                self.pause_quest_loop()
                level_up_summary = f"Level Up! Du bist jetzt Level {self.player.level}!\n\nAttribut-Boni:\n" + "\n".join(level_up_info)
                CountdownDialog(self, title="Level Aufstieg!", message=level_up_summary, on_close_callback=self.resume_quest_loop)
            self.current_quest = None
            self.progress_bar['value'] = 0

            # Bild nach Quest-Abschluss auf Platzhalter zurücksetzen
            self.quest_image_label.config(image=self.placeholder_image)
            self.quest_image_label.image = self.placeholder_image

            if self.is_auto_questing:
                self.master.after(1000, self.start_quest)
        else:
            progress_percent = (self.current_quest.progress / self.current_quest.duration) * 100
            self.progress_bar['value'] = progress_percent
            self.quest_loop_id = self.master.after(150, self.advance_quest)
        self.update_display()

    def pause_quest_loop(self):
        """Pauses the quest advancement loop."""
        if self.quest_loop_id:
            self.master.after_cancel(self.quest_loop_id)
            self.quest_loop_id = None

    def resume_quest_loop(self):
        """Resumes the quest advancement loop if a quest is active."""
        if self.current_quest and not self.quest_loop_id:
            self.advance_quest()

    def equip_item(self):
        selected_indices = self.inventory_listbox.curselection()
        if not selected_indices: return
        item_index = selected_indices[0]
        self.player.equip(item_index, is_auto_equip=False) # Manual equip is not auto
        self.update_display()

    def use_item(self):
        selected_indices = self.inventory_listbox.curselection()
        if not selected_indices: return
        item_index = selected_indices[0]
        success, message = self.player.use_item(item_index)
        if not success:
            messagebox.showwarning("Fehler", message)
        self.update_display()

    def on_item_double_click(self, event=None):
        """Handles double-click events on the inventory listbox."""
        selected_indices = self.inventory_listbox.curselection()
        if not selected_indices:
            return

        item_index = selected_indices[0]
        selected_item = self.player.inventory[item_index]

        if selected_item.item_type == "Ausrüstung":
            self.equip_item()
        elif selected_item.item_type == "Verbrauchsgut":
            self.use_item()

    def update_button_states(self, event=None):
        is_questing = self.current_quest is not None
        selected_indices = self.inventory_listbox.curselection()
        self.quest_button.config(state=tk.DISABLED if is_questing else tk.NORMAL)
        self.trader_button.config(state=tk.DISABLED if is_questing else tk.NORMAL)
        self.blacksmith_button.config(state=tk.DISABLED if is_questing else tk.NORMAL)
        self.auto_quest_button.config(state=tk.DISABLED if is_questing and not self.is_auto_questing else tk.NORMAL)

        # Boss button logic
        can_fight_boss = False
        if not is_questing:
            current_tier = self.player.boss_tier
            if current_tier < len(BOSS_TIERS):
                required_ilvl = BOSS_TIERS[current_tier]["required_item_level"]
                if self.player.get_item_level() >= required_ilvl:
                    can_fight_boss = True
        self.boss_arena_button.config(state=tk.NORMAL if can_fight_boss else tk.DISABLED)
        self.minigame_toggle_button.config(state=tk.NORMAL) # Keep the button always enabled
        if not selected_indices:
            self.equip_button.config(state=tk.DISABLED)
            self.use_button.config(state=tk.DISABLED)
            return
        item_index = selected_indices[0]
        selected_item = self.player.inventory[item_index]
        if selected_item.item_type == "Ausrüstung":
            self.equip_button.config(state=tk.NORMAL)
            self.use_button.config(state=tk.DISABLED)
        elif selected_item.item_type == "Verbrauchsgut":
            self.equip_button.config(state=tk.DISABLED)
            self.use_button.config(state=tk.NORMAL)
        else:
            self.equip_button.config(state=tk.DISABLED)
            self.use_button.config(state=tk.DISABLED)

    def open_trader_window(self):
        self.trader_button.config(state=tk.DISABLED)
        TraderWindow(self, self.player, self.trader, on_close_callback=self.on_trader_close)

    def on_trader_close(self):
        self.update_display()
        self.trader_button.config(state=tk.NORMAL)

    def open_blacksmith_window(self):
        self.blacksmith_button.config(state=tk.DISABLED)
        BlacksmithWindow(self, self.player, on_close_callback=self.on_blacksmith_close)

    def on_blacksmith_close(self):
        self.update_display()
        self.blacksmith_button.config(state=tk.NORMAL)

    def open_boss_arena_window(self):
        self.pause_quest_loop()
        current_tier = self.player.boss_tier
        if current_tier >= len(BOSS_TIERS):
            messagebox.showinfo("Glückwunsch!", "Du hast bereits alle verfügbaren Bosse besiegt!", parent=self)
            self.resume_quest_loop()
            return

        boss_data = BOSS_TIERS[current_tier]
        # Use BASE item level for scaling the boss to ignore blacksmith upgrades
        base_player_ilvl = self.player.get_base_item_level()
        actual_player_ilvl = self.player.get_item_level() # For display and passing to the arena window

        # Create a temporary boss instance to get scaled stats
        temp_boss = Boss(
            name=boss_data["name"],
            hp=boss_data["hp"],
            damage_range=boss_data["damage"],
            image_path=boss_data["image_path"],
            item_level=base_player_ilvl # Scale boss based on non-upgraded gear
        )

        # Get player combat stats for comparison
        player_stats = self.player.get_total_stats()
        main_stat_val = player_stats.get(self.player.main_stat, 0)
        min_damage = main_stat_val // 2
        max_damage = main_stat_val

        title = "Warnung"
        message = (
            f"Du bist dabei, {temp_boss.name} (Stufe {actual_player_ilvl}) herauszufordern.\n\n"
            "--- Werte des Bosses ---\n"
            f"Lebenspunkte: {temp_boss.max_hp}\n"
            f"Schaden: {temp_boss.damage_range[0]} - {temp_boss.damage_range[1]}\n\n"
            "--- Deine Werte ---\n"
            f"Lebenspunkte: {self.player.current_lp} / {self.player.max_lp}\n"
            f"Schaden: {min_damage} - {max_damage}\n\n"
            "Der Kampf kann nicht abgebrochen werden und die Gefahr des Todes ist sehr hoch.\n\n"
            "Möchtest du fortfahren?"
        )

        if messagebox.askyesno(title, message, parent=self):
            self.boss_arena_button.config(state=tk.DISABLED)
            BossArenaWindow(self, self.player, boss_data, base_player_ilvl, on_close_callback=self.on_boss_arena_close, rebirths=self.player.rebirths)
        else:
            self.resume_quest_loop()

    def on_boss_arena_close(self):
        self.update_display()

        # Check for game over condition immediately after the fight
        if self.player.current_lp <= 0:
            self.handle_game_over(death_by_boss=True) # Pass the cause of death
            return # Stop further processing

        self.resume_quest_loop()
        self.update_button_states()

    def handle_game_over(self):
        self.game_over = True

        # Save the character's score before showing the game over screen
        save_highscore(self.player)

        try:
            img = Image.open("assets/grabstein.png")
            img.thumbnail((220, 280))
            photo_img = ImageTk.PhotoImage(img)

            self.portrait_label.config(image=photo_img)
            self.portrait_label.image = photo_img
        except FileNotFoundError:
            self.portrait_label.config(text="Game Over\n(Grabstein nicht gefunden)")

        # Disable all action buttons
        for button in [self.quest_button, self.auto_quest_button, self.trader_button, self.equip_button, self.use_button]:
            button.config(state=tk.DISABLED)

        # Show the custom game over window
        GameOverWindow(self, self.player, on_close_callback=lambda: self.callbacks['game_over'](death_by_boss=False))

    def handle_game_over(self, death_by_boss=False):
        self.game_over = True

        # Save the character's score before showing the game over screen
        save_highscore(self.player)

        try:
            img = Image.open("assets/grabstein.png")
            img.thumbnail((220, 280))
            photo_img = ImageTk.PhotoImage(img)

            self.portrait_label.config(image=photo_img)
            self.portrait_label.image = photo_img
        except FileNotFoundError:
            self.portrait_label.config(text="Game Over\n(Grabstein nicht gefunden)")

        # Disable all action buttons
        for button in [self.quest_button, self.auto_quest_button, self.trader_button, self.equip_button, self.use_button]:
            button.config(state=tk.DISABLED)

        # Show the custom game over window, passing the death cause
        GameOverWindow(self, self.player, on_close_callback=lambda: self.callbacks['game_over'](death_by_boss=death_by_boss), death_by_boss=death_by_boss)

    def _handle_keypress(self, event):
        """Handles key presses to check for cheat codes."""
        self.cheat_buffer += event.char
        # Keep the buffer trimmed to the length of the cheat code
        if len(self.cheat_buffer) > len(self.cheat_code):
            self.cheat_buffer = self.cheat_buffer[-len(self.cheat_code):]

        if self.cheat_buffer == self.cheat_code:
            # Toggle immortality
            self.player.is_immortal = not self.player.is_immortal

            if self.player.is_immortal:
                # If cheat is now active, also set the permanent flag
                self.player.cheat_activated = True
                self.add_to_log("CHEAT AKTIVIERT: Unsterblichkeit!")
            else:
                self.add_to_log("CHEAT DEAKTIVIERT: Sterblichkeit wiederhergestellt.")

            self.cheat_buffer = "" # Reset buffer after activation


class Tooltip:
    """
    Create a tooltip for a given widget.
    """
    def __init__(self, widget, text_callback):
        self.widget = widget
        self.text_callback = text_callback
        self.tip_window = None
        self.id = None
        self.x = self.y = 0
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<Motion>", self.motion)

    def enter(self, event=None):
        # Store the mouse position
        self.x = event.x_root
        self.y = event.y_root
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def motion(self, event=None):
        # Update the mouse position
        self.x = event.x_root
        self.y = event.y_root
        # If the tooltip is already visible, move it
        if self.tip_window:
            self.tip_window.wm_geometry(f"+{self.x + 25}+{self.y + 20}")

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(500, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self):
        text = self.text_callback()
        if not text:
            return

        # Use the stored mouse coordinates
        x = self.x + 25
        y = self.y + 20

        # Create the tooltip window if it doesn't exist
        if self.tip_window is None:
            self.tip_window = tk.Toplevel(self.widget)
            self.tip_window.wm_overrideredirect(True)
            label = tk.Label(self.tip_window, text=text, justify=tk.LEFT,
                             background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                             font=("tahoma", "8", "normal"))
            label.pack(ipadx=1)

        self.tip_window.wm_geometry(f"+{x}+{y}")

    def hidetip(self):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()

class CountdownDialog(tk.Toplevel):
    """A modal dialog with a countdown timer that closes automatically."""
    def __init__(self, parent, title, message, countdown=5, on_close_callback=None):
        super().__init__(parent)
        self.title(title)
        self.message = message
        self.countdown = countdown
        self.parent = parent
        self.on_close_callback = on_close_callback

        # Make window modal
        self.transient(parent)
        self.grab_set()

        # UI Elements
        ttk.Label(self, text=self.message, wraplength=300, justify=tk.LEFT).pack(padx=20, pady=10)

        self.countdown_label = ttk.Label(self, text=f"Schließt in {self.countdown} Sekunden...")
        self.countdown_label.pack(pady=5)

        ok_button = ttk.Button(self, text="OK", command=self.destroy)
        ok_button.pack(pady=10, padx=20, fill=tk.X)

        self.protocol("WM_DELETE_WINDOW", self.destroy)

        # Start the countdown
        self.update_countdown()

        # Center the window over its parent
        center_window(self, self.parent.winfo_toplevel())

    def update_countdown(self):
        if self.countdown > 0:
            self.countdown_label.config(text=f"Schließt in {self.countdown} Sekunden...")
            self.countdown -= 1
            self._after_id = self.after(1000, self.update_countdown)
        else:
            self.destroy()

    def destroy(self):
        # Cancel the pending `after` call before destroying the window
        if hasattr(self, '_after_id'):
            self.after_cancel(self._after_id)

        if self.on_close_callback:
            self.on_close_callback()

        super().destroy()
