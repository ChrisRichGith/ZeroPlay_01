# item.py
"""
Defines the Item class for all in-game items.
"""
from utils import format_currency
from game_data import ITEM_ICONS, RARITIES
from translations import get_text

class Item:
    """Represents an item with localizable name, type, value, and effects."""

    def __init__(self, name_key, gender, item_type="equipment", slot=None,
                 stats_boost=None, value=0, rarity_key="common", armor_type=None, is_boss_item=False):
        """
        Initializes an Item using localization keys.
        """
        self.name_key = name_key
        self.gender = gender
        self.item_type = item_type
        self.slot = slot
        self.armor_type = armor_type
        self.base_stats = stats_boost if stats_boost else {}
        self.base_value = value
        self.rarity_key = rarity_key
        self.upgrade_level = 0
        self.color = RARITIES[rarity_key].get("color", "#FFFFFF")
        self.is_boss_item_flag = is_boss_item

        self.icon = "❔"
        if self.item_type == "equipment" and self.slot:
            self.icon = ITEM_ICONS.get(self.slot, "❔")
        elif self.item_type == "consumable":
            self.icon = ITEM_ICONS.get("consumable", "❔")

        self.stats_boost = {}
        self.value = 0
        self.update_upgraded_state()

    def get_name(self, lang):
        """Returns the translated name based on the language."""
        base_name = get_text(lang, self.name_key)

        # Add "Boss" prefix if it's a boss item
        if self.is_boss_item():
            boss_prefix = get_text(lang, "boss") # "Boss" or "Boss"
            base_name = f"{boss_prefix} {base_name}"

        if self.upgrade_level > 0:
            return f"{base_name} +{self.upgrade_level}"
        return base_name

    def __str__(self):
        """Returns a string representation of the item for a default language."""
        return self.to_string("de") # Default to German for simple print()

    def to_string(self, lang):
        """Returns a fully translated string representation of the item."""
        value_str = format_currency(self.value)
        display_name = f"{self.icon} {self.get_name(lang)}"

        if self.item_type == "equipment":
            boosts = []
            if self.stats_boost:
                for stat, val in self.stats_boost.items():
                    translated_stat = get_text(lang, stat)
                    boosts.append(f"{'+' if val >= 0 else ''}{val} {translated_stat}")
            boost_str = ", ".join(boosts)
            translated_slot = get_text(lang, self.slot)
            return f"{display_name} ({translated_slot}) [{boost_str}] - {value_str}"

        elif self.item_type == "consumable":
            # Consumable effects are stored in base_stats and don't change
            effect = list(self.base_stats.keys())[0] # e.g., 'LP'
            val = list(self.base_stats.values())[0]
            effect_str = get_text(lang, "consumable_effect", value=val, effect=effect)
            return f"{display_name} [{effect_str}] - {value_str}"

        return f"{display_name} - {value_str}"


    def update_upgraded_state(self):
        """Calculates and sets the item's stats and value based on its upgrade level."""
        if self.item_type == "equipment":
            self.stats_boost = {}
            for stat, base_value in self.base_stats.items():
                self.stats_boost[stat] = base_value + self.upgrade_level
        else:
            self.stats_boost = self.base_stats.copy()

        self.value = int(self.base_value * (1 + self.upgrade_level * 0.5))

    def upgrade(self):
        """Increases the item's upgrade level by 1 if not at max."""
        if self.item_type != "equipment":
            return False

        max_upgrades = RARITIES[self.rarity_key].get("max_upgrades", 0)
        if self.upgrade_level >= max_upgrades:
            return False

        self.upgrade_level += 1
        self.update_upgraded_state()
        return True

    def get_weighted_score(self, main_stat, main_stat_weight=1.5):
        """Calculates a weighted score for an item based on a main stat."""
        if not self.stats_boost:
            return 0

        score = 0
        for stat, value in self.stats_boost.items():
            score += value * main_stat_weight if stat == main_stat else value
        return score

    def get_item_score(self):
        """Calculates a single 'item level' score based on total stats and rarity."""
        if not self.stats_boost or self.item_type != "equipment":
            return 0

        total_stats = sum(self.stats_boost.values())
        rarity_modifier = RARITIES[self.rarity_key].get("modifier", 1.0)

        score = total_stats * (rarity_modifier ** 2)
        return int(score)

    def is_boss_item(self):
        """Checks if the item is a designated boss item."""
        return self.is_boss_item_flag

    def get_base_item_score(self):
        """Calculates 'item level' based on BASE stats, ignoring upgrades."""
        if not self.base_stats or self.item_type != "equipment":
            return 0

        total_stats = sum(self.base_stats.values())
        rarity_modifier = RARITIES[self.rarity_key].get("modifier", 1.0)

        score = total_stats * (rarity_modifier ** 2)
        return int(score)
