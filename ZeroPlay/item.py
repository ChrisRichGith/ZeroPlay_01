# item.py
"""
Defines the Item class for all in-game items.
"""
import random
from utils import format_currency
from game_data import ITEM_ICONS, RARITIES

class Item:
    """Represents an item in the game with a name, type, value, and potential effects."""

    def __init__(self, name, item_type="Ausrüstung", slot=None, stats_boost=None, value=0, rarity="Gewöhnlich", color="#ffffff", armor_type=None):
        """
        Initializes an Item.

        Args:
            name (str): The name of the item.
            item_type (str): The type of item ('Ausrüstung' or 'Verbrauchsgut').
            slot (str, optional): The equipment slot for 'Ausrüstung' type.
            stats_boost (dict, optional): Stat boosts or consumable effects (e.g., {'LP': 50}).
            value (int): The copper value of the item.
            rarity (str): The rarity of the item.
            color (str): The hex color code for the item's rarity.
            armor_type (str, optional): The type of armor, if applicable (e.g., 'Leder', 'Platte').
        """
        self.original_name = name
        self.item_type = item_type
        self.slot = slot
        self.armor_type = armor_type
        self.base_stats = stats_boost if stats_boost else {}
        self.base_value = value
        self.rarity = rarity
        self.color = color
        self.upgrade_level = 0

        # Assign an icon based on the item type/slot
        self.icon = "❔" # Default icon
        if self.item_type == "Ausrüstung" and self.slot:
            self.icon = ITEM_ICONS.get(self.slot, "❔")
        elif self.item_type == "Verbrauchsgut":
            self.icon = ITEM_ICONS.get("Verbrauchsgut", "❔")

        # Set initial dynamic properties
        self.update_upgraded_state()


    def __str__(self):
        """Returns a string representation of the item, including its icon."""
        value_str = format_currency(self.value)
        # The name is now dynamic
        display_name = f"{self.icon} {self.name}"

        if self.item_type == "Ausrüstung":
            boosts = []
            if self.stats_boost:
                for stat, val in self.stats_boost.items():
                    boosts.append(f"{'+' if val >= 0 else ''}{val} {stat}")
            boost_str = ", ".join(boosts)
            return f"{display_name} ({self.slot}) [{boost_str}] - {value_str}"
        elif self.item_type == "Verbrauchsgut":
            effects = []
            # Consumables use base_stats as their effect doesn't change
            if self.base_stats:
                for stat, val in self.base_stats.items():
                    effects.append(f"Stellt {val} {stat} wieder her")
            effect_str = ", ".join(effects)
            return f"{display_name} [{effect_str}] - {value_str}"
        return f"{display_name} - {value_str}"

    def update_upgraded_state(self):
        """Calculates and sets the item's name, stats, and value based on its upgrade level."""
        # Update name
        if self.upgrade_level > 0:
            self.name = f"{self.original_name} +{self.upgrade_level}"
        else:
            self.name = self.original_name

        # Update stats
        if self.item_type == "Ausrüstung":
            self.stats_boost = {}
            for stat, base_value in self.base_stats.items():
                # Simple linear scaling: +1 to each stat per upgrade level for simplicity
                self.stats_boost[stat] = base_value + self.upgrade_level
        else:
            # Consumables do not get upgraded stats
            self.stats_boost = self.base_stats.copy()

        # Update value (e.g., increase by 50% of base value per level)
        self.value = int(self.base_value * (1 + self.upgrade_level * 0.5))

    def upgrade(self):
        """
        Increases the item's upgrade level by 1 if not at max.

        Returns:
            bool: True if the upgrade was successful, False otherwise.
        """
        if self.item_type != "Ausrüstung":
            return False

        max_upgrades = RARITIES[self.rarity].get("max_upgrades", 0)
        if self.upgrade_level >= max_upgrades:
            return False # Already at max level

        self.upgrade_level += 1
        self.update_upgraded_state()
        return True

    def get_weighted_score(self, main_stat, main_stat_weight=1.5):
        """
        Calculates a weighted score for an item based on a main stat.

        Args:
            main_stat (str): The primary stat for the character class.
            main_stat_weight (float): The multiplier for the main stat.

        Returns:
            float: The calculated weighted score of the item.
        """
        if not self.stats_boost:
            return 0

        score = 0
        for stat, value in self.stats_boost.items():
            if stat == main_stat:
                score += value * main_stat_weight
            else:
                score += value # Other stats have a weight of 1
        return score

    def get_item_score(self):
        """
        Calculates a single 'item level' score based on total stats and rarity.
        """
        if not self.stats_boost or self.item_type != "Ausrüstung":
            return 0

        total_stats = sum(self.stats_boost.values())
        rarity_modifier = RARITIES.get(self.rarity, {}).get("modifier", 1.0)

        # The score is the total stat points multiplied by the rarity modifier, squared to create a wider gap
        score = total_stats * (rarity_modifier ** 2)
        return int(score)

    def is_boss_item(self):
        """Checks if the item is a boss item by its name prefix."""
        return self.original_name.startswith("Boss ")

    def get_base_item_score(self):
        """
        Calculates a single 'item level' score based on BASE stats and rarity,
        ignoring any blacksmith upgrades.
        """
        if not self.base_stats or self.item_type != "Ausrüstung":
            return 0

        total_stats = sum(self.base_stats.values())
        rarity_modifier = RARITIES.get(self.rarity, {}).get("modifier", 1.0)

        # The score is the total stat points multiplied by the rarity modifier, squared to create a wider gap
        score = total_stats * (rarity_modifier ** 2)
        return int(score)
