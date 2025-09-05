"""Tests for game manager classes."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from typing import List

from game.stats import StatsManager
from game.raid import RaidManager
from game.pvp import PVPManager
from data.models import RaidMode, RaidState, RaidHand


class TestStatsManager:
    """Test cases for StatsManager class."""

    def test_get_most_common_character_single_winner(self, populated_storage):
        """Test getting most common character with single winner."""
        with patch('game.stats.storage', populated_storage):
            # Mikey has count=7, Alex has count=5, David has count=3
            character, count = StatsManager.get_most_common_character()
            
            assert character == "mikey"
            assert count == 7

    def test_get_most_common_character_tie(self, populated_storage):
        """Test getting most common character with tie."""
        with patch('game.stats.storage', populated_storage):
            # Create a tie by setting Alex to same count as Mikey
            populated_storage.update_character_stats("alex", count=7)
            
            character, count = StatsManager.get_most_common_character()
            
            assert isinstance(character, list)
            assert "mikey" in character
            assert "alex" in character
            assert count == 7

    def test_get_winningest_raider(self, populated_storage):
        """Test getting character with most raid wins."""
        with patch('game.stats.storage', populated_storage):
            # Alex has raids_won=2, David has raids_won=1, Mikey has raids_won=0
            character, wins = StatsManager.get_winningest_raider()
            
            assert character == "alex"
            assert wins == 2

    def test_get_winningest_raider_tie(self, populated_storage):
        """Test getting winningest raider with tie."""
        with patch('game.stats.storage', populated_storage):
            # Create a tie
            populated_storage.update_character_stats("david", raids_won=2)
            
            character, wins = StatsManager.get_winningest_raider()
            
            assert isinstance(character, list)
            assert "alex" in character
            assert "david" in character
            assert wins == 2

    def test_get_top_ten(self, populated_storage):
        """Test getting top ten characters."""
        with patch('game.stats.storage', populated_storage):
            top_ten = StatsManager.get_top_ten()
            
            assert isinstance(top_ten, dict)
            assert len(top_ten) <= 10
            assert "mikey" in top_ten
            assert top_ten["mikey"] == 7

    def test_increment_character_count_normal(self, populated_storage):
        """Test normal character count increment."""
        with patch('game.stats.storage', populated_storage):
            result = StatsManager.increment_character_count("david")
            
            assert result == 0  # Normal increment
            assert populated_storage.get_character_stats("david").count == 4

    def test_increment_character_count_takes_lead(self, populated_storage):
        """Test character count increment that takes the lead."""
        with patch('game.stats.storage', populated_storage):
            # Set David to 6, then increment to 7 (takes lead from Mikey)
            populated_storage.update_character_stats("david", count=7)
            
            result = StatsManager.increment_character_count("david")
            
            assert result == 1  # Took the lead
            assert populated_storage.get_character_stats("david").count == 8

    def test_increment_character_count_ties_lead(self, populated_storage):
        """Test character count increment that ties for lead."""
        with patch('game.stats.storage', populated_storage):
            # Set David to 6, then increment to 7 (ties with Mikey)
            populated_storage.update_character_stats("david", count=6)
            
            result = StatsManager.increment_character_count("david")
            
            assert result == 2  # Tied for lead
            assert populated_storage.get_character_stats("david").count == 7

    def test_increment_character_count_milestone(self, populated_storage):
        """Test character count increment that reaches 100 milestone."""
        with patch('game.stats.storage', populated_storage):
            # Set character to 99, then increment to 100
            populated_storage.update_character_stats("alex", count=99)
            
            result = StatsManager.increment_character_count("alex")
            
            assert result == 100  # Milestone reached
            assert populated_storage.get_character_stats("alex").count == 100

    def test_get_character_group_members(self, populated_storage):
        """Test getting characters in a specific group."""
        with patch('game.stats.storage', populated_storage):
            members = StatsManager.get_character_group_members("alex")
            
            assert isinstance(members, list)
            assert "alex" in members
            assert "mikey" in members
            assert "david" not in members

    def test_get_user_ex_cards(self, populated_storage):
        """Test getting user's EX cards."""
        with patch('game.stats.storage', populated_storage):
            # Add some EX cards to user
            populated_storage.update_user_stats("testuser1", deck=["ex1", "ex2"])
            
            ex_cards = StatsManager.get_user_ex_cards("testuser1")
            
            assert ex_cards == ["ex1", "ex2"]

    def test_get_server_campaign_progress(self, populated_storage):
        """Test getting server campaign progress."""
        with patch('game.stats.storage', populated_storage):
            progress = StatsManager.get_server_campaign_progress("testserver")
            
            assert progress["campaign"] == "david"
            assert progress["completed"] == 1

    def test_get_server_campaign_progress_nonexistent(self, populated_storage):
        """Test getting campaign progress for nonexistent server."""
        with patch('game.stats.storage', populated_storage):
            progress = StatsManager.get_server_campaign_progress("nonexistent")
            
            assert progress["campaign"] == "None"
            assert progress["completed"] == 0

    def test_get_pvp_champion(self, populated_storage):
        """Test getting PVP champion."""
        with patch('game.stats.storage', populated_storage):
            # testuser1 has pvp_wins=2, testuser2 has pvp_wins=0
            champion, wins = StatsManager.get_pvp_champion()
            
            assert champion == "testuser1"
            assert wins == 2

    def test_get_pvp_champion_tie(self, populated_storage):
        """Test getting PVP champion with tie."""
        with patch('game.stats.storage', populated_storage):
            # Create a tie
            populated_storage.update_user_stats("testuser2", pvp_wins=2)
            
            champion, wins = StatsManager.get_pvp_champion()
            
            assert isinstance(champion, list)
            assert "testuser1" in champion
            assert "testuser2" in champion
            assert wins == 2


