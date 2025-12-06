# boss.py
"""
Defines the Boss class for the RPG game.
"""
import random

class Boss:
    """Represents a boss enemy in the game."""

    def __init__(self, name, hp, damage_range, image_path, item_level=1, rebirths=0):
        """
        Initializes a new Boss, scaling its stats based on the player's item level
        and reducing them based on the number of rebirths.

        Args:
            name (str): The name of the boss.
            hp (int): The base health points of the boss.
            damage_range (tuple): A tuple containing the base min and max damage.
            image_path (str): The file path for the boss's image.
            item_level (int): The player's current item level, used for scaling.
            rebirths (int): The number of times the player has been reborn.
        """
        self.name = name
        self.image_path = image_path
        self.is_weakened = False

        # Step 1: Calculate the primary scaling based on item level
        item_scaling_factor = 1 + (item_level / 10) ** 1.2

        # Step 2: Calculate a reduction factor based on rebirths.
        # Each rebirth makes the boss 5% weaker, capped at 50% reduction.
        rebirth_reduction = min(0.5, rebirths * 0.05)
        final_scaling_factor = item_scaling_factor * (1 - rebirth_reduction)

        # Apply the final scaling factor to the boss's stats
        self.max_hp = int(hp * final_scaling_factor)
        self.current_hp = self.max_hp
        min_dmg, max_dmg = damage_range
        self.damage_range = (int(min_dmg * final_scaling_factor), int(max_dmg * final_scaling_factor))

    def attack(self):
        """
        Calculates the damage for the boss's attack.

        Returns:
            int: The amount of damage dealt.
        """
        return random.randint(*self.damage_range)

    def take_damage(self, damage):
        """
        Reduces the boss's HP by a given amount.
        If the boss is weakened, it takes increased damage.
        """
        final_damage = damage
        if self.is_weakened:
            final_damage = int(final_damage * 1.5)  # Take 50% more damage

        self.current_hp -= final_damage
        if self.current_hp < 0:
            self.current_hp = 0

    def is_defeated(self):
        """
        Checks if the boss has been defeated.

        Returns:
            bool: True if the boss's HP is 0, False otherwise.
        """
        return self.current_hp <= 0
