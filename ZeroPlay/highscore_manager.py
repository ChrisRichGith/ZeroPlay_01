# highscore_manager.py
"""
Handles saving and loading of high scores.
"""
import json
import os

HIGHSCORE_FILE = "highscores.json"

def load_highscores():
    """
    Loads the high scores from the JSON file.

    Returns:
        list: A list of high score dictionaries, sorted by level.
              Returns an empty list if the file doesn't exist.
    """
    if not os.path.exists(HIGHSCORE_FILE):
        return []
    try:
        with open(HIGHSCORE_FILE, 'r', encoding='utf-8') as f:
            scores = json.load(f)
            # Sort scores by level in descending order
            scores.sort(key=lambda x: x.get('level', 0), reverse=True)
            return scores
    except (json.JSONDecodeError, IOError):
        return []

def save_highscore(character):
    """
    Saves a character's stats to the high score list.

    Args:
        character (Character): The character object whose stats to save.
    """
    scores = load_highscores()

    # Extract best equipment names
    best_weapon = character.equipment.get('Waffe').name if character.equipment.get('Waffe') else "Nichts"
    best_head = character.equipment.get('Kopf').name if character.equipment.get('Kopf') else "Nichts"
    best_chest = character.equipment.get('Brust').name if character.equipment.get('Brust') else "Nichts"

    new_score = {
        "name": character.name,
        "klasse": character.klasse,
        "level": character.level,
        "copper": character.copper,
        "bosses_defeated": character.bosses_defeated,
        "resources": character.resources,
        "cheat_activated": character.cheat_activated,
        "best_weapon": best_weapon,
        "best_head": best_head,
        "best_chest": best_chest
    }

    scores.append(new_score)

    # Sort the scores by level in descending order
    scores.sort(key=lambda x: x.get('level', 0), reverse=True)

    # Keep only the top 10 scores
    top_scores = scores[:10]

    try:
        with open(HIGHSCORE_FILE, 'w', encoding='utf-8') as f:
            json.dump(top_scores, f, indent=4, ensure_ascii=False)
    except IOError as e:
        print(f"Fehler beim Speichern der Highscores: {e}")
