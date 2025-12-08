# game_data.py
"""
Contains static game data, such as class definitions.
Uses localization keys for user-facing text.
"""

CLASSES = {
    "warrior": {
        "name_key": "class_warrior_name",
        "desc_key": "class_warrior_desc",
        "attributes": {'strength': 8, 'agility': 4, 'intelligence': 3, 'luck': 4},
        "main_stat": "strength",
        "allowed_armor": ["chain", "plate"],
        "image_path": "assets/krieger.png"
    },
    "mage": {
        "name_key": "class_mage_name",
        "desc_key": "class_mage_desc",
        "attributes": {'strength': 3, 'agility': 5, 'intelligence': 8, 'luck': 4},
        "main_stat": "intelligence",
        "allowed_armor": ["cloth"],
        "image_path": "assets/magier.png"
    },
    "rogue": {
        "name_key": "class_rogue_name",
        "desc_key": "class_rogue_desc",
        "attributes": {'strength': 4, 'agility': 8, 'intelligence': 3, 'luck': 6},
        "main_stat": "agility",
        "allowed_armor": ["leather"],
        "image_path": "assets/schurke.png"
    }
}

ITEM_BLUEPRINTS = {
    # Nomen: (Name, Artikel) -> (name_key, gender)
    "weapon": [
        {"name_key": "item_sword", "gender": "n", "base_stat": "strength", "base_bonus": 2},
        {"name_key": "item_staff", "gender": "m", "base_stat": "intelligence", "base_bonus": 2},
        {"name_key": "item_dagger", "gender": "m", "base_stat": "agility", "base_bonus": 2},
    ],
    "head": [
        {"name_key": "item_chain_hood", "gender": "f", "base_stat": "strength", "base_bonus": 1, "armor_type": "chain"},
        {"name_key": "item_cloth_hat", "gender": "m", "base_stat": "intelligence", "base_bonus": 1, "armor_type": "cloth"},
        {"name_key": "item_leather_cowl", "gender": "f", "base_stat": "agility", "base_bonus": 1, "armor_type": "leather"},
    ],
    "chest": [
        {"name_key": "item_plate_armor", "gender": "m", "base_stat": "strength", "base_bonus": 3, "armor_type": "plate"},
        {"name_key": "item_cloth_robe", "gender": "f", "base_stat": "intelligence", "base_bonus": 3, "armor_type": "cloth"},
        {"name_key": "item_leather_jerkin", "gender": "n", "base_stat": "agility", "base_bonus": 2, "armor_type": "leather"},
    ]
}

RARITIES = {
    "poor":         {"name_key": "rarity_poor", "color": "#B0B0B0", "modifier": 0.7, "min_level": 1, "weight": 10, "max_upgrades": 2},
    "common":       {"name_key": "rarity_common", "color": "#FFFFFF", "modifier": 1.0, "min_level": 1, "weight": 70, "max_upgrades": 3},
    "uncommon":     {"name_key": "rarity_uncommon", "color": "#1EFF00", "modifier": 1.2, "min_level": 5, "weight": 15, "max_upgrades": 5},
    "rare":         {"name_key": "rarity_rare", "color": "#68AFFF", "modifier": 1.5, "min_level": 15, "weight": 4,  "max_upgrades": 7},
    "epic":         {"name_key": "rarity_epic", "color": "#A335EE", "modifier": 1.8, "min_level": 30, "weight": 1,  "max_upgrades": 10},
    "legendary":    {"name_key": "rarity_legendary", "color": "#FF8000", "modifier": 2.2, "min_level": 50, "weight": 0.1,"max_upgrades": 13},
    "mythic":       {"name_key": "rarity_mythic", "color": "#E5CC80", "modifier": 2.7, "min_level": 75, "weight": 0.01,"max_upgrades": 15}
}

