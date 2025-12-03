# save_load_system.py
"""
Handles saving and loading of game states using pickle.
"""
import os
import pickle
from game_data import CLASSES

SAVE_DIR = "saves"

def save_game(character):
    """
    Saves the character object to a file.

    Args:
        character (Character): The character object to save.
    """
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    filename = os.path.join(SAVE_DIR, f"{character.name}.sav")
    try:
        with open(filename, 'wb') as f:
            pickle.dump(character, f)
        print(f"Spielstand für {character.name} gespeichert.")
    except Exception as e:
        print(f"Fehler beim Speichern von {character.name}: {e}")

def load_game(character_name):
    """
    Loads a character object from a file.

    Args:
        character_name (str): The name of the character to load.

    Returns:
        Character: The loaded character object, or None if not found.
    """
    filename = os.path.join(SAVE_DIR, f"{character_name}.sav")
    if os.path.exists(filename):
        try:
            with open(filename, 'rb') as f:
                character = pickle.load(f)
                # Compatibility check for old saves
                if not hasattr(character, 'resources'):
                    character.resources = {}
                if not hasattr(character, 'main_stat'):
                    character.main_stat = CLASSES.get(character.klasse, {}).get("main_stat")
                return character
        except Exception as e:
            print(f"Fehler beim Laden von {character_name}: {e}")
            return None
    return None

def get_save_files():
    """
    Gets a list of all available save file character names.

    Returns:
        list: A list of strings with character names.
    """
    if not os.path.exists(SAVE_DIR):
        return []

    save_files = [f.replace(".sav", "") for f in os.listdir(SAVE_DIR) if f.endswith(".sav")]
    return save_files
