# quest.py
"""
Defines the Quest class, which handles quest progression and rewards.
"""
import random
import time
from item import Item
from loot_system import generate_item_for_level
from game_data import (
    CLASSES, WARRIOR_EVENTS, MAGE_EVENTS, ROGUE_EVENTS,
    QUEST_LOCATIONS, QUEST_ACTIONS_PREFIX, QUEST_RETURNS
)

class Quest:
    """Represents a quest that automatically progresses and grants rewards."""

    def __init__(self, description, duration=40):
        """
        Initializes a new quest.

        Args:
            description (str): The description of the quest.
            duration (int): The number of 'ticks' required to complete the quest.
        """
        self.description = description
        self.duration = duration
        self.progress = 0
        self.phase = "Anreise" # Anreise, Aktion, Rückkehr

        # Procedurally generate static phase texts
        self.generate_phase_texts()

    def is_complete(self):
        """Checks if the quest is complete."""
        return self.progress >= self.duration

    def advance(self, character):
        """
        Advances the quest progress and returns an event message.
        """
        if self.is_complete():
            return None

        # --- 1. Determine current phase ---
        phase_length = self.duration / 3
        if self.progress < phase_length:
            self.phase = "Anreise"
        elif self.progress < phase_length * 2:
            self.phase = "Aktion"
        else:
            self.phase = "Rückkehr"

        # --- 2. Calculate progress and consume resources ---
        main_stat = CLASSES[character.klasse]["main_stat"]
        stat_value = character.get_total_stats().get(main_stat, 5)
        progress_increase = 1 + (stat_value / 50.0)

        # Only consume resources during the 'Aktion' phase
        if self.phase == "Aktion":
            if character.klasse == "Magier":
                if character.current_mp > 0:
                    character.current_mp = max(0, character.current_mp - 2) # Higher cost for action
                else:
                    progress_increase *= 0.25
            elif character.klasse == "Schurke":
                if character.current_energie > 0:
                    character.current_energie = max(0, character.current_energie - 2)
                else:
                    progress_increase *= 0.25
            elif character.klasse == "Krieger":
                if character.current_wut > 0:
                    character.current_wut = max(0, character.current_wut - 2)
                else:
                    progress_increase *= 0.5

        self.progress += progress_increase

        # --- 3. Select event message based on phase and class ---
        event_message = None # By default, no message is generated

        # --- 4. Handle quest completion ---
        if self.is_complete():
            damage = random.randint(5, 15)
            # Use the take_damage method to respect immortality
            character.take_damage(damage)
            if not character.is_immortal:
                event_message = f"Quest abgeschlossen! Du hast {damage} Schaden erlitten."
            else:
                event_message = "Quest abgeschlossen! Dank deiner Unsterblichkeit hast du keinen Schaden erlitten."

        # Generate a class-specific action message, but less frequently
        if self.phase == "Aktion" and random.random() < 0.2: # 20% chance per tick
            if character.klasse == "Krieger":
                return random.choice(WARRIOR_EVENTS)
            elif character.klasse == "Magier":
                return random.choice(MAGE_EVENTS)
            elif character.klasse == "Schurke":
                return random.choice(ROGUE_EVENTS)

        # Return None most of the time to keep the log clean
        return None

    def generate_phase_texts(self):
        """Generates and stores the descriptive text for each quest phase."""
        location = random.choice(QUEST_LOCATIONS)
        action_prefix = random.choice(QUEST_ACTIONS_PREFIX)
        return_prefix = random.choice(QUEST_RETURNS)

        self.travel_text = f"Deine Quest führt dich {location}."
        self.action_text = f"{action_prefix} {self.description}."
        self.return_text = return_prefix

    def generate_reward(self, character):
        """
        Generates random gold, XP, and an item, influenced by character's luck.

        Args:
            character (Character): The character receiving the reward.

        Returns:
            tuple: A tuple containing gold, xp, and an Item object (or None).
        """
        luck_bonus = 1 + (character.get_total_stats()['Glück'] / 100) # e.g., 10 luck = 10% bonus

        copper_reward = int((random.randint(50, 250) + self.duration * 10) * luck_bonus)
        xp_reward = int((random.randint(20, 40) + self.duration * 2) * luck_bonus)

        # Luck also slightly increases the chance of finding an item
        item_chance = 0.7 + (character.get_total_stats()['Glück'] / 200) # 10 luck = +5% chance
        if random.random() < min(0.95, item_chance): # Cap at 95%
            item_reward = generate_item_for_level(character.level, character.get_total_stats()['Glück'])
        else:
            item_reward = None

        return copper_reward, xp_reward, item_reward
