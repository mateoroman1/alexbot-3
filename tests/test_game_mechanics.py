"""Tests for core game mechanics and calculations."""

import pytest
from unittest.mock import Mock, patch

from utils.helpers import calculate_damage_multiplier, is_valid_image_path, find_closest_match
from game.evolution import EvolutionManager
from data.models import EVOLUTION_RECIPES


class TestDamageCalculation:
    """Test damage calculation mechanics."""

    def test_basic_damage_calculation(self, populated_storage):
        """Test basic damage calculation with character count and tool multiplier."""
        with patch('utils.helpers.storage', populated_storage):
            # Alex has count=5, sword has character_multipliers={"alex": 2.0}
            damage = calculate_damage_multiplier("alex", "sword")
            
            # Base: 5 * 10 = 50, Character-specific: 50 * 2.0 = 100
            assert damage == 100.0

    def test_character_specific_tool_multiplier(self, populated_storage):
        """Test damage calculation with character-specific tool multiplier."""
        with patch('utils.helpers.storage', populated_storage):
            # Alex has count=5, sword has character_multipliers={"alex": 2.0}
            damage = calculate_damage_multiplier("alex", "sword")
            
            # Base: 5 * 10 = 50, Character-specific: 50 * 2.0 = 100
            assert damage == 100.0

    def test_group_bonus_calculation(self, populated_storage):
        """Test damage calculation with group bonus."""
        with patch('utils.helpers.storage', populated_storage):
            # Create a character and tool with matching groups
            populated_storage.update_character_stats("testchar", count=3, group="warriors")
            populated_storage.update_tool_stats("warrior_sword", group="warriors", default_multiplier=1.2)
            
            damage = calculate_damage_multiplier("testchar", "warrior_sword")
            
            # Base: 3 * 10 = 30, Tool: 30 * 1.2 = 36, Group bonus: 36 * 2 = 72
            assert damage == 72.0

    def test_no_tool_stats(self, populated_storage):
        """Test damage calculation when tool stats don't exist."""
        with patch('utils.helpers.storage', populated_storage):
            damage = calculate_damage_multiplier("alex", "nonexistent_tool")
            
            # Should return base damage only: 5 * 10 = 50
            assert damage == 50.0

    def test_zero_character_count(self, populated_storage):
        """Test damage calculation with zero character count."""
        with patch('utils.helpers.storage', populated_storage):
            populated_storage.update_character_stats("newchar", count=0)
            
            damage = calculate_damage_multiplier("newchar", "sword")
            
            # Base: 0 * 10 = 0, Tool: 0 * 1.5 = 0
            assert damage == 0.0

    def test_negative_character_count(self, populated_storage):
        """Test damage calculation with negative character count."""
        with patch('utils.helpers.storage', populated_storage):
            populated_storage.update_character_stats("negchar", count=-2)
            
            damage = calculate_damage_multiplier("negchar", "sword")
            
            # Base: -2 * 10 = -20, Tool: -20 * 1.5 = -30
            assert damage == -30.0


class TestEvolutionMechanics:
    """Test evolution system mechanics."""

    def test_evolution_check_success(self):
        """Test successful evolution check."""
        tools = ["the gorb", "the necromancers skull", "other_tool"]
        result = EvolutionManager.check_evolution(tools)
        
        assert result is not None
        assert result[0] == "full power gorb"
        assert result[1] == "the gorb"
        assert result[2] == "the necromancers skull"

    def test_evolution_check_no_match(self):
        """Test evolution check with no matching tools."""
        tools = ["tool1", "tool2", "tool3"]
        result = EvolutionManager.check_evolution(tools)
        
        assert result is None

    def test_evolution_check_partial_match(self):
        """Test evolution check with only one matching tool."""
        tools = ["the gorb", "other_tool"]
        result = EvolutionManager.check_evolution(tools)
        
        assert result is None

    def test_evolution_check_empty_list(self):
        """Test evolution check with empty tool list."""
        tools = []
        result = EvolutionManager.check_evolution(tools)
        
        assert result is None

    def test_evolution_bonus_application(self, populated_storage):
        """Test evolution bonus application."""
        with patch('game.evolution.storage', populated_storage):
            # Create evolution tool stats
            populated_storage.update_tool_stats("full power gorb", default_multiplier=3.0)
            
            total_damage = 100.0
            result = EvolutionManager.apply_evolution_bonus("full power gorb", total_damage)
            
            assert result == 300.0

    def test_evolution_bonus_no_stats(self, populated_storage):
        """Test evolution bonus when tool stats don't exist."""
        with patch('game.evolution.storage', populated_storage):
            total_damage = 100.0
            result = EvolutionManager.apply_evolution_bonus("nonexistent_evolution", total_damage)
            
            assert result == 100.0  # Should return original damage

    def test_all_evolution_recipes(self):
        """Test that all evolution recipes are valid."""
        for evolved, recipe in EVOLUTION_RECIPES.items():
            assert len(recipe) == 2
            assert isinstance(recipe[0], str)
            assert isinstance(recipe[1], str)
            assert recipe[0] != recipe[1]  # Tools should be different


class TestUtilityFunctions:
    """Test utility functions."""

    def test_is_valid_image_path_valid(self):
        """Test valid image path validation."""
        valid_paths = [
            "image.png",
            "character.jpg",
            "boss.jpeg",
            "tool.gif",
            "path/to/image.png"
        ]
        
        for path in valid_paths:
            assert is_valid_image_path(path) is True

    def test_is_valid_image_path_invalid(self):
        """Test invalid image path validation."""
        invalid_paths = [
            "image.txt",
            "document.pdf",
            "../image.png",  # Path traversal
            "../../../etc/passwd",
            "image",  # No extension
            ""
        ]
        
        for path in invalid_paths:
            assert is_valid_image_path(path) is False

    def test_find_closest_match_exact(self):
        """Test finding exact matches."""
        choices = ["alex", "david", "mikey", "alexrot"]
        
        result = find_closest_match("alex", choices)
        assert result == "alex"

    def test_find_closest_match_fuzzy(self):
        """Test finding fuzzy matches."""
        choices = ["alex", "david", "mikey", "alexrot"]
        
        # Test exact match
        result = find_closest_match("alexrot", choices, threshold=80)
        assert result == "alexrot"
        
        # Test fuzzy match with typo
        result = find_closest_match("alexr0t", choices, threshold=70)
        assert result == "alexrot"

    def test_find_closest_match_no_match(self):
        """Test when no match meets threshold."""
        choices = ["alex", "david", "mikey"]
        
        result = find_closest_match("completely_different", choices)
        assert result is None

    def test_find_closest_match_case_insensitive(self):
        """Test that matching is case insensitive."""
        choices = ["Alex", "David", "Mikey"]
        
        result = find_closest_match("alex", choices)
        assert result == "Alex"

    def test_find_closest_match_custom_threshold(self):
        """Test custom threshold for matching."""
        choices = ["alex", "david", "mikey"]
        
        # With high threshold, should find no match
        result = find_closest_match("al", choices, threshold=95)
        assert result is None
        
        # With low threshold, should find match
        result = find_closest_match("al", choices, threshold=50)
        assert result == "alex"

    def test_find_closest_match_empty_choices(self):
        """Test with empty choices list."""
        result = find_closest_match("alex", [])
        assert result is None

    def test_find_closest_match_empty_query(self):
        """Test with empty query."""
        choices = ["alex", "david", "mikey"]
        
        result = find_closest_match("", choices)
        assert result is None
