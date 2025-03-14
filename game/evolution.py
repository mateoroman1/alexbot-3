from typing import List, Optional, Tuple
from pathlib import Path

from config.config import EVOLUTIONS_DIR
from data.models import EVOLUTION_RECIPES
from data.storage import storage

class EvolutionManager:
    @staticmethod
    def check_evolution(tools: List[str]) -> Optional[Tuple[str, str, str]]:
        """
        Check if any tools in the list can evolve.
        
        Args:
            tools: List of tool names to check
            
        Returns:
            Tuple of (evolved_tool, tool1, tool2) if evolution possible, None otherwise
        """
        for evolved, recipe in EVOLUTION_RECIPES.items():
            if recipe[0] in tools and recipe[1] in tools:
                return evolved, recipe[0], recipe[1]
        return None
    
    @staticmethod
    def get_evolution_path(evolved_name: str) -> Optional[Path]:
        """Get the path to an evolution's image file."""
        path = EVOLUTIONS_DIR / f"{evolved_name}.gif"
        return path if path.exists() else None
    
    @staticmethod
    def apply_evolution_bonus(evolved_name: str, total_damage: float) -> float:
        """Apply the evolution's damage multiplier."""
        tool_stats = storage.get_tool_stats(evolved_name)
        if tool_stats:
            return total_damage * tool_stats.default_multiplier
        return total_damage 