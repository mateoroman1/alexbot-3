"""Test summary and quick validation tests."""

import pytest
from unittest.mock import patch

from data.storage import DataStorage
from game.stats import StatsManager
from utils.helpers import calculate_damage_multiplier


class TestQuickValidation:
    """Quick validation tests to ensure core functionality works."""

    def test_storage_basic_operations(self, mock_storage):
        """Test basic storage operations work correctly."""
        storage = mock_storage
        
        # Test character stats
        char_stats = storage.get_character_stats("testchar")
        assert char_stats.count == 0
        
        storage.increment_character_stat("testchar", "count", 5)
        updated_stats = storage.get_character_stats("testchar")
        assert updated_stats.count == 5

    def test_damage_calculation_basic(self, populated_storage):
        """Test basic damage calculation works."""
        with patch('utils.helpers.storage', populated_storage):
            damage = calculate_damage_multiplier("alex", "sword")
            assert damage > 0
            assert isinstance(damage, float)

    def test_stats_manager_basic(self, populated_storage):
        """Test basic stats manager operations."""
        with patch('game.stats.storage', populated_storage):
            # Test getting most common character
            character, count = StatsManager.get_most_common_character()
            assert isinstance(character, (str, list))
            assert isinstance(count, int)
            assert count >= 0

    def test_evolution_system(self):
        """Test evolution system works."""
        from game.evolution import EvolutionManager
        
        # Test evolution check
        tools = ["the gorb", "the necromancers skull"]
        result = EvolutionManager.check_evolution(tools)
        assert result is not None
        assert result[0] == "full power gorb"

    def test_utility_functions(self):
        """Test utility functions work."""
        from utils.helpers import is_valid_image_path, find_closest_match
        
        # Test path validation
        assert is_valid_image_path("test.png") is True
        assert is_valid_image_path("test.txt") is False
        
        # Test fuzzy matching
        choices = ["alex", "david", "mikey"]
        result = find_closest_match("alex", choices)
        assert result == "alex"
