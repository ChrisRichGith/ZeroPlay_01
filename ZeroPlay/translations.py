# translations.py
"""
Centralized dictionary for all UI text translations.
"""

TEXTS = {
    "de": {
        # General
        "warning": "Warnung",
        "error": "Fehler",
        "ok": "OK",
        "close": "Schließen",
        "name": "Name",
        "level": "Level",
        "gold": "Gold",
        "strength": "Stärke",
        "intelligence": "Intelligenz",
        "luck": "Glück",
        "agility": "Agilität",

        # Splash Screen
        "splash_title": "Willkommen bei Chronicle of the Idle Hero!",
        "splash_objective_title": "Ziel des Spiels:",
        "splash_objective_text": "Werde stärker, besiege immer mächtigere Bosse und erklimme die Spitze der Highscore-Liste. Der Tod durch einen Boss ist nicht das Ende, sondern eine Wiedergeburt, die dich stärker macht. Aber sei gewarnt: Ein Scheitern bei einer normalen Quest führt zur endgültigen Löschung deines Helden!",
        "splash_controls_title": "Steuerung:",
        "splash_controls_text": "Das Spiel wird hauptsächlich mit der Maus bedient. Beginne Quests, besuche Händler und rüste Gegenstände aus, um dein Abenteuer voranzutreiben.",
        "continue": "Weiter",
        "language": "Sprache / Language",

        # Start Menu
        "start_menu_title": "Chronicle of the Idle Hero - Hauptmenü",
        "load_save": "Spielstand laden",
        "preview": "Vorschau",
        "load": "Laden",
        "new_game": "Neues Spiel",
        "highscores": "Highscores",
        "quit": "Beenden",
        "start_menu_intro": "Wähle einen Spielstand oder erstelle einen neuen Helden.\nAchtung: Tod bei einer Quest löscht den Spielstand!",

        # Class Selection
        "class_selection_title": "Charaktererstellung",
        "enter_name": "Gib deinen Namen ein:",
        "select_class": "Wähle deine Klasse:",
        "warrior": "Krieger",
        "mage": "Magier",
        "rogue": "Schurke",
        "confirm": "Bestätigen",
        "back": "Zurück",
        "warrior_desc": "Ein Meister des Nahkampfs, verlässt sich auf Stärke und Zähigkeit.",
        "mage_desc": "Ein Gelehrter der arkanen Künste, dessen Macht von seiner Intelligenz abhängt.",
        "rogue_desc": "Ein geschickter Halunke, der Agilität nutzt, um seine Feinde auszutricksen.",

        # RPG GUI (Main Game)
        "char_status": "Charakterstatus",
        "item_level": "Item Level",
        "attributes": "Attribute",
        "resources": "Ressourcen",
        "no_resources": "Noch keine Ressourcen gesammelt.",
        "life_points": "Lebenspunkte",
        "mana_points": "Manapunkte",
        "energy": "Energie",
        "rage": "Wut",
        "experience": "Erfahrung",
        "actions": "Aktionen",
        "start_quest": "Neue Quest beginnen",
        "start_auto_quest": "Auto-Quest starten",
        "stop_auto_quest": "Auto-Quest stoppen",
        "visit_trader": "Händler besuchen",
        "visit_blacksmith": "Schmied besuchen",
        "boss_arena": "Boss Arena",
        "equip_item": "Gegenstand ausrüsten",
        "use_item": "Gegenstand benutzen",
        "log": "Log",
        "equipment": "Ausrüstung",
        "inventory": "Inventar",
        "head": "Kopf",
        "chest": "Brust",
        "weapon": "Waffe",
        "empty_slot": "Leer",
        "quest_active": "Quest aktiv",
        "quest_active_msg": "Bitte schließe erst die aktuelle Quest ab.",
        "inventory_full": "Inventar voll",
        "inventory_full_msg": "Dein Inventar ist voll. Besuche den Händler!",
        "low_health": "Niedrige Lebenspunkte!",
        "low_health_msg": "Deine Lebenspunkte sind kritisch niedrig! Auto-Quest pausiert. Heile dich!",
        "level_up_title": "Level Aufstieg!",
        "level_up_msg": "Level Up! Du bist jetzt Level {level}!\n\nAttribut-Boni:\n{bonuses}",
        "milestone_unlocked": "Meilenstein freigeschaltet!",

        # Game Over
        "game_over_title": "Game Over",
        "rebirth_title": "Wiedergeburt!",
        "game_over_quest_text": "Ruhe in Frieden, {name}.\n\nDu bist bei einer Quest gestorben und dein Charakter wurde gelöscht.",
        "game_over_rebirth_text": "{name} wurde von einem Boss besiegt!\n\nDurch die Niederlage bist du stärker geworden.\nDu wirst auf Level 1 zurückgesetzt, aber deine Basisattribute wurden permanent verbessert!",

        # ... (we will add more texts as we refactor each file)
    },
    "en": {
        # General
        "warning": "Warning",
        "error": "Error",
        "ok": "OK",
        "close": "Close",
        "name": "Name",
        "level": "Level",
        "gold": "Gold",
        "strength": "Strength",
        "intelligence": "Intelligence",
        "luck": "Luck",
        "agility": "Agility",

        # Splash Screen
        "splash_title": "Welcome to Chronicle of the Idle Hero!",
        "splash_objective_title": "Objective:",
        "splash_objective_text": "Grow stronger, defeat increasingly powerful bosses, and climb to the top of the highscore list. Death by a boss is not the end, but a rebirth that makes you stronger. But be warned: Failing a normal quest will lead to the permanent deletion of your hero!",
        "splash_controls_title": "Controls:",
        "splash_controls_text": "The game is primarily controlled with the mouse. Start quests, visit merchants, and equip items to advance your adventure.",
        "continue": "Continue",
        "language": "Sprache / Language",

        # Start Menu
        "start_menu_title": "Chronicle of the Idle Hero - Main Menu",
        "load_save": "Load Save File",
        "preview": "Preview",
        "load": "Load",
        "new_game": "New Game",
        "highscores": "Highscores",
        "quit": "Quit",
        "start_menu_intro": "Choose a save file or create a new hero.\nWarning: Death on a quest deletes the save file!",

        # Class Selection
        "class_selection_title": "Character Creation",
        "enter_name": "Enter your name:",
        "select_class": "Select your class:",
        "warrior": "Warrior",
        "mage": "Mage",
        "rogue": "Rogue",
        "confirm": "Confirm",
        "back": "Back",
        "warrior_desc": "A master of melee combat, relying on strength and toughness.",
        "mage_desc": "A scholar of the arcane arts, whose power depends on their intelligence.",
        "rogue_desc": "A skillful scoundrel who uses agility to outmaneuver their foes.",

        # RPG GUI (Main Game)
        "char_status": "Character Status",
        "item_level": "Item Level",
        "attributes": "Attributes",
        "resources": "Resources",
        "no_resources": "No resources gathered yet.",
        "life_points": "Life Points",
        "mana_points": "Mana Points",
        "energy": "Energy",
        "rage": "Rage",
        "experience": "Experience",
        "actions": "Actions",
        "start_quest": "Start New Quest",
        "start_auto_quest": "Start Auto-Quest",
        "stop_auto_quest": "Stop Auto-Quest",
        "visit_trader": "Visit Trader",
        "visit_blacksmith": "Visit Blacksmith",
        "boss_arena": "Boss Arena",
        "equip_item": "Equip Item",
        "use_item": "Use Item",
        "log": "Log",
        "equipment": "Equipment",
        "inventory": "Inventory",
        "head": "Head",
        "chest": "Chest",
        "weapon": "Weapon",
        "empty_slot": "Empty",
        "quest_active": "Quest Active",
        "quest_active_msg": "Please complete your current quest first.",
        "inventory_full": "Inventory Full",
        "inventory_full_msg": "Your inventory is full. Visit the trader!",
        "low_health": "Low Health!",
        "low_health_msg": "Your health is critically low! Auto-Quest paused. Heal up!",
        "level_up_title": "Level Up!",
        "level_up_msg": "Level Up! You are now level {level}!\n\nAttribute Bonuses:\n{bonuses}",
        "milestone_unlocked": "Milestone Unlocked!",

        # Game Over
        "game_over_title": "Game Over",
        "rebirth_title": "Rebirth!",
        "game_over_quest_text": "Rest in peace, {name}.\n\nYou died on a quest and your character has been deleted.",
        "game_over_rebirth_text": "{name} was defeated by a boss!\n\nThrough defeat, you have grown stronger.\nYou are reset to level 1, but your base attributes have been permanently increased!",

        # ... (we will add more texts as we refactor each file)
    }
}

def get_text(lang, key):
    """
    Returns the translated text for a given key and language.
    Falls back to German if the key is not found in the selected language.
    """
    return TEXTS.get(lang, TEXTS["de"]).get(key, TEXTS["de"].get(key, key))
