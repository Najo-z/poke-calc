import json
from functools import cache
from pathlib import Path
from typing import Any

import requests

from utils import clean_name

BASIC_URL = "https://pokeapi.co/api/v2/"
CACHE_DIR = Path("_pokedex_cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)
POKEMON_DIR = CACHE_DIR / "pokemon"
SPECIES_DIR = CACHE_DIR / "pokemon-species"


def get_all(category: str) -> None:
    # Get total count
    url = BASIC_URL + category
    info = requests.get(url)
    info = info.json()
    total_count = info["count"]
    # Get all urls
    url = f"{url}?limit={total_count}"
    info = requests.get(url)
    info = info.json()
    all_urls_names = [(result["name"], result["url"]) for result in info["results"]]
    category_dir = CACHE_DIR / category
    category_dir.mkdir(parents=True, exist_ok=True)
    for category_name, url in all_urls_names:
        category_file = category_dir / f"{category_name}.json"
        if category_file.exists():
            continue
        data = requests.get(url).text
        print("Requesting ", category_name)
        category_file.write_text(data)


@cache
def species(_species: str) -> dict[str, Any]:
    return json.loads((SPECIES_DIR / f"{_species}.json").read_text())


@cache
def pokemon(_pokemon: str) -> dict[str, Any]:
    _pokemon = clean_name(_pokemon)
    return json.loads((POKEMON_DIR / f"{_pokemon}.json").read_text())


@cache
def rate(_pokemon: str) -> int:
    _pokemon = clean_name(_pokemon)
    species_nb = pokemon(_pokemon)["species"]["name"]
    return species(species_nb)["capture_rate"]

@cache
def poketypes(_pokemon: str) -> list[str]:
    _pokemon = clean_name(_pokemon)
    types = [_type["type"]["name"] for _type in pokemon(_pokemon)["types"]]
    return types

print("Getting all data...")
get_all("pokemon-species")
get_all("pokemon")
print("Done getting all data...")

pokemon_names = [file.stem for file in sorted(POKEMON_DIR.glob("*.json"))]