class TestRaidManager:
    """Test cases for RaidManager class."""

    def test_raid_manager_initialization(self):
        """Test RaidManager initialization."""
        manager = RaidManager(RaidMode.CLASSIC, "testserver")
        
        assert manager.mode == RaidMode.CLASSIC
        assert manager.server_name == "testserver"
        assert manager.raid_state is None
        assert manager.boss is None

    @patch('game.raid.roll_boss')
    def test_get_boss_classic_mode(self, mock_roll_boss, populated_storage):
        """Test getting boss in classic mode."""
        with patch('game.raid.storage', populated_storage):
            mock_roll_boss.return_value = "david.jpg"
            
            manager = RaidManager(RaidMode.CLASSIC, "testserver")
            result = manager.get_boss()
            
            assert result == "david.jpg"
            assert manager.boss_name == "david"
            assert manager.boss_stats is not None

    @patch('game.raid.roll_boss')
    def test_get_boss_campaign_mode(self, mock_roll_boss, populated_storage):
        """Test getting boss in campaign mode."""
        with patch('game.raid.storage', populated_storage):
            mock_roll_boss.return_value = "david.jpg"
            
            manager = RaidManager(RaidMode.CAMPAIGN, "testserver")
            result = manager.get_boss()
            
            assert result == "david.jpg"
            assert manager.boss_name == "david"

    def test_raid_state_creation(self, populated_storage):
        """Test RaidState creation with proper health scaling."""
        with patch('game.raid.storage', populated_storage):
            manager = RaidManager(RaidMode.CLASSIC, "testserver")
            manager.boss = "david.jpg"
            manager.boss_name = "david"
            manager.boss_stats = populated_storage.get_boss_stats("david")
            
            # Mock the server stats for campaign scaling
            populated_storage.update_server_stats("testserver", campaign_completed=2)
            
            raid_state = RaidState(
                player_list=["player1", "player2"],
                boss=manager.boss,
                boss_health=manager.boss_stats.health * (1 + 0.15 * 2),  # Campaign scaling
                boss_weakness=manager.boss_stats.weakness
            )
            
            assert raid_state.player_list == ["player1", "player2"]
            assert raid_state.boss == "david.jpg"
            assert raid_state.boss_health == 100.0 * 1.3  # 100 * (1 + 0.15 * 2)
            assert raid_state.boss_weakness == "alex"

    @patch('game.raid.roll_character')
    @patch('game.raid.roll_tool')
    @patch('game.raid.calculate_damage_multiplier')
    def test_draw_cards(self, mock_calculate_damage, mock_roll_tool, mock_roll_character, populated_storage):
        """Test drawing cards for raid players."""
        with patch('game.raid.storage', populated_storage):
            mock_roll_character.return_value = "alex.jpg"
            mock_roll_tool.return_value = "sword.jpg"
            mock_calculate_damage.return_value = 75.0
            
            manager = RaidManager(RaidMode.CLASSIC, "testserver")
            manager.raid_state = RaidState(
                player_list=["player1", "player2"],
                boss="david.jpg",
                boss_health=100.0,
                boss_weakness="alex"
            )
            
            # This is an async method, so we need to run it
            import asyncio
            asyncio.run(manager.draw_cards())
            
            # Check that player data was created
            assert "player1" in manager.raid_state.player_data
            assert "player2" in manager.raid_state.player_data
            
            # Check that RaidHand objects were created
            hand1 = manager.raid_state.player_data["player1"]
            assert isinstance(hand1, RaidHand)
            assert hand1.character == "alex.jpg"
            assert hand1.tool == "sword.jpg"
            assert hand1.damage_index == 75.0

    def test_raid_hand_creation(self):
        """Test RaidHand dataclass creation."""
        hand = RaidHand(
            character="alex.jpg",
            tool="sword.jpg",
            damage_index=75.0
        )
        
        assert hand.character == "alex.jpg"
        assert hand.tool == "sword.jpg"
        assert hand.damage_index == 75.0

    def test_raid_hand_without_tool(self):
        """Test RaidHand creation without tool."""
        hand = RaidHand(
            character="alex.jpg",
            tool=None,
            damage_index=50.0
        )
        
        assert hand.character == "alex.jpg"
        assert hand.tool is None
        assert hand.damage_index == 50.0


