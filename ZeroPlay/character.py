# character.py
"""
Defines the Character class, which manages the player's stats, inventory, and equipment.
"""
import random
from item import Item
from game_data import CLASSES

class Character:
    """Manages character attributes, inventory, and equipment."""

    def __init__(self, name, klasse):
        """
        Initializes a new character.

        Args:
            name (str): The character's name.
            klasse (str): The character's class.
        """
        self.name = name
        self.klasse = klasse
        self.level = 1
        self.xp = 0
        self.xp_to_next_level = 100
        self.copper = 0
        # Load base attributes and image path from the selected class
        class_data = CLASSES.get(klasse, {})
        self.attributes = class_data.get("attributes", {'Stärke': 5, 'Agilität': 5, 'Intelligenz': 5, 'Glück': 5}).copy()
        self.main_stat = class_data.get("main_stat") # Assign main_stat
        self.image_path = class_data.get("image_path", None)  # Store the image path
        self.inventory = []
        self.max_inventory_size = 10
        self.equipment = {'Kopf': None, 'Brust': None, 'Waffe': None}
        self.resources = {}
        self.boss_tier = 0
        self.bosses_defeated = 0
        self.autosell_unlocked_notified = False
        self.cheat_activated = False # Flag for highscore
        self.is_immortal = False

        # Derived stats
        self.max_lp = 0
        self.current_lp = 0
        self.max_mp = 0
        self.current_mp = 0
        self.max_energie = 0
        self.current_energie = 0
        self.max_wut = 0
        self.current_wut = 0
        self.update_derived_stats(heal_on_update=True) # Initial calculation and full heal

    def get_allowed_armor_types(self):
        """Returns a list of armor types the character's class can wear."""
        return CLASSES[self.klasse].get("allowed_armor", [])

    def update_derived_stats(self, heal_on_update=False):
        """
        Calculates derived stats like LP and MP based on base attributes.
        Does not heal the character unless specified (e.g., on level up).
        """
        total_stats = self.get_total_stats()

        self.max_lp = 50 + total_stats['Stärke'] * 5
        self.max_mp = 30 + total_stats['Intelligenz'] * 3

        # Energie is only for Schurke
        if self.klasse == "Schurke":
            self.max_energie = 50 + total_stats['Agilität'] * 5
        else:
            self.max_energie = 0

        if self.klasse == "Krieger":
            self.max_wut = 30 + total_stats['Stärke'] * 3
        else:
            self.max_wut = 0

        # Keep current values unless they exceed the new max
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

        Returns:
            list: A list of strings describing the attribute increases on level up, or empty list.
        """
        self.xp += amount
        level_up_messages = []
        while self.xp >= self.xp_to_next_level:
            self.xp -= self.xp_to_next_level
            level_up_messages.extend(self.level_up())
        return level_up_messages

    def level_up(self):
        """Handles the character's level up process."""
        self.level += 1
        self.xp_to_next_level = self._calculate_xp_for_next_level()

        stat_increases = []
        # Increase 1 to 2 random stats
        stats_to_increase = random.sample(list(self.attributes.keys()), k=random.randint(1, 2))
        for stat in stats_to_increase:
            increase = random.randint(1, 2)
            self.attributes[stat] += increase
            stat_increases.append(f"{stat} +{increase}")

        self.update_derived_stats(heal_on_update=True) # Recalculate LP/MP and heal on level up
        return stat_increases

    def use_item(self, item_index):
        """Uses a consumable item from the inventory."""
        if not (0 <= item_index < len(self.inventory)):
            return False, "Ungültiger Gegenstand."

        item = self.inventory[item_index]
        if item.item_type != "Verbrauchsgut":
            return False, "Dieser Gegenstand kann nicht benutzt werden."

        effect = item.stats_boost
        if "LP" in effect:
            self.current_lp = min(self.max_lp, self.current_lp + effect["LP"])
        if "MP" in effect:
            self.current_mp = min(self.max_mp, self.current_mp + effect["MP"])
        if "Energie" in effect:
            self.current_energie = min(self.max_energie, self.current_energie + effect["Energie"])
        if "Wut" in effect:
            self.current_wut = min(self.max_wut, self.current_wut + effect["Wut"])

        self.inventory.pop(item_index)
        return True, f"{item.name} benutzt."

    def take_damage(self, damage):
        """Reduces the character's HP by a given amount."""
        if self.is_immortal:
            return  # Don't take any damage if immortal
        self.current_lp -= damage
        if self.current_lp < 0:
            self.current_lp = 0

    def add_loot(self, copper, item):
        """
        Adds copper and an item to the character's inventory if there is space.
        Also handles auto-selling of non-upgrade items if inventory size is >= 50.

        Returns:
            tuple: A tuple containing a status string and the item object (or None).
        """
        self.copper += copper

        if item:
            # Check for auto-sell condition
            if self.max_inventory_size >= 50 and item.item_type == "Ausrüstung" and not self.is_upgrade(item):
                self.copper += item.value
                return "auto_sold", item

            # Default behavior: add to inventory if space is available
            if len(self.inventory) < self.max_inventory_size:
                self.inventory.append(item)
                return "added", item
            else:
                return "inventory_full", item

        return "no_item", None

    def add_resource(self, resource_name, amount):
        """Adds a specified amount of a resource to the character."""
        if resource_name in self.resources:
            self.resources[resource_name] += amount
        else:
            self.resources[resource_name] = amount

    def add_cheat_resources(self):
        """Adds 100 of each resource for testing and flags the character."""
        self.cheat_activated = True
        self.add_resource("Eisenerz", 100)
        self.add_resource("Juwel", 100)

    def remove_resources(self, cost):
        """
        Removes resources from the character's inventory based on a cost dictionary.
        Assumes the check for affordability has already been made.
        """
        for resource, amount in cost.items():
            if resource in self.resources:
                self.resources[resource] -= amount
                if self.resources[resource] <= 0:
                    del self.resources[resource]

    def is_upgrade(self, item_from_inventory):
        """
        Checks if an item in the inventory is an upgrade over the equipped item.

        Args:
            item_from_inventory (Item): The item to check.

        Returns:
            bool: True if the item is an upgrade, False otherwise.
        """
        # Rule 1: Must be equippable by the character's class
        if item_from_inventory.armor_type:
            allowed_armor = CLASSES[self.klasse].get("allowed_armor", [])
            if item_from_inventory.armor_type not in allowed_armor:
                return False

        if item_from_inventory.item_type != "Ausrüstung":
            return False

        equipped_item = self.equipment.get(item_from_inventory.slot)
        main_stat = CLASSES[self.klasse]['main_stat']

        if not equipped_item:
            # Any item is an upgrade if the slot is empty, provided it has a positive score
            return item_from_inventory.get_weighted_score(main_stat) > 0

        # Compare the weighted scores
        new_item_score = item_from_inventory.get_weighted_score(main_stat)
        equipped_item_score = equipped_item.get_weighted_score(main_stat)

        return new_item_score > equipped_item_score

    def equip(self, item_index):
        """
        Equips an item from the inventory.

        Args:
            item_index (int): The index of the item in the inventory.
        """
        if 0 <= item_index < len(self.inventory):
            item_to_equip = self.inventory[item_index]

            # Check for armor type restriction
            if item_to_equip.armor_type:
                allowed_armor = CLASSES[self.klasse].get("allowed_armor", [])
                if item_to_equip.armor_type not in allowed_armor:
                    # In a real GUI, we would show a message. For now, just prevent equipping.
                    print(f"Deine Klasse ({self.klasse}) kann '{item_to_equip.armor_type}' nicht tragen.")
                    return

            slot = item_to_equip.slot
            if slot in self.equipment:
                if self.equipment[slot]:
                    self.inventory.append(self.equipment[slot])

                self.equipment[slot] = item_to_equip
                self.inventory.pop(item_index)
                self.update_derived_stats()

    def get_total_stats(self):
        """
        Calculates total stats including bonuses from equipped items.

        Returns:
            dict: A dictionary with the total stats.
        """
        total_stats = self.attributes.copy()
        for slot, item in self.equipment.items():
            if item:
                for stat, boost in item.stats_boost.items():
                    if stat in total_stats:
                        total_stats[stat] += boost
        return total_stats

    def get_item_level(self):
        """Calculates the average item score of all equipped gear."""
        total_score = 0
        equipped_items = 0
        for item in self.equipment.values():
            if item:
                total_score += item.get_item_score()
                equipped_items += 1

        if equipped_items == 0:
            return 0
        return total_score // equipped_items

    def get_base_item_level(self):
        """
        Calculates the average item score of equipped gear based on BASE stats,
        ignoring blacksmith upgrades.
        """
        total_score = 0
        equipped_items = 0
        for item in self.equipment.values():
            if item:
                total_score += item.get_base_item_score()
                equipped_items += 1

        if equipped_items == 0:
            return 0
        return total_score // equipped_items

    def display_status(self):
        """DEPRECATED: Prints a detailed status screen for the character."""
        # This method is no longer used by the GUI but kept for potential CLI debugging.
        total_stats = self.get_total_stats()
        print("\n--- CHARAKTERSTATUS ---")
        print(f"Name: {self.name}, Klasse: {self.klasse}, Level: {self.level}")
        print(f"LP: {self.current_lp}/{self.max_lp} | MP: {self.current_mp}/{self.max_mp}")
        print(f"XP: {self.xp}/{self.xp_to_next_level}")
        print(f"Gold: {self.copper}")
        print("\nAttribute:")
        for stat, value in total_stats.items():
            base_value = self.attributes.get(stat, 0)
            bonus = value - base_value
            if bonus > 0:
                print(f"  - {stat}: {value} ({base_value} + {bonus})")
            else:
                print(f"  - {stat}: {value}")

        print("\nAusrüstung:")
        for slot, item in self.equipment.items():
            item_name = item.name if item else "Leer"
            print(f"  - {slot}: {item_name}")

        print("\nInventar:")
        if self.inventory:
            for i, item in enumerate(self.inventory):
                print(f"  {i}: {item}")
        else:
            print("  - Leer")
        print("-----------------------\n")
