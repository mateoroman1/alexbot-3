from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union
from enum import Enum

class RaidMode(Enum):
    CAMPAIGN = "campaign"
    CLASSIC = "classic"

@dataclass
class CharacterStats:
    count: int = 0
    group: str = "_unsorted"
    raids_won: int = 0
    raids_completed: int = 0
    favorite_weapon: str = "None"
    total_pvp: int = 0
    pvp_wins: int = 0
    is_1_0: bool = False

@dataclass
class BossStats:
    health: float
    weakness: str
    times_defeated: int = 0
    times_won: int = 0
    wake_message: str = ""
    campaign_id: Optional[str] = None

@dataclass
class ToolStats:
    default_multiplier: float = 1.0
    group: str = "None"
    character_multipliers: Dict[str, float] = field(default_factory=dict)

@dataclass
class UserStats:
    total_rolls: int = 0
    highest_damage: int = 0
    average_damage: float = 0.0
    total_damage: int = 0
    total_raids: int = 0
    raid_wins: int = 0
    deck: List[str] = field(default_factory=list)
    tolls: int = 0
    total_pvp: int = 0
    pvp_wins: int = 0
    cursed: bool = False

@dataclass
class ServerStats:
    active_raid: bool = False
    total_rolls: int = 0
    campaign: str = "None"
    campaign_completed: int = 0
    users: int = 0
    ex_cards: int = 0
    raid_wins: int = 0
    total_raids: int = 0
    total_damage: int = 0
    highest_damage: int = 0
    total_pvp: int = 0
    successful_user: Dict[str, Union[str, int]] = field(default_factory=lambda: {
        "name": "None",
        "raid_wins": 0
    })

@dataclass
class RaidHand:
    character: str
    tool: Optional[str]
    damage_index: float
    
@dataclass
class RaidState:
    player_list: List[str]
    boss: str
    boss_health: float
    boss_weakness: str
    player_data: Dict[str, Union[RaidHand, tuple]] = field(default_factory=dict)
    hard_mode: bool = False
    nightmare: bool = False

# Evolution recipes
EVOLUTION_RECIPES: Dict[str, tuple[str, str]] = {
    "full power gorb": ("the gorb", "the necromancers skull"),
    "psychosis": ("voice to skull", "alexs pure lsd"),
    "indescribable wealth": ("gerder gumpsneeds guaranteed jackpot method", "luck of the irish"),
    "planetary annihilation": ("spindablocks storage", "liquid tiberium bomb"),
    "wok fortress": ("loan from chinese mike", "wok28"),
    "holy pact": ("tome of divine knowledge", "the gorb"),
    "dark pact": ("tome of irreverent knowledge", "the gorb"),
    "dads shotgun": ("dads gun", "moms purse"),
    "ultimate brain freeze": ("wok ki ki energy vortex", "coke flavored slurpee"),
    "avatar of the wok ki ki guardian": ("wok ki ki energy vortex", "ancient slapahoe peace pipe of good fortune and fruit"),
    "thugnars modified glock": ("thugnars glock", "the prollum solva"),
    "infinite omnipotent awareness": ("tome of divine knowledge", "tome of irreverent knowledge"),
    "alexbot militia": ("convoy", "backup"),
    "20 ton discount": ("10 finger discount", "titanium pimp hand")
} 