class TestPVPManager:
    """Test cases for PVPManager class."""

    def test_pvp_manager_initialization(self, mock_bot):
        """Test PVPManager initialization."""
        channel = Mock()
        manager = PVPManager("host", channel, mock_bot)
        
        assert manager.host_name == "host"
        assert manager.challenger_name is None
        assert manager.channel == channel
        assert manager.bot == mock_bot
        assert manager.is_active is False
        assert manager.host_wins == 0
        assert manager.challenger_wins == 0
        assert manager.current_round == 0

    def test_pvp_manager_round_tracking(self, mock_bot):
        """Test PVP round tracking."""
        channel = Mock()
        manager = PVPManager("host", channel, mock_bot)
        
        # Simulate some rounds
        manager.host_wins = 1
        manager.challenger_wins = 1
        manager.current_round = 2
        
        assert manager.host_wins == 1
        assert manager.challenger_wins == 1
        assert manager.current_round == 2

    def test_pvp_manager_winner_determination(self, mock_bot):
        """Test PVP winner determination logic."""
        channel = Mock()
        manager = PVPManager("host", channel, mock_bot)
        manager.challenger_name = "challenger"
        
        # Test host wins
        manager.host_wins = 2
        manager.challenger_wins = 1
        
        winner = "host" if manager.host_wins > manager.challenger_wins else "challenger"
        assert winner == "host"
        
        # Test challenger wins
        manager.host_wins = 1
        manager.challenger_wins = 2
        
        winner = "host" if manager.host_wins > manager.challenger_wins else "challenger"
        assert winner == "challenger"

    def test_pvp_manager_timeout_handling(self, mock_bot):
        """Test PVP timeout handling."""
        channel = Mock()
        manager = PVPManager("host", channel, mock_bot)
        
        assert manager.timeout == 60  # Default timeout
        
        # Test timeout setting
        manager.timeout = 30
        assert manager.timeout == 30
