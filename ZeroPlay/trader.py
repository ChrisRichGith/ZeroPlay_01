# trader.py
"""
Defines the Trader class for handling item selling and inventory upgrades.
"""
from item import Item
from game_data import POTIONS

class Trader:
    """Manages all trading-related logic."""

    def __init__(self):
        """Initializes the trader."""
        self.inventory_upgrade_cost = 1000 # Start cost: 10 silver
        self.upgrade_cost_increase_factor = 1.8

    def get_potions_for_sale(self, character):
        """Returns a list of potions available based on character level and class."""
        available_potions = []
        char_level = character.level
        char_class = character.klasse

        # Determine which potion types are relevant for the class
        relevant_types = ["LP"] # Health potions are for everyone
        if char_class == "Magier":
            relevant_types.append("MP")
        elif char_class == "Schurke":
            relevant_types.append("Energie")
        elif char_class == "Krieger":
            relevant_types.append("Wut")

        for data in POTIONS:
            if char_level >= data["level_req"] and data["type"] in relevant_types:
                potion = Item(
                    name=data["name"],
                    item_type="Verbrauchsgut",
                    stats_boost={data["type"]: data["value"]},
                    value=data["cost"]
                )
                available_potions.append(potion)
        return available_potions

    def sell_item(self, character, item_index):
        """
        Sells an item from the character's inventory.

        Args:
            character (Character): The player character.
            item_index (int): The index of the item to sell.

        Returns:
            bool: True if the sale was successful, False otherwise.
        """
        if 0 <= item_index < len(character.inventory):
            item_to_sell = character.inventory.pop(item_index)
            character.copper += item_to_sell.value
            return True
        return False

    def get_upgrade_cost(self):
        """Returns the current cost for the next inventory upgrade."""
        return self.inventory_upgrade_cost

    def buy_inventory_upgrade(self, character):
        """
        Upgrades the character's inventory size if they have enough gold.

        Args:
            character (Character): The player character.

        Returns:
            bool: True if the upgrade was successful, False otherwise.
        """
        if character.copper >= self.inventory_upgrade_cost:
            character.copper -= self.inventory_upgrade_cost
            character.max_inventory_size += 5  # Increase inventory by 5 slots

            # Increase the cost for the next upgrade
            self.inventory_upgrade_cost = int(self.inventory_upgrade_cost * self.upgrade_cost_increase_factor)
            return True
        return False

    def sell_all_non_upgrades(self, character):
        """
        Sells all items that are not considered an upgrade.

        Args:
            character (Character): The player character.

        Returns:
            tuple: A tuple containing the number of items sold and the total gold gained.
        """
        items_to_sell = [
            item for item in character.inventory
            if item.item_type == "Ausrüstung" and not character.is_upgrade(item)
        ]

        items_sold_count = len(items_to_sell)
        copper_gained = 0

        if not items_to_sell:
            return 0, 0

        for item in items_to_sell:
            copper_gained += item.value
            character.inventory.remove(item)

        character.copper += copper_gained
        return items_sold_count, copper_gained

    def buy_item(self, character, item_to_buy):
        """
        Allows the character to buy an item from the trader.

        Args:
            character (Character): The player character.
            item_to_buy (Item): The item instance to be bought.

        Returns:
            bool: True if the purchase was successful, False otherwise.
        """
        if len(character.inventory) >= character.max_inventory_size:
            return False, "Inventar ist voll."

        if character.copper < item_to_buy.value:
            return False, "Nicht genug Münzen."

        character.copper -= item_to_buy.value
        character.inventory.append(item_to_buy)
        return True, f"{item_to_buy.name} gekauft."
