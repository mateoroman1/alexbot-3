"""Test configuration and fixtures for AlexBot tests."""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
from typing import Dict, Any

from data.models import CharacterStats, BossStats, ToolStats, UserStats, ServerStats
from data.storage import DataStorage


@pytest.fixture
def temp_data_dir():
    """Create a temporary directory for test data files."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_storage(temp_data_dir):
    """Create a DataStorage instance with temporary data files."""
    with patch('data.storage.CHARACTER_STATS_FILE', temp_data_dir / "character_stats.json"), \
         patch('data.storage.BOSS_STATS_FILE', temp_data_dir / "boss_stats.json"), \
         patch('data.storage.TOOL_STATS_FILE', temp_data_dir / "tool_stats.json"), \
         patch('data.storage.USER_STATS_FILE', temp_data_dir / "user_stats.json"), \
         patch('data.storage.SERVER_STATS_FILE', temp_data_dir / "server_stats.json"):
        
        storage = DataStorage()
        yield storage


@pytest.fixture
def sample_character_stats():
    """Sample character stats for testing."""
    return {
        "alex": CharacterStats(count=5, group="alex", raids_won=2, raids_completed=3),
        "david": CharacterStats(count=3, group="classics", raids_won=1, raids_completed=2),
        "mikey": CharacterStats(count=7, group="alex", raids_won=0, raids_completed=1),
    }


@pytest.fixture
def sample_boss_stats():
    """Sample boss stats for testing."""
    return {
        "david": BossStats(health=100.0, weakness="alex", times_defeated=5, times_won=2),
        "alexrot": BossStats(health=150.0, weakness="classics", times_defeated=1, times_won=3),
    }


@pytest.fixture
def sample_tool_stats():
    """Sample tool stats for testing."""
    return {
        "sword": ToolStats(default_multiplier=1.5, group="warriors", character_multipliers={"alex": 2.0}),
        "staff": ToolStats(default_multiplier=1.2, group="magic entities", character_multipliers={}),
    }


@pytest.fixture
def sample_user_stats():
    """Sample user stats for testing."""
    return {
        "testuser1": UserStats(total_rolls=10, raid_wins=3, total_raids=5, pvp_wins=2),
        "testuser2": UserStats(total_rolls=5, raid_wins=1, total_raids=2, pvp_wins=0),
    }


@pytest.fixture
def sample_server_stats():
    """Sample server stats for testing."""
    return {
        "testserver": ServerStats(
            total_rolls=15, 
            raid_wins=4, 
            total_raids=7, 
            campaign="david",
            campaign_completed=1
        ),
    }


@pytest.fixture
def populated_storage(mock_storage, sample_character_stats, sample_boss_stats, 
                     sample_tool_stats, sample_user_stats, sample_server_stats):
    """Storage instance populated with sample data."""
    storage = mock_storage
    
    # Populate with sample data
    storage.character_stats.update(sample_character_stats)
    storage.boss_stats.update(sample_boss_stats)
    storage.tool_stats.update(sample_tool_stats)
    storage.user_stats.update(sample_user_stats)
    storage.server_stats.update(sample_server_stats)
    
    return storage


@pytest.fixture
def mock_discord_context():
    """Mock Discord context for testing commands."""
    ctx = Mock()
    ctx.author = Mock()
    ctx.author.name = "testuser"
    ctx.author.id = 12345
    ctx.guild = Mock()
    ctx.guild.name = "testserver"
    ctx.channel = Mock()
    ctx.send = Mock()
    return ctx


@pytest.fixture
def mock_discord_interaction():
    """Mock Discord interaction for testing slash commands."""
    interaction = Mock()
    interaction.user = Mock()
    interaction.user.name = "testuser"
    interaction.user.id = 12345
    interaction.guild = Mock()
    interaction.guild.name = "testserver"
    interaction.channel = Mock()
    interaction.response = Mock()
    interaction.followup = Mock()
    return interaction


@pytest.fixture
def mock_bot():
    """Mock Discord bot for testing."""
    bot = Mock()
    bot.loop = Mock()
    bot.loop.create_task = Mock()
    return bot


@pytest.fixture
def temp_assets_dir():
    """Create temporary assets directory for testing file operations."""
    temp_dir = tempfile.mkdtemp()
    assets_dir = Path(temp_dir) / "assets"
    assets_dir.mkdir()
    
    # Create subdirectories
    (assets_dir / "characters").mkdir()
    (assets_dir / "items").mkdir()
    (assets_dir / "bosses").mkdir()
    (assets_dir / "utility").mkdir()
    
    yield assets_dir
    shutil.rmtree(temp_dir)
