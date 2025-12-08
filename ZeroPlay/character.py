# character.py
"""
Defines the Character class, which manages the player's stats, inventory, and equipment.
"""
import random
from item import Item
from game_data import CLASSES
from translations import get_text

class Character:
    """Manages character attributes, inventory, and equipment."""

    def __init__(self, name, klasse):
        """
        Initializes a new character.

        Args:
            name (str): The character's name.
            klasse (str): The character's class key (e.g., "warrior").
        """
        self.name = name
        self.klasse = klasse
        self.level = 1
        self.xp = 0
        self.xp_to_next_level = 100
        self.copper = 0

        class_data = CLASSES.get(klasse, {})
        self.base_attributes = class_data.get("attributes", {'strength': 5, 'agility': 5, 'intelligence': 5, 'luck': 5}).copy()
        self.attributes = self.base_attributes.copy()
        self.main_stat = class_data.get("main_stat")
        self.image_path = class_data.get("image_path", None)

        self.inventory = []
        self.max_inventory_size = 10
        self.equipment = {'head': None, 'chest': None, 'weapon': None}
        self.resources = {}
        self.boss_tier = 0
        self.bosses_defeated = 0
        self.rebirths = 0
        self.autosell_unlocked_notified = False
        self.keep_inventory_size_unlocked = False
        self.auto_equip_unlocked = False
        self.pending_unlock_messages = []
        self.cheat_activated = False
        self.is_immortal = False
        self.language = "de" # Default language, can be updated from outside

        self.max_lp = 0
        self.current_lp = 0
        self.max_mp = 0
        self.current_mp = 0
        self.max_energie = 0
        self.current_energie = 0
        self.max_wut = 0
        self.current_wut = 0
        self.update_derived_stats(heal_on_update=True)

    def get_allowed_armor_types(self):
        """Returns a list of armor types the character's class can wear."""
        return CLASSES[self.klasse].get("allowed_armor", [])

    def update_derived_stats(self, heal_on_update=False):
        """
        Calculates derived stats like LP and MP based on base attributes.
        """
        total_stats = self.get_total_stats()

        self.max_lp = 50 + total_stats['strength'] * 5
        self.max_mp = 30 + total_stats['intelligence'] * 3

        if self.klasse == "rogue":
            self.max_energie = 50 + total_stats['agility'] * 5
        else:
            self.max_energie = 0

        if self.klasse == "warrior":
            self.max_wut = 30 + total_stats['strength'] * 3
        else:
            self.max_wut = 0

        self.current_lp = min(self.current_lp, self.max_lp)
        self.current_mp = min(self.current_mp, self.max_mp)
        self.current_energie = min(self.current_energie, self.max_energie)
        self.current_wut = min(self.current_wut, self.max_wut)

        if heal_on_update:
            self.current_lp = self.max_lp
            self.current_mp = self.max_mp
            self.current_energie = self.max_energie
            self.current_wut = self.max_wut

    def _calculate_xp_for_next_level(self):
        """Calculates the XP needed for the next level."""
        return int(100 * (self.level ** 1.5))

    def add_xp(self, amount):
        """
        Adds XP to the character and checks for level ups.
        """
        self.xp += amount
        level_up_messages = []
        while self.xp >= self.xp_to_next_level:
            self.xp -= self.xp_to_next_level
            level_up_messages.extend(self.level_up())
        return level_up_messages

    def rebirth(self):
        """
        Resets the character to level 1 but with improved base stats.
        """
        self.rebirths += 1
        self.level = 1
        self.xp = 0
        self.xp_to_next_level = self._calculate_xp_for_next_level()
        self.copper = 0
        self.inventory = []
        self.equipment = {'head': None, 'chest': None, 'weapon': None}
        self.resources = {}
        self.boss_tier = 0

        if not self.keep_inventory_size_unlocked:
            self.max_inventory_size = 10

        if self.rebirths == 5 and not self.keep_inventory_size_unlocked:
            self.keep_inventory_size_unlocked = True
            self.pending_unlock_messages.append("milestone_inventory_unlocked")
        if self.rebirths == 10 and not self.auto_equip_unlocked:
            self.auto_equip_unlocked = True
            self.pending_unlock_messages.append("milestone_auto_equip_unlocked")

        for stat in self.base_attributes:
            increase = max(1, int(self.base_attributes[stat] * 0.10))
            self.base_attributes[stat] += increase

        self.attributes = self.base_attributes.copy()
        self.update_derived_stats(heal_on_update=True)

    def level_up(self):
        """Handles the character's level up process."""
        self.level += 1
        self.xp_to_next_level = self._calculate_xp_for_next_level()

        stat_increases = []
        stats_to_increase = random.sample(list(self.attributes.keys()), k=random.randint(1, 2))
        for stat in stats_to_increase:
            increase = random.randint(1, 2)
            self.attributes[stat] += increase
            stat_increases.append(f"{self._(stat)} +{increase}")

        self.update_derived_stats(heal_on_update=True)
        return stat_increases

    def _(self, key, **kwargs):
        """Alias for get_text for shorter calls, with formatting."""
        return get_text(self.language, key, **kwargs)

    def use_item(self, item_index):
        """Uses a consumable item from the inventory."""
        if not (0 <= item_index < len(self.inventory)):
            return False, self._("error_invalid_item")

        item = self.inventory[item_index]
        if item.item_type != "consumable":
            return False, self._("cannot_use_item")

        effect = item.stats_boost
        if "LP" in effect: self.current_lp = min(self.max_lp, self.current_lp + effect["LP"])
        if "MP" in effect: self.current_mp = min(self.max_mp, self.current_mp + effect["MP"])
        if "Energie" in effect: self.current_energie = min(self.max_energie, self.current_energie + effect["Energie"])
        if "Wut" in effect: self.current_wut = min(self.max_wut, self.current_wut + effect["Wut"])

        self.inventory.pop(item_index)
        return True, self._("item_used_success", item_name=item.get_name(self.language))

    def take_damage(self, damage):
        """Reduces the character's HP by a given amount."""
        if self.is_immortal:
            return
        self.current_lp -= damage
        if self.current_lp < 0:
            self.current_lp = 0

    def add_loot(self, copper, item):
        """
        Adds copper and an item to the character's inventory.
        Handles auto-selling and auto-equipping.
        """
        self.copper += copper
        if not item:
            return "no_item", None

        if self.auto_equip_unlocked and item.item_type == "equipment" and self.is_upgrade(item):
            self.inventory.append(item)
            self.equip(len(self.inventory) - 1, is_auto_equip=True)
            return "auto_equipped", item

        if self.max_inventory_size >= 50 and item.item_type == "equipment" and not self.is_upgrade(item):
            self.copper += item.value
            return "auto_sold", item

        if len(self.inventory) < self.max_inventory_size:
            self.inventory.append(item)
            return "added", item
        else:
            return "inventory_full", item

    def add_resource(self, resource_name, amount):
        """Adds a specified amount of a resource to the character."""
        self.resources[resource_name] = self.resources.get(resource_name, 0) + amount

    def add_cheat_resources(self):
        """Adds 100 of each resource for testing and flags the character."""
        self.cheat_activated = True
        self.add_resource("iron_ore", 100)
        self.add_resource("jewel", 100)

    def remove_resources(self, cost):
        """
        Removes resources from the character's inventory based on a cost dictionary.
        """
        for resource, amount in cost.items():
            if resource in self.resources:
                self.resources[resource] -= amount
                if self.resources[resource] <= 0:
                    del self.resources[resource]

    def is_upgrade(self, item_from_inventory):
        """
        Checks if an item in the inventory is an upgrade over the equipped item.
        """
        if item_from_inventory.armor_type:
            if item_from_inventory.armor_type not in self.get_allowed_armor_types():
                return False

        if item_from_inventory.item_type != "equipment":
            return False

        equipped_item = self.equipment.get(item_from_inventory.slot)
        main_stat = self.main_stat

        if not equipped_item:
            return item_from_inventory.get_weighted_score(main_stat) > 0

        new_item_score = item_from_inventory.get_weighted_score(main_stat)
        equipped_item_score = equipped_item.get_weighted_score(main_stat)
        return new_item_score > equipped_item_score

    def equip(self, item_index, is_auto_equip=False):
        """
        Equips an item from the inventory.
        """
        if not (0 <= item_index < len(self.inventory)):
            return

        item_to_equip = self.inventory[item_index]
        if item_to_equip.armor_type:
            if item_to_equip.armor_type not in self.get_allowed_armor_types():
                char_class_name = self._(CLASSES[self.klasse]['name_key'])
                armor_type_name = self._(f"armor_type_{item_to_equip.armor_type}")
                message = self._("error_class_cannot_wear", char_class=char_class_name, armor_type=armor_type_name)
                print(message) # Fallback for now
                return

        slot = item_to_equip.slot
        if slot in self.equipment:
            if self.equipment[slot]:
                self.inventory.append(self.equipment[slot])

            self.equipment[slot] = item_to_equip
            self.inventory.pop(item_index)
            self.update_derived_stats()

            if is_auto_equip:
                item_name = item_to_equip.get_name(self.language)
                self.pending_unlock_messages.append(f"auto_equip_notification:{item_name}")

    def get_total_stats(self):
        """
        Calculates total stats including bonuses from equipped items.
        """
        total_stats = self.attributes.copy()
        for item in self.equipment.values():
            if item:
                for stat, boost in item.stats_boost.items():
                    if stat in total_stats:
                        total_stats[stat] += boost
        return total_stats

    def get_item_level(self):
        """Calculates the average item score of all equipped gear."""
        total_score, equipped_items = 0, 0
        for item in self.equipment.values():
            if item:
                total_score += item.get_item_score()
                equipped_items += 1
        return total_score // equipped_items if equipped_items > 0 else 0

    def get_base_item_level(self):
        """
        Calculates the average item score of equipped gear based on BASE stats.
        """
        total_score, equipped_items = 0, 0
        for item in self.equipment.values():
            if item:
                total_score += item.get_base_item_score()
                equipped_items += 1
        return total_score // equipped_items if equipped_items > 0 else 0
