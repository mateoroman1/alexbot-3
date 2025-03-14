import os
from pathlib import Path
from typing import Final

# Directory paths
ROOT_DIR: Final[Path] = Path(__file__).parent.parent
ASSETS_DIR: Final[Path] = ROOT_DIR / "assets/utility"
IMAGES_DIR: Final[Path] = ROOT_DIR / "assets/characters"
TOOLS_DIR: Final[Path] = ROOT_DIR / "assets/items"
BOSSES_DIR: Final[Path] = ROOT_DIR / "assets/bosses"
EX_DIR: Final[Path] = ROOT_DIR / "assets/ex"
EVOLUTIONS_DIR: Final[Path] = ROOT_DIR / "assets/evolutions"

# File paths
CHARACTER_STATS_FILE: Final[Path] = ROOT_DIR / "data/character_stats.json"
BOSS_STATS_FILE: Final[Path] = ROOT_DIR / "data/boss_stats.json"
TOOL_STATS_FILE: Final[Path] = ROOT_DIR / "data/tool_stats.json"
USER_STATS_FILE: Final[Path] = ROOT_DIR / "data/user_stats.json"
SERVER_STATS_FILE: Final[Path] = ROOT_DIR / "data/server_stats.json"

# Bot settings
DISCORD_TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')
APPLICATION_ID: Final[int] = 1166182848273854534
OWNER_ID: Final[int] = 108378541988515840
MAIN_GUILD_ID: Final[int] = 240265833199173633

# Game settings
RAID_TIMEOUT: Final[int] = 60  # seconds
RAID_MIN_PLAYERS: Final[int] = 1
RAID_HARDMODE_THRESHOLD: Final[int] = 4
RAID_NIGHTMARE_THRESHOLD: Final[int] = 5
HARDMODE_HEALTH_MULTIPLIER: Final[float] = 1.5
NIGHTMARE_HEALTH_MULTIPLIER: Final[float] = 2.0
CAMPAIGN_HEALTH_SCALING: Final[float] = 0.25

# Image settings
ALLOWED_IMAGE_EXTENSIONS: Final[tuple] = (".png", ".jpg", ".jpeg", ".gif")

# Character groups
CHARACTER_GROUPS: Final[tuple] = (
    "alex", "alex call center", "alex drag strip", "alex garage", 
    "alex scholars", "alex shamans", "alexcon", "ALEXFORCE", 
    "china expansion", "classics", "classics family", "drip havers", 
    "duos", "evil geniuses", "experiment", "geekers", "hamburger", 
    "hooligans", "intuitive eaters", "magic cards", "magic entities", 
    "majhong club", "middle east", "money getters", "negative morale", 
    "non human", "non living", "oldheads", "poopbutt industries", 
    "prisoners", "quans", "racing team", "rec center", "retirement home", 
    "shapeshifter", "shawties", "shop class", "space war", "squads", 
    "tater dynasty", "the arcane", "the cookout", "truck month", 
    "warriors", "yurt kitchen", "yurt trucking", "yurttears", "_unsorted"
) 