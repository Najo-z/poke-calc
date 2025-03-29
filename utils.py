from typing import Any


def clean_name(name: str) -> str:
    return name.lower().replace(" ", "")


def get_status_rate(
    frozen_sleep: bool = False, para_burn_poison: bool = False
) -> float:
    if frozen_sleep:
        return 2.5
    if para_burn_poison:
        return 1.5
    return 1.0


def get_capture_rate(
    cap_rate: int, ball: float, status: float, hp_ratio: float
) -> float:
    """Heavy Ball not yet Supported"""
    return cap_rate * ball * status * (1 - 2 / 3 * hp_ratio) / 255 * 100


def get_ball_rate(ball: str, pokemon_info: dict[str, Any]) -> float:
    ball = clean_name(ball)

    match ball:
        case "beastball":
            return 5.0 if pokemon_info.get("is_ultra_beast", False) else 0.1
        case "cherishball" | "gsball" | "pokeball" | "ancientpokeball":
            return 1.0
        case "diveball":
            return 3.5 if pokemon_info.get("in_water", False) else 1.0
        case "dreamball":
            return 4.0 if pokemon_info.get("status") == "sleep" else 1.0
        case "duskball":
            if pokemon_info.get("is_ultra_beast", False):
                return 0.1
            elif pokemon_info.get("is_dark_place", False):
                return 3.0
            else:
                return 1.0
        case "fastball":
            return 4.0 if pokemon_info.get("base_speed", 0) >= 100 else 1.0
        case "featherball":
            return 1.0  # Normal catch rate, travels farther outside battle
        case "friendball":
            return 1.0  # Sets happiness to 200, no catch rate bonus
        case "gigatonball":
            return 2.75  # Higher catch rate but shorter throw distance
        case "greatball" | "ancientgreatball":
            return 1.5
        case "healball":
            return 1.0  # Heals Pokémon, no catch rate bonus
        case "heavyball" | "ancientheavyball":
            weight = pokemon_info.get("weight", 0)
            if ball == "ancientheavyball":
                return 1.25  # Ancient Heavy Ball has fixed rate
            else:
                # Regular Heavy Ball depends on weight
                if weight >= 300:
                    return 30.0
                elif weight >= 200:
                    return 20.0
                elif weight >= 100:
                    return 10.0
                else:
                    return 0.5  # Penalty for light Pokémon
        case "jetball":
            return 1.5  # Higher catch rate and much farther distance
        case "leadenball":
            return 2.0  # Higher catch rate but shorter distance
        case "levelball":
            player_level = pokemon_info.get("player_pokemon_level", 1)
            wild_level = pokemon_info.get("wild_pokemon_level", 1)
            if player_level >= wild_level * 4:
                return 8.0
            elif player_level >= wild_level * 2:
                return 4.0
            elif player_level > wild_level:
                return 2.0
            else:
                return 1.0
        case "loveball":
            same_species = pokemon_info.get("same_species", False)
            opposite_gender = pokemon_info.get("opposite_gender", False)
            return 8.0 if same_species and opposite_gender else 1.0
        case "lureball":
            return 5.0 if pokemon_info.get("found_by_fishing", False) else 1.0
        case "luxuryball":
            return 1.0  # Happiness bonus, no catch rate bonus
        case "masterball" | "originball" | "parkball":
            return float("inf")  # Catches without fail
        case "moonball":
            return 4.0 if pokemon_info.get("evolves_with_moon_stone", False) else 1.0
        case "nestball":
            level = pokemon_info.get("wild_pokemon_level", 1)
            if level <= 30:
                return (41 - level) / 10
            else:
                return 1.0
        case "netball":
            types = [_type["type"]["name"] for _type in pokemon_info["types"]]
            return 3.5 if "bug" in types or "water" in types else 1.0
        case "premierball":
            return 1.0  # Visual effect, no catch rate bonus
        case "quickball":
            return 5.0
        case "repeatball":
            return 3.5 if pokemon_info.get("previously_caught", False) else 1.0
        case "safariball":
            biome = pokemon_info.get("biome", "")
            return 1.5 if biome in ["Plains", "Savanna"] else 1.0
        case "sportball":
            types = [_type["type"]["name"] for _type in pokemon_info["types"]]
            return 1.5 if "bug" in types else 1.0
        case "timerball":
            turn = pokemon_info.get("turn", 1)
            return min(4.0, (1 + turn * 0.3))
        case "ultraball" | "ancientultraball":
            return 2.0
        case "wingball":
            return 1.25  # Slightly higher catch rate and farther distance
        case _:
            raise ValueError(f"Ball {ball} is not implemented.")
