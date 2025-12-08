# rpg_gui.py
"""
Defines the main game GUI frame.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import random
import time
from PIL import Image, ImageTk

from boss import Boss
from quest import Quest
from trader import Trader
from trader_gui import TraderWindow
from blacksmith_gui import BlacksmithWindow
from boss_arena_gui import BossArenaWindow
from utils import format_currency, center_window
from game_over_gui import GameOverWindow
from game_data import BOSS_TIERS, CLASSES
from translations import get_text

AVAILABLE_QUESTS = [
    {"name": "quest_slimes_name", "image": "assets/quests/kill_all_slimes.jpg"},
    {"name": "quest_iron_ore_name", "image": "assets/quests/bring_5_iron_ore_to_the_blacksmith.jpg"},
    {"name": "quest_princess_name", "image": "assets/quests/save_a_princess_from_another_castle.jpg"},
]

class RpgGui(ttk.Frame):
    """Manages the main game GUI frame."""

    def __init__(self, parent, character, callbacks, initial_messages=None, language="de"):
        super().__init__(parent)
        self.callbacks = callbacks
        self.language = language
        self.player = character
        self.player.language = language
        self.trader = Trader()
        self.current_quest = None
        self.is_auto_questing = False
        self.game_over = False
        self.quest_loop_id = None
        self.minigame_loop_id = None
        self.minigame_orbs = {}
        self.last_orb_spawn_time = 0
        self.next_orb_spawn_delay = random.uniform(2, 5)
        self.minigame_running = False
        self.typed_string = ""
        self.cheat_buffer = ""
        self.cheat_code = "ordilogicus"

        self.master.bind("<Key>", self.handle_keypress)
        self.master.bind("<Key>", self._handle_keypress, add="+")

        self._setup_string_vars()
        self.create_widgets()
        self.update_display()

        if initial_messages:
            for msg in initial_messages:
                self.show_unlock_message(msg)

    def _(self, key, **kwargs):
        return get_text(self.language, key, **kwargs)

    def show_unlock_message(self, message_key):
        if ":" in message_key:
            key, value = message_key.split(":", 1)
            message = self._(key, item_name=value)
        else:
            message = self._(message_key)

        self.add_to_log(f"⭐ {message} ⭐")
        messagebox.showinfo(self._("milestone_unlocked"), message, parent=self)

    def handle_keypress(self, event):
        self.typed_string += event.char.lower()
        self.typed_string = self.typed_string[-20:]
        if "showmethemoney" in self.typed_string:
            self.player.add_cheat_resources()
            self.set_loot_text(self._("cheat_resources_added"))
            self.update_display()
            self.typed_string = ""

    def _setup_string_vars(self):
        self.char_name_var = tk.StringVar()
        self.char_level_var = tk.StringVar()
        self.item_level_var = tk.StringVar()
        self.char_gold_var = tk.StringVar()
        self.stats_vars = {stat: tk.StringVar() for stat in ['strength', 'agility', 'intelligence', 'luck']}
        self.equipment_vars = {slot: tk.StringVar() for slot in ['head', 'chest', 'weapon']}
        self.lp_label_var = tk.StringVar()
        self.mp_label_var = tk.StringVar()
        self.xp_label_var = tk.StringVar()
        self.energie_label_var = tk.StringVar()
        self.wut_label_var = tk.StringVar()

    def create_widgets(self):
        self.columnconfigure(0, weight=1, uniform="char_inv_group")
        self.columnconfigure(1, weight=0)
        self.columnconfigure(2, weight=1, uniform="char_inv_group")
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)

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

        self._create_character_frame(char_frame_container)
        self._create_actions_frame(actions_frame)

        notebook = ttk.Notebook(inventory_frame)
        notebook.grid(row=0, column=0, sticky="nsew")
        equipment_tab = ttk.Frame(notebook)
        inventory_tab = ttk.Frame(notebook)
        notebook.add(equipment_tab, text=self._('equipment'))
        notebook.add(inventory_tab, text=self._('inventory'))

        self._create_equipment_frame(equipment_tab)
        self._create_inventory_frame(inventory_tab)
        self._create_log_frame(log_frame)

    def _create_character_frame(self, parent):
        char_frame = ttk.LabelFrame(parent, text=self._("char_status"), padding="10")
        char_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10), anchor='n')
        char_frame.columnconfigure(2, weight=1)

        labels = {"name": self.char_name_var, "level": self.char_level_var, "item_level": self.item_level_var, "gold": self.char_gold_var}
        for i, (key, var) in enumerate(labels.items()):
            ttk.Label(char_frame, text=f"{self._(key)}:").grid(row=i, column=0, sticky="w")
            ttk.Label(char_frame, textvariable=var).grid(row=i, column=1, sticky="w")

        attr_frame = ttk.LabelFrame(char_frame, text=self._("attributes"), padding="5")
        attr_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        self.stat_labels = {}
        for i, key in enumerate(self.stats_vars.keys()):
            self.stat_labels[key] = ttk.Label(attr_frame, text=f"{self._(key)}:")
            self.stat_labels[key].grid(row=i, column=0, sticky="w")
            ttk.Label(attr_frame, textvariable=self.stats_vars[key]).grid(row=i, column=1, sticky="w", padx=5)

        resources_frame = ttk.LabelFrame(char_frame, text=self._("resources"), padding="5")
        resources_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        self.resources_label = ttk.Label(resources_frame, text=self._("no_resources"))
        self.resources_label.pack(fill=tk.X, expand=True)

        progress_bars_data = [("life_points", "lp"), ("mana_points", "mp"), ("energy", "energie"), ("rage", "wut"), ("experience", "xp")]
        for text_key, var_name in progress_bars_data:
            frame = ttk.LabelFrame(char_frame, text=self._(text_key), padding=5)
            setattr(self, f"{var_name}_frame", frame)
            bar = ttk.Progressbar(frame, orient='horizontal', mode='determinate')
            bar.pack(fill=tk.X, expand=True)
            ttk.Label(frame, textvariable=getattr(self, f"{var_name}_label_var"), anchor="center").pack()
            setattr(self, f"{var_name}_bar", bar)

        self.portrait_label = ttk.Label(char_frame)
        self.portrait_label.grid(row=0, column=2, rowspan=7, sticky="nsew", padx=(20, 0))
        self.load_image(self.player.image_path, self.portrait_label, (220, 280))

    def _create_actions_frame(self, parent):
        actions_frame = ttk.LabelFrame(parent, text=self._("actions"), padding="10")
        actions_frame.pack(fill=tk.Y, expand=False, anchor='n')

        buttons = {
            "start_quest": self.start_quest, "start_auto_quest": self.toggle_auto_quest,
            "visit_trader": self.open_trader_window, "visit_blacksmith": self.open_blacksmith_window,
            "boss_arena": self.open_boss_arena_window, "equip_item": self.equip_item, "use_item": self.use_item
        }
        for key, cmd in buttons.items():
            button = ttk.Button(actions_frame, text=self._(key), command=cmd)
            button.pack(fill=tk.X, pady=5)
            setattr(self, f"{key.replace('visit_', '')}_button", button)

        self.progress_bar = ttk.Progressbar(actions_frame, orient='horizontal', mode='determinate', length=120)
        self.progress_bar.pack(fill=tk.X, pady=(10, 5))

        self.loot_status_text = tk.Text(actions_frame, height=2, wrap=tk.WORD, bg="lightgrey", relief="flat", fg="gray", state=tk.DISABLED)
        self.loot_status_text.pack(fill=tk.X, pady=5)

        self.quest_image_label = ttk.Label(actions_frame)
        self.quest_image_label.pack(pady=10)

        minigame_frame = ttk.LabelFrame(actions_frame, text=self._("resource_hunt"), padding="5")
        minigame_frame.pack(fill=tk.X, pady=(10, 0), expand=True)

        self.minigame_toggle_button = ttk.Button(minigame_frame, text=self._("start_resource_hunt"), command=self.toggle_minigame)
        self.minigame_toggle_button.pack(fill=tk.X, pady=(0, 5))

        self.minigame_canvas = tk.Canvas(minigame_frame, width=240, height=300, relief="sunken", borderwidth=1)
        self.minigame_canvas.pack(expand=True, fill=tk.BOTH)
        self.minigame_canvas.bind("<Configure>", self._resize_minigame_background)
        self.load_image("assets/minigame_background.png", self.minigame_canvas, is_background=True)

    def _create_log_frame(self, parent):
        log_labelframe = ttk.LabelFrame(parent, text=self._("log"), padding="10")
        log_labelframe.pack(fill=tk.X, expand=True)
        log_labelframe.rowconfigure(0, weight=1)
        log_labelframe.columnconfigure(0, weight=1)
        self.quest_log = tk.Text(log_labelframe, height=10, wrap=tk.WORD, bg="#2B2B2B", fg="white", relief="flat", state=tk.DISABLED)
        self.quest_log.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(log_labelframe, orient=tk.VERTICAL, command=self.quest_log.yview)
        self.quest_log.config(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

    def _resize_minigame_background(self, event):
        if hasattr(self, 'minigame_bg_img_original_pil'):
            resized_pil = self.minigame_bg_img_original_pil.resize((event.width, event.height))
            self.minigame_bg_img = ImageTk.PhotoImage(resized_pil)
            self.minigame_canvas.create_image(0, 0, image=self.minigame_bg_img, anchor='nw')

    def _create_equipment_frame(self, parent):
        parent.columnconfigure(1, weight=1)
        equip_frame = ttk.LabelFrame(parent, text=self._("equipped_gear"), padding="10")
        equip_frame.pack(fill=tk.X, padx=10, pady=10)
        self.slot_labels = {}
        for i, (slot, var) in enumerate(self.equipment_vars.items()):
            self.slot_labels[slot] = ttk.Label(equip_frame, text=f"{self._(slot)}:")
            self.slot_labels[slot].grid(row=i, column=0, sticky="w")
            ttk.Label(equip_frame, textvariable=var).grid(row=i, column=1, sticky="w", padx=5)

    def _create_inventory_frame(self, parent):
        parent.rowconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)
        self.inv_frame = ttk.LabelFrame(parent, text=self._("backpack"), padding="10")
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
        try:
            index = self.inventory_listbox.nearest(self.inventory_listbox.winfo_pointery() - self.inventory_listbox.winfo_rooty())
            item = self.player.inventory[index]
            item_type = self._(f"item_type_{item.item_type}")
            text = f"{item.get_name(self.language)}\n"
            text += self._("tooltip_type", item_type=item_type, slot=self._(item.slot)) + "\n"
            text += self._("tooltip_value", value=format_currency(item.value)) + "\n\n"
            for stat, value in item.stats_boost.items():
                text += f"{self._(stat)}: +{value}\n"
            return text.strip()
        except (IndexError, tk.TclError):
            return ""

    def update_display(self):
        class_name = self._(CLASSES[self.player.klasse]['name_key'])
        self.char_name_var.set(f"{self.player.name} ({class_name})")
        self.char_level_var.set(self.player.level)
        self.item_level_var.set(self.player.get_item_level())
        self.char_gold_var.set(format_currency(self.player.copper))
        total_stats = self.player.get_total_stats()

        for stat, label in self.stat_labels.items():
            label.config(text=f"{self._(stat)}:")
        for stat, var in self.stats_vars.items():
            base, total = self.player.attributes.get(stat, 0), total_stats.get(stat, 0)
            bonus = total - base
            var.set(f"{total} ({base} {'+' if bonus >= 0 else ''}{bonus})" if bonus != 0 else total)

        for slot, var in self.equipment_vars.items():
            item = self.player.equipment.get(slot)
            var.set(item.get_name(self.language) if item else self._("empty_slot"))
            self.slot_labels[slot].config(text=f"{self._(slot)}:")

        self.inv_frame.config(text=self._("inventory_count", current=len(self.player.inventory), max=self.player.max_inventory_size))
        self.inventory_listbox.delete(0, tk.END)
        for i, item in enumerate(self.player.inventory):
            item_text = item.to_string(self.language)
            self.inventory_listbox.insert(tk.END, f"⭐ {item_text}" if self.player.is_upgrade(item) else item_text)
            self.inventory_listbox.itemconfig(i, {'fg': item.color})

        self.update_progress_bars()
        self.update_resources_display()
        self.update_button_states()
        self.update_idletasks()

    def update_progress_bars(self):
        lp_val = (self.player.current_lp / self.player.max_lp) * 100 if self.player.max_lp > 0 else 0
        self.lp_label_var.set(f"{self.player.current_lp} / {self.player.max_lp} LP")
        self.lp_bar['value'] = lp_val

        xp_val = (self.player.xp / self.player.xp_to_next_level) * 100 if self.player.xp_to_next_level > 0 else 0
        self.xp_label_var.set(f"{self.player.xp} / {self.player.xp_to_next_level} XP")
        self.xp_bar['value'] = xp_val

        self.mp_frame.grid_remove()
        self.energie_frame.grid_remove()
        self.wut_frame.grid_remove()

        if self.player.klasse == "rogue":
            val = (self.player.current_energie / self.player.max_energie) * 100 if self.player.max_energie > 0 else 0
            self.energie_label_var.set(f"{self.player.current_energie} / {self.player.max_energie} {self._('energy')}")
            self.energie_bar['value'] = val
            self.energie_frame.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(5, 0))
        elif self.player.klasse == "warrior":
            val = (self.player.current_wut / self.player.max_wut) * 100 if self.player.max_wut > 0 else 0
            self.wut_label_var.set(f"{self.player.current_wut} / {self.player.max_wut} {self._('rage')}")
            self.wut_bar['value'] = val
            self.wut_frame.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(5, 0))
        else: # Mage
            val = (self.player.current_mp / self.player.max_mp) * 100 if self.player.max_mp > 0 else 0
            self.mp_label_var.set(f"{self.player.current_mp} / {self.player.max_mp} MP")
            self.mp_bar['value'] = val
            self.mp_frame.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(5, 0))

        self.lp_frame.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(5, 0))
        self.xp_frame.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(5, 0))

    def update_resources_display(self):
        if not self.player.resources:
            self.resources_label.config(text=self._("no_resources"))
        else:
            res_text = "\n".join([f"{self._('resource_' + key)}: {amount}" for key, amount in self.player.resources.items()])
            self.resources_label.config(text=res_text)

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
        self.auto_quest_button.config(text=self._("stop_auto_quest" if self.is_auto_questing else "start_auto_quest"))
        self.set_loot_text(self._("auto_quest_active" if self.is_auto_questing else "auto_quest_stopped"))
        if self.is_auto_questing: self.start_quest()

    def toggle_minigame(self):
        self.minigame_running = not self.minigame_running
        self.minigame_toggle_button.config(text=self._("stop_resource_hunt" if self.minigame_running else "start_resource_hunt"))
        if self.minigame_running:
            self.last_orb_spawn_time, self.next_orb_spawn_delay = 0, random.uniform(0.5, 1.5)
            self.run_minigame_loop()
        else:
            if self.minigame_loop_id: self.master.after_cancel(self.minigame_loop_id)
            for orb_id in list(self.minigame_orbs.keys()): self.minigame_canvas.delete(orb_id)
            self.minigame_orbs.clear()

    def run_minigame_loop(self):
        self.update_minigame()
        self.minigame_loop_id = self.master.after(150, self.run_minigame_loop)

    def start_quest(self):
        if self.current_quest:
            if not self.is_auto_questing: messagebox.showwarning(self._("quest_active"), self._("quest_active_msg"))
            return
        if len(self.player.inventory) >= self.player.max_inventory_size:
            self.set_loot_text(self._("inventory_full_auto_quest_stopped"))
            messagebox.showinfo(self._("inventory_full"), self._("inventory_full_msg"))
            if self.is_auto_questing: self.toggle_auto_quest()
            return

        quest_data = random.choice(AVAILABLE_QUESTS)
        self.load_image(quest_data["image"], self.quest_image_label, (300, 200))
        self.current_quest = Quest(self._(quest_data["name"]))
        self.quest_log.config(state=tk.NORMAL); self.quest_log.delete("1.0", tk.END); self.quest_log.config(state=tk.DISABLED)
        self.add_to_log(self.current_quest.travel_text)
        self.progress_bar['value'] = 0
        self.update_display()
        self.advance_quest()

    def update_minigame(self):
        if not self.minigame_running: return
        now = time.time()
        for orb_id in [oid for oid, data in self.minigame_orbs.items() if now - data['spawn_time'] > data['lifespan']]:
            self.minigame_canvas.delete(orb_id); del self.minigame_orbs[orb_id]

        if now - self.last_orb_spawn_time > self.next_orb_spawn_delay and self.minigame_canvas.winfo_width() > 1:
            x, y = random.randint(10, self.minigame_canvas.winfo_width() - 10), random.randint(10, self.minigame_canvas.winfo_height() - 10)
            res_key, symbol = ("iron_ore", "🪨") if random.random() < 0.8 else ("jewel", "💎")
            orb_id = self.minigame_canvas.create_text(x, y, text=symbol, font=("", 14))
            self.minigame_canvas.tag_bind(orb_id, "<Button-1>", lambda e, o=orb_id: self.on_orb_click(o))
            self.minigame_orbs[orb_id] = {'spawn_time': now, 'lifespan': random.uniform(2, 3), 'resource': res_key}
            self.last_orb_spawn_time, self.next_orb_spawn_delay = now, random.uniform(2, 5)

    def on_orb_click(self, orb_id):
        if orb_id not in self.minigame_orbs: return
        res_data = self.minigame_orbs.pop(orb_id)
        self.player.add_resource(res_data['resource'], 1)
        start_time, duration, i_size, m_size = time.time(), 0.3, 14, 24
        def pulse():
            elapsed, p = time.time() - start_time, min((time.time() - start_time) / duration, 1.0)
            size = int(i_size + (m_size - i_size) * (p*2 if p<0.5 else (1-p)*2))
            try: self.minigame_canvas.itemconfig(orb_id, font=("", size))
            except tk.TclError: return
            if p < 1.0: self.after(15, pulse)
            else:
                try: self.minigame_canvas.delete(orb_id)
                except tk.TclError: pass
                self.update_display()
        pulse()

    def advance_quest(self):
        if self.current_quest is None: return
        old_phase = self.current_quest.phase
        event_message = self.current_quest.advance(self.player)
        if self.current_quest.phase != old_phase and getattr(self.current_quest, self.current_quest.phase.lower() + "_text", ""):
            self.add_to_log(getattr(self.current_quest, self.current_quest.phase.lower() + "_text"))
        if event_message: self.add_to_log(event_message)

        if self.player.current_lp <= 0: self.handle_game_over(death_by_boss=False); return
        if self.player.current_lp / self.player.max_lp < 0.1 and self.is_auto_questing:
            self.toggle_auto_quest(); messagebox.showwarning(self._("low_health"), self._("low_health_msg"))

        if self.current_quest.is_complete():
            gold, xp, item = self.current_quest.generate_reward(self.player)
            status, rec_item = self.player.add_loot(gold, item)
            lvl_info = self.player.add_xp(xp)

            loot_msg = f"{self._('loot')}: {format_currency(gold)}, {xp} XP"
            if rec_item:
                rec_item_name = rec_item.get_name(self.language)
                if status == "added": loot_msg += f" {self._('and')} '{rec_item_name}'"
                elif status == "inventory_full": loot_msg += f" ({self._('but')} '{rec_item_name}' {self._('did_not_fit')})"
                elif status == "auto_sold": loot_msg += f" {self._('and')} '{rec_item_name}' ({self._('auto_sold_for')} {format_currency(rec_item.value)})"
                elif status == "auto_equipped": loot_msg += f" {self._('and')} '{rec_item_name}' ({self._('auto_equipped')})"
            self.set_loot_text(loot_msg)

            if lvl_info:
                self.pause_quest_loop()
                CountdownDialog(self, title=self._("level_up_title"),
                                message=self._("level_up_msg", level=self.player.level, bonuses="\n".join(lvl_info)),
                                on_close_callback=self.resume_quest_loop, language=self.language)

            self.current_quest = None
            self.progress_bar['value'] = 0
            self.load_image(None, self.quest_image_label) # Clear image
            if self.is_auto_questing: self.master.after(1000, self.start_quest)
        else:
            self.progress_bar['value'] = (self.current_quest.progress / self.current_quest.duration) * 100
            self.quest_loop_id = self.master.after(150, self.advance_quest)
        self.update_display()

    def pause_quest_loop(self):
        if self.quest_loop_id: self.master.after_cancel(self.quest_loop_id); self.quest_loop_id = None

    def resume_quest_loop(self):
        if self.current_quest and not self.quest_loop_id: self.advance_quest()

    def _manage_item(self, action):
        selected = self.inventory_listbox.curselection()
        if not selected: return
        success, message = action(selected[0])
        if not success: messagebox.showwarning(self._("error"), message, parent=self)
        self.update_display()

    def equip_item(self): self._manage_item(lambda i: self.player.equip(i) or (True, ""))
    def use_item(self): self._manage_item(self.player.use_item)
    def on_item_double_click(self, e=None):
        selected = self.inventory_listbox.curselection()
        if not selected: return
        item = self.player.inventory[selected[0]]
        if item.item_type == "equipment": self.equip_item()
        elif item.item_type == "consumable": self.use_item()

    def update_button_states(self, e=None):
        is_questing = self.current_quest is not None
        selected = self.inventory_listbox.curselection()
        self.quest_button.config(state=tk.DISABLED if is_questing else tk.NORMAL)
        self.trader_button.config(state=tk.DISABLED if is_questing else tk.NORMAL)
        self.blacksmith_button.config(state=tk.DISABLED if is_questing else tk.NORMAL)
        self.auto_quest_button.config(state=tk.DISABLED if is_questing and not self.is_auto_questing else tk.NORMAL)

        can_fight_boss = not is_questing and self.player.boss_tier < len(BOSS_TIERS) and \
                         self.player.get_item_level() >= BOSS_TIERS[self.player.boss_tier]["required_item_level"]
        self.boss_arena_button.config(state=tk.NORMAL if can_fight_boss else tk.DISABLED)

        if not selected:
            self.equip_button.config(state=tk.DISABLED); self.use_button.config(state=tk.DISABLED)
            return
        item = self.player.inventory[selected[0]]
        self.equip_button.config(state=tk.NORMAL if item.item_type == "equipment" else tk.DISABLED)
        self.use_button.config(state=tk.NORMAL if item.item_type == "consumable" else tk.DISABLED)

    def on_window_close(self, button, callback):
        callback()
        button.config(state=tk.NORMAL)

    def open_trader_window(self):
        self.trader_button.config(state=tk.DISABLED)
        TraderWindow(self, self.player, self.trader, on_close_callback=lambda: self.on_window_close(self.trader_button, self.update_display), language=self.language)

    def open_blacksmith_window(self):
        self.blacksmith_button.config(state=tk.DISABLED)
        BlacksmithWindow(self, self.player, on_close_callback=lambda: self.on_window_close(self.blacksmith_button, self.update_display), language=self.language)

    def open_boss_arena_window(self):
        self.pause_quest_loop()
        tier = self.player.boss_tier
        if tier >= len(BOSS_TIERS):
            messagebox.showinfo(self._("congratulations"), self._("all_bosses_defeated"), parent=self); self.resume_quest_loop(); return

        boss_data = BOSS_TIERS[tier]
        boss = Boss(boss_data["name_key"], boss_data["hp"], boss_data["damage"], boss_data["image_path"],
                    self.player.get_base_item_level(), self.player.rebirths)

        stats = self.player.get_total_stats(); main_stat = stats.get(self.player.main_stat, 0)
        msg = self._("boss_fight_warning", boss_name=boss.get_name(self.language), player_ilvl=self.player.get_item_level(),
                     boss_hp=boss.max_hp, boss_dmg_min=boss.damage_range[0], boss_dmg_max=boss.damage_range[1],
                     player_hp=self.player.current_lp, player_max_hp=self.player.max_lp,
                     player_dmg_min=main_stat // 2, player_dmg_max=main_stat)

        if messagebox.askyesno(self._("warning"), msg, parent=self):
            self.boss_arena_button.config(state=tk.DISABLED)
            BossArenaWindow(self, self.player, boss_data, on_close_callback=self.on_boss_arena_close, language=self.language)
        else:
            self.resume_quest_loop()

    def on_boss_arena_close(self):
        self.update_display()
        if self.player.current_lp <= 0: self.handle_game_over(death_by_boss=True); return
        self.resume_quest_loop(); self.update_button_states()

    def handle_game_over(self, death_by_boss=False):
        self.game_over = True
        save_highscore(self.player)
        self.load_image("assets/grabstein.png", self.portrait_label, (220, 280))
        for btn in [self.quest_button, self.auto_quest_button, self.trader_button, self.equip_button, self.use_button]:
            btn.config(state=tk.DISABLED)
        GameOverWindow(self, self.player, on_close_callback=lambda: self.callbacks['game_over'](death_by_boss=death_by_boss),
                       death_by_boss=death_by_boss, language=self.player.language)

    def _handle_keypress(self, event):
        self.cheat_buffer = (self.cheat_buffer + event.char)[-len(self.cheat_code):]
        if self.cheat_buffer == self.cheat_code:
            self.player.is_immortal = not self.player.is_immortal
            if self.player.is_immortal: self.player.cheat_activated = True
            self.add_to_log(self._(f"cheat_immortality_{'on' if self.player.is_immortal else 'off'}"))
            self.cheat_buffer = ""

    def load_image(self, path, widget, size=None, is_background=False):
        try:
            if not path:
                if hasattr(widget, 'placeholder_image'): widget.config(image=widget.placeholder_image)
                else: widget.config(image='')
                return
            img = Image.open(path)
            if size: img.thumbnail(size)

            if is_background:
                widget.minigame_bg_img_original_pil = img
                self._resize_minigame_background(tk.Event()) # Initial draw
            else:
                photo_img = ImageTk.PhotoImage(img)
                widget.config(image=photo_img)
                widget.image = photo_img
        except Exception as e:
            if not is_background: widget.config(text=self._("image_load_error", e=e), image='')


class Tooltip:
    def __init__(self, widget, text_callback):
        self.widget, self.text_callback, self.tip_window, self.id = widget, text_callback, None, None
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<Motion>", self.motion)

    def enter(self, event): self.schedule()
    def leave(self, event): self.unschedule(); self.hidetip()
    def motion(self, event):
        if self.tip_window: self.tip_window.wm_geometry(f"+{event.x_root + 25}+{event.y_root + 20}")

    def schedule(self): self.unschedule(); self.id = self.widget.after(500, self.showtip)
    def unschedule(self):
        if self.id: self.widget.after_cancel(self.id); self.id = None

    def showtip(self):
        text = self.text_callback()
        if not text or self.tip_window: return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True); tw.wm_geometry(f"+{x}+{y}")
        tk.Label(tw, text=text, justify=tk.LEFT, background="#ffffe0", relief=tk.SOLID, borderwidth=1).pack(ipadx=1)

    def hidetip(self):
        if self.tip_window: self.tip_window.destroy(); self.tip_window = None

class CountdownDialog(tk.Toplevel):
    def __init__(self, parent, title, message, countdown=5, on_close_callback=None, language="de"):
        super().__init__(parent)
        self.title(title); self.language = language; self.countdown = countdown; self.on_close_callback = on_close_callback
        self.transient(parent); self.grab_set()
        ttk.Label(self, text=message, wraplength=300, justify=tk.LEFT).pack(padx=20, pady=10)
        self.countdown_label = ttk.Label(self)
        self.countdown_label.pack(pady=5)
        ttk.Button(self, text=get_text(language, "ok"), command=self.destroy).pack(pady=10, padx=20, fill=tk.X)
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.update_countdown()
        center_window(self, parent.winfo_toplevel())

    def update_countdown(self):
        if self.countdown > 0:
            self.countdown_label.config(text=get_text(self.language, "countdown_closing_in", seconds=self.countdown))
            self.countdown -= 1
            self._after_id = self.after(1000, self.update_countdown)
        else: self.destroy()

    def destroy(self):
        if hasattr(self, '_after_id'): self.after_cancel(self._after_id)
        if self.on_close_callback: self.on_close_callback()
        super().destroy()
