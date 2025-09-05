from typing import List, Optional, Tuple, Dict, Union
from dataclasses import asdict

from data.storage import storage
from data.models import CharacterStats, UserStats, ServerStats

class StatsManager:
    @staticmethod
    def get_most_common_character() -> Tuple[Union[str, List[str]], int]:
        """Get the most commonly rolled character(s)."""
        max_count = 0
        max_chars = []
        
        for name, stats in storage.character_stats.items():
            if stats.count > max_count:
                max_count = stats.count
                max_chars = [name]
            elif stats.count == max_count:
                max_chars.append(name)
                
        return max_chars if len(max_chars) > 1 else max_chars[0], max_count

    @staticmethod
    def get_winningest_raider() -> Tuple[Union[str, List[str]], int]:
        """Get the character(s) with the most raid wins."""
        max_wins = 0
        max_chars = []
        
        for name, stats in storage.character_stats.items():
            if stats.raids_won > max_wins:
                max_wins = stats.raids_won
                max_chars = [name]
            elif stats.raids_won == max_wins:
                max_chars.append(name)
                
        return max_chars if len(max_chars) > 1 else max_chars[0], max_wins
    
    @staticmethod
    def get_top_ten():
        top_chars = {name: stats.count for name, stats in storage.character_stats.items()}
        sorted_chars = sorted(top_chars.items(), key=lambda item: item[1], reverse=True)
        
        return dict(sorted_chars[:10])
            

    @staticmethod
    def increment_character_count(name: str) -> int:
        """
        Increment a character's roll count and return status code:
        0 = normal increment
        1 = took the lead
        2 = tied for lead
        100 = first to 100 rolls
        """
        char_stats = storage.get_character_stats(name)
        if not char_stats:
            return 0
            
        most_common, count = StatsManager.get_most_common_character()
        char_stats.count += 1
        storage.save_all()
        
        if char_stats.count > count:
            return 1
        elif char_stats.count == count:
            return 2
        elif char_stats.count > count and char_stats.count == 100:
            return 100
            
        return 0

    @staticmethod
    def get_character_group_members(group: str) -> List[str]:
        """Get all characters in a specific group."""
        return [
            name for name, stats in storage.character_stats.items()
            if stats.group == group
        ]

    @staticmethod
    def get_user_ex_cards(name: str) -> List[str]:
        """Get all EX cards owned by a user."""
        user_stats = storage.get_user_stats(name)
        return user_stats.deck if user_stats else []

    @staticmethod
    def get_server_campaign_progress(name: str) -> Dict[str, Union[str, int]]:
        """Get a server's campaign progress."""
        server_stats = storage.get_server_stats(name)
        if not server_stats:
            return {"campaign": "None", "completed": 0}
            
        return {
            "campaign": server_stats.campaign,
            "completed": server_stats.campaign_completed
        }

    @staticmethod
    def increment_pvp_wins(name: str) -> int:
        """Increment a user's PVP win count."""
        print(f"Incrementing PVP wins for {name}")
        stats = storage.get_user_stats(name)
        
        if not stats:
            stats = UserStats(name)
            
        if not hasattr(stats, 'pvp_wins'):
            stats.pvp_wins = 1
            
        stats.pvp_wins += 1
        storage.update_user_stats(name)
        return stats.pvp_wins
        
    @staticmethod
    def get_pvp_champion() -> Tuple[Union[str, List[str]], int]:
        """Returns the user(s) with the most PVP wins and their win count."""
        max_wins = 0
        champions = []
        
        for name, stats in storage.user_stats.items():
            if not hasattr(stats, 'pvp_wins'):
                continue
                
            if stats.pvp_wins > max_wins:
                max_wins = stats.pvp_wins
                champions = [name]
            elif stats.pvp_wins == max_wins:
                champions.append(name)
                
        if len(champions) == 1:
            return champions[0], max_wins
        return champions, max_wins 