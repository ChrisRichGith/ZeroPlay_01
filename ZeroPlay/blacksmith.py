# blacksmith.py
"""
Defines the Blacksmith class, which handles item upgrades.
"""

class Blacksmith:
    """Manages the logic for upgrading items."""

    def get_upgrade_cost(self, item):
        """
        Determines the cost to upgrade an item to the next level.

        Args:
            item (Item): The item to be upgraded.

        Returns:
            dict: A dictionary of resource names and the required amounts.
                  Returns None if the item cannot be upgraded.
        """
        if item.item_type != "Ausrüstung":
            return None

        next_level = item.upgrade_level + 1

        # Define cost based on the next level
        # This can be made more complex later (e.g., based on rarity)
        cost = {}
        if next_level <= 5:
            cost["Eisenerz"] = next_level * 5
        else:
            cost["Eisenerz"] = next_level * 5
            cost["Juwel"] = (next_level - 5) * 2

        return cost

    def can_afford_upgrade(self, player_resources, cost):
        """
        Checks if the player has enough resources to afford the upgrade.

        Args:
            player_resources (dict): The player's current resources.
            cost (dict): The cost of the upgrade.

        Returns:
            bool: True if the player can afford it, False otherwise.
        """
        for resource, amount in cost.items():
            if player_resources.get(resource, 0) < amount:
                return False
        return True

    def upgrade_item(self, player, item):
        """
        Attempts to upgrade an item for a player.

        Args:
            player (Character): The player character.
            item (Item): The item to upgrade.

        Returns:
            tuple: (bool, str) indicating success and a message.
        """
        cost = self.get_upgrade_cost(item)
        if not cost:
            return False, "Dieser Gegenstand kann nicht aufgewertet werden."

        if not self.can_afford_upgrade(player.resources, cost):
            return False, "Nicht genügend Ressourcen für die Aufwertung."

        # Attempt to upgrade the item
        if item.upgrade():
            player.remove_resources(cost)
            return True, f"{item.name} erfolgreich aufgewertet!"
        else:
            return False, "Gegenstand hat bereits die maximale Stufe erreicht."