ITEM_ICONS = {
    "weapon": "🗡️",
    "shield": "🛡️",
    "head": "👑",
    "chest": "👕",
    "legs": "👖",
    "feet": "👢",
    "consumable": "🧪"
}

POTIONS = [
    # LP Potions
    {"level_req": 1, "name_key": "potion_small_healing", "type": "LP", "value": 50, "cost": 25},
    {"level_req": 10, "name_key": "potion_healing", "type": "LP", "value": 150, "cost": 100},
    {"level_req": 25, "name_key": "potion_large_healing", "type": "LP", "value": 500, "cost": 500},
    {"level_req": 50, "name_key": "potion_superior_healing", "type": "LP", "value": 2000, "cost": 2500},

    # Mana Potions
    {"level_req": 1, "name_key": "potion_small_mana", "type": "MP", "value": 30, "cost": 35},
    {"level_req": 10, "name_key": "potion_mana", "type": "MP", "value": 100, "cost": 120},
    {"level_req": 25, "name_key": "potion_large_mana", "type": "MP", "value": 400, "cost": 600},
    {"level_req": 50, "name_key": "potion_superior_mana", "type": "MP", "value": 1500, "cost": 3000},

    # Energy Potions
    {"level_req": 1, "name_key": "potion_small_energy", "type": "Energie", "value": 30, "cost": 35},
    {"level_req": 10, "name_key": "potion_energy", "type": "Energie", "value": 100, "cost": 120},

    # Rage Potions
    {"level_req": 1, "name_key": "potion_small_rage", "type": "Wut", "value": 20, "cost": 40},
    {"level_req": 10, "name_key": "potion_rage", "type": "Wut", "value": 75, "cost": 130},
]

WARRIOR_EVENTS = [
    "warrior_event_1", "warrior_event_2", "warrior_event_3",
    "warrior_event_4", "warrior_event_5", "warrior_event_6"
]

MAGE_EVENTS = [
    "mage_event_1", "mage_event_2", "mage_event_3",
    "mage_event_4", "mage_event_5", "mage_event_6"
]

ROGUE_EVENTS = [
    "rogue_event_1", "rogue_event_2", "rogue_event_3",
    "rogue_event_4", "rogue_event_5", "rogue_event_6"
]

BOSS_TIERS = [
    {
        "tier": 0, "name_key": "boss_goblin_king", "hp": 150, "damage": (10, 20),
        "image_path": "assets/bosses/goblin_king.png", "required_item_level": 0
    },
    {
        "tier": 1, "name_key": "boss_stone_golem", "hp": 250, "damage": (15, 25),
        "image_path": "assets/bosses/stone_golem.png", "required_item_level": 20
    },
    {
        "tier": 2, "name_key": "boss_chimera_matriarch", "hp": 400, "damage": (25, 40),
        "image_path": "assets/bosses/chimaeren_matriarchin.png", "required_item_level": 45
    },
    {
        "tier": 3, "name_key": "boss_necromancer_lord", "hp": 650, "damage": (40, 60),
        "image_path": "assets/bosses/nekromanten_lord.png", "required_item_level": 75
    },
    {
        "tier": 4, "name_key": "boss_ice_giant_chief", "hp": 1000, "damage": (60, 80),
        "image_path": "assets/bosses/eisriesen_haeuptling.png", "required_item_level": 110
    },
    {
        "tier": 5, "name_key": "boss_ancient_dragon", "hp": 1500, "damage": (80, 120),
        "image_path": "assets/bosses/alter_drache.png", "required_item_level": 150
    }
]

# --- Components for procedural text generation ---

QUEST_LOCATIONS = [
    "quest_location_1", "quest_location_2", "quest_location_3",
    "quest_location_4", "quest_location_5"
]

QUEST_ACTIONS_PREFIX = [
    "quest_action_prefix_1", "quest_action_prefix_2", "quest_action_prefix_3"
]

QUEST_RETURNS = [
    "quest_return_1", "quest_return_2", "quest_return_3"
]
