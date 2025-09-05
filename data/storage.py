import json
from pathlib import Path
from typing import Dict, Optional, TypeVar, Type, Any, Union
from dataclasses import asdict

from config.config import (
    CHARACTER_STATS_FILE,
    BOSS_STATS_FILE,
    TOOL_STATS_FILE,
    USER_STATS_FILE,
    SERVER_STATS_FILE
)
from .models import CharacterStats, BossStats, ToolStats, UserStats, ServerStats

T = TypeVar('T')

class DataStorage:
    def __init__(self):
        self.character_stats: Dict[str, CharacterStats] = {}
        self.boss_stats: Dict[str, BossStats] = {}
        self.tool_stats: Dict[str, ToolStats] = {}
        self.user_stats: Dict[str, UserStats] = {}
        self.server_stats: Dict[str, ServerStats] = {}
        self.load_all()

    def _load_json_file(self, file_path: Path) -> dict:
        """Load a JSON file, creating an empty one if it doesn't exist."""
        try:
            with open(file_path, 'r', encoding='utf8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf8') as f:
                json.dump({}, f)
            return {}

    def _save_json_file(self, file_path: Path, data: dict) -> None:
        """Save data to a JSON file."""
        with open(file_path, 'w', encoding='utf8') as f:
            json.dump(data, f, indent=2)

    def _convert_dict_to_dataclass(self, data: dict, cls: Type[T]) -> T:
        """Convert a dictionary to a dataclass instance."""
        if data.get('active_raid') is not None:
            data['active_raid'] = False
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    def load_all(self) -> None:
        """Load all data from JSON files."""
        # Load character stats
        char_data = self._load_json_file(CHARACTER_STATS_FILE)
        self.character_stats = {
            k: self._convert_dict_to_dataclass(v, CharacterStats) 
            for k, v in char_data.items()
        }

        # Load boss stats
        boss_data = self._load_json_file(BOSS_STATS_FILE)
        self.boss_stats = {
            k: self._convert_dict_to_dataclass(v, BossStats)
            for k, v in boss_data.items()
        }

        # Load tool stats
        tool_data = self._load_json_file(TOOL_STATS_FILE)
        self.tool_stats = {
            k: self._convert_dict_to_dataclass(v, ToolStats)
            for k, v in tool_data.items()
        }

        # Load user stats
        user_data = self._load_json_file(USER_STATS_FILE)
        self.user_stats = {
            k: self._convert_dict_to_dataclass(v, UserStats)
            for k, v in user_data.items()
        }

        # Load server stats
        server_data = self._load_json_file(SERVER_STATS_FILE)
        self.server_stats = {
            k: self._convert_dict_to_dataclass(v, ServerStats)
            for k, v in server_data.items()
        }

    def save_all(self) -> None:
        """Save all data to JSON files."""
        self._save_json_file(CHARACTER_STATS_FILE, {k: asdict(v) for k, v in self.character_stats.items()})
        self._save_json_file(BOSS_STATS_FILE, {k: asdict(v) for k, v in self.boss_stats.items()})
        self._save_json_file(TOOL_STATS_FILE, {k: asdict(v) for k, v in self.tool_stats.items()})
        self._save_json_file(USER_STATS_FILE, {k: asdict(v) for k, v in self.user_stats.items()})
        self._save_json_file(SERVER_STATS_FILE, {k: asdict(v) for k, v in self.server_stats.items()})

    def get_character_stats(self, name: str) -> CharacterStats:
        """Get stats for a character by name."""
        name = name.casefold()
        if name not in self.character_stats:
            self.character_stats[name] = CharacterStats()
        return self.character_stats[name]

    def get_boss_stats(self, name: str) -> BossStats:
        """Get stats for a boss by name."""
        if name not in self.boss_stats:
            self.boss_stats[name] = BossStats(health=0.0, weakness="")
        return self.boss_stats[name]

    def get_tool_stats(self, name: str) -> ToolStats:
        """Get stats for a tool by name."""
        if name not in self.tool_stats:
            self.tool_stats[name] = ToolStats()
        return self.tool_stats[name]

    def get_user_stats(self, name: str) -> UserStats:
        """Get stats for a user by name."""
        if name not in self.user_stats:
            self.user_stats[name] = UserStats()
        return self.user_stats[name]

    def get_server_stats(self, name: str) -> ServerStats:
        """Get stats for a server by name."""
        if name not in self.server_stats:
            self.server_stats[name] = ServerStats()
        return self.server_stats[name]

    def update_character_stats(self, name: str, **kwargs: Any) -> None:
        """Update stats for a character."""
        if name not in self.character_stats:
            self.character_stats[name] = CharacterStats()
        char_stats = self.character_stats[name]
        for k, v in kwargs.items():
            if hasattr(char_stats, k):
                setattr(char_stats, k, v)
        self.save_all()

    def update_tool_stats(self, name: str, **kwargs: Any) -> None:
        """Update stats for a tool."""
        if name not in self.tool_stats:
            self.tool_stats[name] = ToolStats()
        tool_stat = self.tool_stats[name]
        for k, v in kwargs.items():
            if hasattr(tool_stat, k):
                setattr(tool_stat, k, v)
        self.save_all()

    def update_user_stats(self, name: str, **kwargs: Any) -> None:
        """Update stats for a user."""
        if name not in self.user_stats:
            self.user_stats[name] = UserStats()
        user_stats = self.user_stats[name]
        for k, v in kwargs.items():
            if hasattr(user_stats, k):
                setattr(user_stats, k, v)
        self.save_all()

    def update_boss_stats(self, boss: str, **kwargs: Any)-> None:
        """Updates boss stats"""
        if boss not in self.boss_stats:
            self.boss_stats[boss] = BossStats()
        boss_stats = self.boss_stats[boss]
        for k, v in kwargs.items():
            if hasattr(boss_stats, k):
                setattr(boss_stats, k, v)
        self.save_all()
    
    def update_server_stats(self, name: str, **kwargs: Any) -> None:
        """Update stats for a server."""
        if name not in self.server_stats:
            self.server_stats[name] = ServerStats()
        server_stats = self.server_stats[name]
        for k, v in kwargs.items():
            if hasattr(server_stats, k):
                setattr(server_stats, k, v)
        self.save_all()

    def increment_user_stat(self, name: str, field: str, amount: Union[int, float] = 1) -> None:
        """Increment a user stat by the specified amount."""
        user_stats = self.get_user_stats(name)
        if hasattr(user_stats, field):
            current_value = getattr(user_stats, field, 0)
            setattr(user_stats, field, current_value + amount)
        self.save_all()

    def increment_character_stat(self, name: str, field: str, amount: Union[int, float] = 1) -> None:
        """Increment a character stat by the specified amount."""
        char_stats = self.get_character_stats(name.casefold())
        if hasattr(char_stats, field):
            current_value = getattr(char_stats, field, 0)
            setattr(char_stats, field, current_value + amount)
        self.save_all()

    def increment_server_stat(self, name: str, field: str, amount: Union[int, float] = 1) -> None:
        """Increment a server stat by the specified amount."""
        server_stats = self.get_server_stats(name)
        if hasattr(server_stats, field):
            current_value = getattr(server_stats, field, 0)
            setattr(server_stats, field, current_value + amount)
        self.save_all()

    def increment_boss_stat(self, name: str, field: str, amount: Union[int, float] = 1) -> None:
        """Increment a boss stat by the specified amount."""
        boss_stats = self.get_boss_stats(name)
        if hasattr(boss_stats, field):
            current_value = getattr(boss_stats, field, 0)
            setattr(boss_stats, field, current_value + amount)
        self.save_all()

# Global instance
storage = DataStorage() 