import os
import random
from pathlib import Path
from typing import List, Optional, Tuple
from fuzzywuzzy import fuzz

from config.config import (
    IMAGES_DIR,
    TOOLS_DIR,
    BOSSES_DIR,
    ALLOWED_IMAGE_EXTENSIONS
)
from data.storage import storage

def get_random_file(directory: Path, allowed_extensions: Tuple[str, ...] = ALLOWED_IMAGE_EXTENSIONS) -> str:
    """Get a random file from a directory with allowed extensions."""
    all_files = os.listdir(directory)
    valid_files = [file for file in all_files if file.endswith(allowed_extensions)]
    if not valid_files:
        raise FileNotFoundError(f"No valid files found in {directory}")
    return random.choice(valid_files)

def get_image_extension(filename: str) -> str:
    """Get the file extension from a filename."""
    for ext in ALLOWED_IMAGE_EXTENSIONS:
        if filename.endswith(ext):
            return ext
    return ""

def find_closest_match(query: str, choices: List[str], threshold: int = 92) -> Optional[str]:
    """Find the closest matching string from a list of choices."""
    closest_score = -1
    closest_match = None
    
    for choice in choices:
        score = fuzz.ratio(query.casefold(), choice.casefold())
        if score > closest_score:
            closest_score = score
            closest_match = choice
            
    return closest_match if closest_score >= threshold else None

def roll_character(revealed_only: bool = True) -> str:
    """Roll a random character."""
    while True:
        character = get_random_file(IMAGES_DIR)
        name = os.path.splitext(character)[0].casefold()
        if storage.get_character_stats(name) is not None:
            if not revealed_only or storage.get_character_stats(name).count > 0:
                return character

def roll_tool() -> str:
    """Roll a random tool."""
    while True:
        tool = get_random_file(TOOLS_DIR)
        name = os.path.splitext(tool)[0]
        if name in storage.tool_stats:
            return tool

def roll_boss(mode: str, server_name: str) -> str:
    """Roll a boss based on mode and server."""
    server_stats = storage.get_server_stats(server_name)
    print("Server stats retrieved")
    
    if mode == "campaign":
        boss = server_stats.campaign
        if boss == "None" or boss is None:
            boss = "david"
        elif server_stats.campaign == "COMPLETE":
            boss = "Tipp Tronix" if server_stats.campaign_completed % 2 == 1 else "david"
            storage.update_server_stats(server_name, campaign=boss)
        return f"{boss}.jpg"
    
    while True:
        print("Attempting to get boss...")
        boss = get_random_file(BOSSES_DIR)
        print(boss)
        name = os.path.splitext(boss)[0]
        print(name)
        if storage.get_boss_stats(name).times_defeated >= 0:
            print("Classic boss selected")
            return boss

def calculate_damage_multiplier(character: str, tool: str) -> float:
    """Calculate damage multiplier for a character-tool combination."""
    char_stats = storage.get_character_stats(character)
    tool_stats = storage.get_tool_stats(tool)
    
    base_multiplier = char_stats.count * 10
    
    # Apply tool multiplier
    if tool_stats is not None:
        if character in tool_stats.character_multipliers:
            base_multiplier *= tool_stats.character_multipliers[character]
        else:
            base_multiplier *= tool_stats.default_multiplier
        
    # Apply group bonus
        if tool_stats.group == char_stats.group:
            base_multiplier *= 2
        
    return base_multiplier

def is_valid_image_path(path: str) -> bool:
    """Check if a path is safe and valid for image operations."""
    return (
        ".." not in path and
        any(path.endswith(ext) for ext in ALLOWED_IMAGE_EXTENSIONS)
    ) 