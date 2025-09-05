"""Tests for the DataStorage class and its methods."""

import pytest
import json
from pathlib import Path
from unittest.mock import patch, mock_open

from data.storage import DataStorage
from data.models import CharacterStats, BossStats, ToolStats, UserStats, ServerStats


class TestDataStorage:
    """Test cases for DataStorage class."""

    def test_storage_initialization(self, mock_storage):
        """Test that storage initializes with empty dictionaries."""
        storage = mock_storage
        assert isinstance(storage.character_stats, dict)
        assert isinstance(storage.boss_stats, dict)
        assert isinstance(storage.tool_stats, dict)
        assert isinstance(storage.user_stats, dict)
        assert isinstance(storage.server_stats, dict)

    def test_get_character_stats_creates_new(self, mock_storage):
        """Test that get_character_stats creates new stats if they don't exist."""
        storage = mock_storage
        stats = storage.get_character_stats("newcharacter")
        
        assert isinstance(stats, CharacterStats)
        assert stats.count == 0
        assert stats.group == "_unsorted"
        assert "newcharacter" in storage.character_stats

    def test_get_character_stats_case_folding(self, mock_storage):
        """Test that character names are properly case-folded."""
        storage = mock_storage
        stats1 = storage.get_character_stats("ALEX")
        stats2 = storage.get_character_stats("alex")
        stats3 = storage.get_character_stats("Alex")
        
        assert stats1 is stats2 is stats3
        assert "alex" in storage.character_stats

    def test_get_boss_stats_creates_new(self, mock_storage):
        """Test that get_boss_stats creates new stats if they don't exist."""
        storage = mock_storage
        stats = storage.get_boss_stats("newboss")
        
        assert isinstance(stats, BossStats)
        assert stats.health == 0.0
        assert stats.weakness == ""
        assert "newboss" in storage.boss_stats

    def test_get_user_stats_creates_new(self, mock_storage):
        """Test that get_user_stats creates new stats if they don't exist."""
        storage = mock_storage
        stats = storage.get_user_stats("newuser")
        
        assert isinstance(stats, UserStats)
        assert stats.total_rolls == 0
        assert stats.raid_wins == 0
        assert "newuser" in storage.user_stats

    def test_get_server_stats_creates_new(self, mock_storage):
        """Test that get_server_stats creates new stats if they don't exist."""
        storage = mock_storage
        stats = storage.get_server_stats("newserver")
        
        assert isinstance(stats, ServerStats)
        assert stats.total_rolls == 0
        assert stats.active_raid is False
        assert "newserver" in storage.server_stats

    def test_increment_user_stat(self, populated_storage):
        """Test incrementing user stats."""
        storage = populated_storage
        initial_rolls = storage.get_user_stats("testuser1").total_rolls
        
        storage.increment_user_stat("testuser1", "total_rolls", 5)
        
        updated_stats = storage.get_user_stats("testuser1")
        assert updated_stats.total_rolls == initial_rolls + 5

    def test_increment_character_stat(self, populated_storage):
        """Test incrementing character stats."""
        storage = populated_storage
        initial_count = storage.get_character_stats("alex").count
        
        storage.increment_character_stat("alex", "count", 3)
        
        updated_stats = storage.get_character_stats("alex")
        assert updated_stats.count == initial_count + 3

    def test_increment_server_stat(self, populated_storage):
        """Test incrementing server stats."""
        storage = populated_storage
        initial_raids = storage.get_server_stats("testserver").total_raids
        
        storage.increment_server_stat("testserver", "total_raids", 2)
        
        updated_stats = storage.get_server_stats("testserver")
        assert updated_stats.total_raids == initial_raids + 2

    def test_increment_boss_stat(self, populated_storage):
        """Test incrementing boss stats."""
        storage = populated_storage
        initial_defeated = storage.get_boss_stats("david").times_defeated
        
        storage.increment_boss_stat("david", "times_defeated", 1)
        
        updated_stats = storage.get_boss_stats("david")
        assert updated_stats.times_defeated == initial_defeated + 1

    def test_increment_nonexistent_field(self, populated_storage):
        """Test that incrementing non-existent fields doesn't cause errors."""
        storage = populated_storage
        
        # Should not raise an exception
        storage.increment_user_stat("testuser1", "nonexistent_field", 5)
        
        # Stats should remain unchanged
        stats = storage.get_user_stats("testuser1")
        assert not hasattr(stats, "nonexistent_field")

    def test_update_character_stats(self, populated_storage):
        """Test updating character stats with multiple fields."""
        storage = populated_storage
        
        storage.update_character_stats("alex", count=10, group="newgroup", raids_won=5)
        
        stats = storage.get_character_stats("alex")
        assert stats.count == 10
        assert stats.group == "newgroup"
        assert stats.raids_won == 5

    def test_update_user_stats(self, populated_storage):
        """Test updating user stats with multiple fields."""
        storage = populated_storage
        
        storage.update_user_stats("testuser1", total_rolls=20, raid_wins=8, cursed=True)
        
        stats = storage.get_user_stats("testuser1")
        assert stats.total_rolls == 20
        assert stats.raid_wins == 8
        assert stats.cursed is True

    def test_save_and_load_cycle(self, temp_data_dir):
        """Test that data persists correctly through save/load cycle."""
        # Create storage with temporary files
        with patch('data.storage.CHARACTER_STATS_FILE', temp_data_dir / "character_stats.json"), \
             patch('data.storage.BOSS_STATS_FILE', temp_data_dir / "boss_stats.json"), \
             patch('data.storage.TOOL_STATS_FILE', temp_data_dir / "tool_stats.json"), \
             patch('data.storage.USER_STATS_FILE', temp_data_dir / "user_stats.json"), \
             patch('data.storage.SERVER_STATS_FILE', temp_data_dir / "server_stats.json"):
            
            # Create and populate storage
            storage1 = DataStorage()
            storage1.update_character_stats("testchar", count=5, group="testgroup")
            storage1.update_user_stats("testuser", total_rolls=10)
            storage1.save_all()
            
            # Create new storage instance and load data
            storage2 = DataStorage()
            
            # Verify data was loaded correctly
            char_stats = storage2.get_character_stats("testchar")
            user_stats = storage2.get_user_stats("testuser")
            
            assert char_stats.count == 5
            assert char_stats.group == "testgroup"
            assert user_stats.total_rolls == 10

    def test_load_nonexistent_files(self, temp_data_dir):
        """Test that storage handles missing data files gracefully."""
        with patch('data.storage.CHARACTER_STATS_FILE', temp_data_dir / "nonexistent.json"), \
             patch('data.storage.BOSS_STATS_FILE', temp_data_dir / "nonexistent.json"), \
             patch('data.storage.TOOL_STATS_FILE', temp_data_dir / "nonexistent.json"), \
             patch('data.storage.USER_STATS_FILE', temp_data_dir / "nonexistent.json"), \
             patch('data.storage.SERVER_STATS_FILE', temp_data_dir / "nonexistent.json"):
            
            # Should not raise an exception
            storage = DataStorage()
            
            # Should create empty dictionaries
            assert len(storage.character_stats) == 0
            assert len(storage.boss_stats) == 0
            assert len(storage.tool_stats) == 0
            assert len(storage.user_stats) == 0
            assert len(storage.server_stats) == 0

    def test_convert_dict_to_dataclass(self, mock_storage):
        """Test the _convert_dict_to_dataclass method."""
        storage = mock_storage
        
        # Test normal conversion
        data = {"count": 5, "group": "test", "raids_won": 2}
        result = storage._convert_dict_to_dataclass(data, CharacterStats)
        
        assert isinstance(result, CharacterStats)
        assert result.count == 5
        assert result.group == "test"
        assert result.raids_won == 2

    def test_convert_dict_with_extra_fields(self, mock_storage):
        """Test that extra fields in dict are ignored."""
        storage = mock_storage
        
        data = {"count": 5, "group": "test", "extra_field": "should_be_ignored"}
        result = storage._convert_dict_to_dataclass(data, CharacterStats)
        
        assert isinstance(result, CharacterStats)
        assert result.count == 5
        assert result.group == "test"
        assert not hasattr(result, "extra_field")
