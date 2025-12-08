# loot_system.py
"""
Handles the dynamic generation of loot based on player level.
"""
import random
from item import Item
from game_data import ITEM_BLUEPRINTS, RARITIES

def generate_item_for_level(level, luck):
    """
    Generates a new item with stats, rarity, and value scaled to the given level.
    """
    available_rarities = {r_key: data for r_key, data in RARITIES.items() if level >= data["min_level"]}

    rarity_keys = list(available_rarities.keys())
    rarity_weights = [data["weight"] for data in available_rarities.values()]

    luck_factor = 1 + (luck / 100)
    for i, r_key in enumerate(rarity_keys):
        if r_key not in ["poor", "common"]:
             rarity_weights[i] *= luck_factor

    chosen_rarity_key = random.choices(rarity_keys, weights=rarity_weights, k=1)[0]
    rarity_data = RARITIES[chosen_rarity_key]

    slot = random.choice(list(ITEM_BLUEPRINTS.keys()))
    blueprint = random.choice(ITEM_BLUEPRINTS[slot])

    stats_boost = {}
    base_bonus = blueprint["base_bonus"]
    primary_stat_value = int((base_bonus + (level * 0.9)) * rarity_data["modifier"])
    primary_stat_value = int(primary_stat_value * random.uniform(0.95, 1.05))
    stats_boost[blueprint["base_stat"]] = max(1, primary_stat_value)

    all_stats = ["strength", "agility", "intelligence", "luck"]
    if chosen_rarity_key in ["epic", "legendary", "mythic"]:
        possible_secondary_stats = [s for s in all_stats if s != blueprint["base_stat"]]
        if possible_secondary_stats:
            secondary_stat = random.choice(possible_secondary_stats)
            secondary_value = int(primary_stat_value * 0.4)
            stats_boost[secondary_stat] = max(1, secondary_value)

    if chosen_rarity_key == "mythic":
        possible_tertiary_stats = [s for s in all_stats if s not in stats_boost]
        if possible_tertiary_stats:
            tertiary_stat = random.choice(possible_tertiary_stats)
            tertiary_value = int(primary_stat_value * 0.25)
            stats_boost[tertiary_stat] = max(1, tertiary_value)

    total_stat_points = sum(stats_boost.values())
    value = max(1, int((level * 1.5) + (total_stat_points * 2.0) * rarity_data["modifier"]))

    return Item(
        name_key=blueprint["name_key"],
        gender=blueprint["gender"],
        slot=slot,
        stats_boost=stats_boost,
        value=value,
        rarity_key=chosen_rarity_key,
        armor_type=blueprint.get("armor_type")
    )

def generate_boss_reward(player):
    """
    Generates a guaranteed item upgrade after a boss fight.
    """
    all_slots = ["weapon", "head", "chest"]
    main_stat = player.main_stat

    occupied_slots = {
        item.slot for item in list(player.equipment.values()) + player.inventory
        if item and item.is_boss_item()
    }

    available_slots = [s for s in all_slots if s not in occupied_slots]

    if available_slots:
        chosen_slot = random.choice(available_slots)
        currently_equipped = player.equipment.get(chosen_slot)
        base_score = currently_equipped.get_weighted_score(main_stat) if currently_equipped else 0

        if player.level < 15: chosen_rarity_key = "rare"
        elif player.level < 30: chosen_rarity_key = "epic"
        else: chosen_rarity_key = "legendary"
        rarity_data = RARITIES[chosen_rarity_key]

        min_primary_stat = int((base_score * 1.2) + (player.level * 1.5))
        primary_stat_value = int(min_primary_stat * rarity_data["modifier"])
        stats_boost = {main_stat: max(min_primary_stat, primary_stat_value)}

        if random.random() < 0.75:
            stats_boost[main_stat] += int(primary_stat_value * 0.4)
        else:
            stats_boost["luck"] = int(primary_stat_value * 0.5)
    else:
        existing_boss_items = [item for item in list(player.equipment.values()) + player.inventory if item and item.is_boss_item()]
        item_to_upgrade = random.choice(existing_boss_items)
        chosen_slot = item_to_upgrade.slot
        chosen_rarity_key = item_to_upgrade.rarity_key
        rarity_data = RARITIES[chosen_rarity_key]

        stats_boost = {
            stat: int(value * random.uniform(1.05, 1.10)) + 1
            for stat, value in item_to_upgrade.base_stats.items()
        }

    allowed_armor_types = player.get_allowed_armor_types()
    possible_blueprints = [
        bp for bp in ITEM_BLUEPRINTS.get(chosen_slot, [])
        if (bp.get("base_stat") == main_stat) and
           (not bp.get("armor_type") or bp.get("armor_type") in allowed_armor_types)
    ]

    if not possible_blueprints: # Fallback for safety
        possible_blueprints = [bp for bp in ITEM_BLUEPRINTS["weapon"] if bp.get("base_stat") == main_stat]
        chosen_slot = "weapon"
    blueprint = random.choice(possible_blueprints)

    total_stat_points = sum(stats_boost.values())
    value = int((player.level * 5) + (total_stat_points * 4) * rarity_data["modifier"])

    return Item(
        name_key=blueprint["name_key"],
        gender=blueprint["gender"],
        slot=chosen_slot,
        stats_boost=stats_boost,
        value=value,
        rarity_key=chosen_rarity_key,
        armor_type=blueprint.get("armor_type"),
        is_boss_item=True
    )
