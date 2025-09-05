"""Tests for utility functions and helper methods."""

import pytest
import os
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

from utils.helpers import (
    get_random_file, 
    get_image_extension, 
    find_closest_match,
    is_valid_image_path
)


class TestFileUtilities:
    """Test file-related utility functions."""

    def test_get_random_file_success(self, temp_assets_dir):
        """Test getting random file from directory."""
        # Create test files
        test_files = ["char1.png", "char2.jpg", "char3.gif", "doc.txt"]
        for filename in test_files:
            (temp_assets_dir / "characters" / filename).touch()
        
        # Test with default extensions (should only get image files)
        result = get_random_file(temp_assets_dir / "characters")
        
        assert result in ["char1.png", "char2.jpg", "char3.gif"]
        assert result != "doc.txt"

    def test_get_random_file_custom_extensions(self, temp_assets_dir):
        """Test getting random file with custom extensions."""
        # Create test files
        test_files = ["file1.txt", "file2.doc", "file3.pdf"]
        for filename in test_files:
            (temp_assets_dir / "characters" / filename).touch()
        
        result = get_random_file(temp_assets_dir / "characters", (".txt", ".doc"))
        
        assert result in ["file1.txt", "file2.doc"]
        assert result != "file3.pdf"

    def test_get_random_file_empty_directory(self, temp_assets_dir):
        """Test getting random file from empty directory."""
        with pytest.raises(FileNotFoundError):
            get_random_file(temp_assets_dir / "characters")

    def test_get_random_file_no_matching_extensions(self, temp_assets_dir):
        """Test getting random file when no files match extensions."""
        # Create only .txt files
        (temp_assets_dir / "characters" / "file.txt").touch()
        
        with pytest.raises(FileNotFoundError):
            get_random_file(temp_assets_dir / "characters", (".png", ".jpg"))

    def test_get_image_extension_png(self):
        """Test getting PNG extension."""
        result = get_image_extension("image.png")
        assert result == ".png"

    def test_get_image_extension_jpg(self):
        """Test getting JPG extension."""
        result = get_image_extension("image.jpg")
        assert result == ".jpg"

    def test_get_image_extension_jpeg(self):
        """Test getting JPEG extension."""
        result = get_image_extension("image.jpeg")
        assert result == ".jpeg"

    def test_get_image_extension_gif(self):
        """Test getting GIF extension."""
        result = get_image_extension("image.gif")
        assert result == ".gif"

    def test_get_image_extension_no_extension(self):
        """Test getting extension from filename without extension."""
        result = get_image_extension("image")
        assert result == ""

    def test_get_image_extension_unknown_extension(self):
        """Test getting extension from filename with unknown extension."""
        result = get_image_extension("image.txt")
        assert result == ""

    def test_get_image_extension_case_sensitive(self):
        """Test that extension matching is case sensitive."""
        result = get_image_extension("image.PNG")
        assert result == ""  # Should not match uppercase

    def test_is_valid_image_path_valid(self):
        """Test valid image path validation."""
        valid_paths = [
            "image.png",
            "character.jpg",
            "boss.jpeg",
            "tool.gif",
            "path/to/image.png",
            "nested/path/to/character.jpg"
        ]
        
        for path in valid_paths:
            assert is_valid_image_path(path) is True

    def test_is_valid_image_path_invalid_extension(self):
        """Test invalid image path with wrong extension."""
        invalid_paths = [
            "image.txt",
            "document.pdf",
            "script.py",
            "data.json"
        ]
        
        for path in invalid_paths:
            assert is_valid_image_path(path) is False

    def test_is_valid_image_path_path_traversal(self):
        """Test invalid image path with path traversal."""
        invalid_paths = [
            "../image.png",
            "../../../etc/passwd",
            "..\\image.png",
            "..\\..\\image.png"
        ]
        
        for path in invalid_paths:
            assert is_valid_image_path(path) is False

    def test_is_valid_image_path_empty(self):
        """Test empty path validation."""
        assert is_valid_image_path("") is False

    def test_is_valid_image_path_no_extension(self):
        """Test path without extension."""
        assert is_valid_image_path("image") is False


class TestStringUtilities:
    """Test string-related utility functions."""

    def test_find_closest_match_exact_match(self):
        """Test finding exact matches."""
        choices = ["alex", "david", "mikey", "alexrot", "davidson"]
        
        result = find_closest_match("alex", choices)
        assert result == "alex"

    def test_find_closest_match_close_match(self):
        """Test finding close matches."""
        choices = ["alex", "david", "mikey", "alexrot"]
        
        result = find_closest_match("alexr", choices)
        assert result == "alexrot"

    def test_find_closest_match_no_good_match(self):
        """Test when no match meets threshold."""
        choices = ["alex", "david", "mikey"]
        
        result = find_closest_match("completely_different", choices)
        assert result is None

    def test_find_closest_match_case_insensitive(self):
        """Test that matching is case insensitive."""
        choices = ["Alex", "David", "Mikey", "AlexRot"]
        
        result = find_closest_match("alex", choices)
        assert result == "Alex"

    def test_find_closest_match_custom_threshold_high(self):
        """Test with high threshold (should find fewer matches)."""
        choices = ["alex", "david", "mikey"]
        
        result = find_closest_match("al", choices, threshold=95)
        assert result is None

    def test_find_closest_match_custom_threshold_low(self):
        """Test with low threshold (should find more matches)."""
        choices = ["alex", "david", "mikey"]
        
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

    def test_find_closest_match_single_choice(self):
        """Test with single choice."""
        choices = ["alex"]
        
        result = find_closest_match("alex", choices)
        assert result == "alex"

    def test_find_closest_match_special_characters(self):
        """Test with special characters in choices."""
        choices = ["alex-rot", "david_smith", "mikey.jones"]
        
        result = find_closest_match("alexrot", choices)
        assert result == "alex-rot"

    def test_find_closest_match_unicode(self):
        """Test with unicode characters."""
        choices = ["café", "naïve", "résumé"]
        
        result = find_closest_match("cafe", choices)
        assert result == "café"


class TestRollingFunctions:
    """Test character and tool rolling functions."""

    @patch('utils.helpers.storage')
    @patch('utils.helpers.get_random_file')
    def test_roll_character_revealed_only(self, mock_get_random_file, mock_storage):
        """Test rolling character with revealed_only=True."""
        from utils.helpers import roll_character
        
        # Mock storage to return character with count > 0
        mock_char_stats = Mock()
        mock_char_stats.count = 5
        mock_storage.get_character_stats.return_value = mock_char_stats
        mock_get_random_file.return_value = "alex.jpg"
        
        result = roll_character(revealed_only=True)
        
        assert result == "alex.jpg"
        mock_get_random_file.assert_called_once()

    @patch('utils.helpers.storage')
    @patch('utils.helpers.get_random_file')
    def test_roll_character_not_revealed(self, mock_get_random_file, mock_storage):
        """Test rolling character that hasn't been revealed yet."""
        from utils.helpers import roll_character
        
        # Mock storage to return character with count = 0
        mock_char_stats = Mock()
        mock_char_stats.count = 0
        mock_storage.get_character_stats.return_value = mock_char_stats
        mock_get_random_file.return_value = "alex.jpg"
        
        # Should keep trying until it finds a revealed character
        # For this test, we'll mock it to eventually return a revealed one
        mock_char_stats_revealed = Mock()
        mock_char_stats_revealed.count = 3
        
        def side_effect(name):
            if name == "alex":
                return mock_char_stats
            else:
                return mock_char_stats_revealed
        
        mock_storage.get_character_stats.side_effect = side_effect
        mock_get_random_file.side_effect = ["alex.jpg", "david.jpg"]
        
        result = roll_character(revealed_only=True)
        
        assert result == "david.jpg"

    @patch('utils.helpers.storage')
    @patch('utils.helpers.get_random_file')
    def test_roll_tool_success(self, mock_get_random_file, mock_storage):
        """Test rolling tool successfully."""
        from utils.helpers import roll_tool
        
        mock_storage.tool_stats = {"sword": Mock()}
        mock_get_random_file.return_value = "sword.jpg"
        
        result = roll_tool()
        
        assert result == "sword.jpg"

    @patch('utils.helpers.storage')
    @patch('utils.helpers.get_random_file')
    def test_roll_tool_not_in_stats(self, mock_get_random_file, mock_storage):
        """Test rolling tool that's not in tool_stats."""
        from utils.helpers import roll_tool
        
        mock_storage.tool_stats = {"sword": Mock()}
        mock_get_random_file.side_effect = ["invalid_tool.jpg", "sword.jpg"]
        
        result = roll_tool()
        
        assert result == "sword.jpg"
        assert mock_get_random_file.call_count == 2

    @patch('utils.helpers.storage')
    @patch('utils.helpers.get_random_file')
    def test_roll_boss_campaign_mode(self, mock_get_random_file, mock_storage):
        """Test rolling boss in campaign mode."""
        from utils.helpers import roll_boss
        
        # Mock server stats
        mock_server_stats = Mock()
        mock_server_stats.campaign = "david"
        mock_storage.get_server_stats.return_value = mock_server_stats
        
        result = roll_boss("campaign", "testserver")
        
        assert result == "david.jpg"

    @patch('utils.helpers.storage')
    @patch('utils.helpers.get_random_file')
    def test_roll_boss_campaign_complete(self, mock_get_random_file, mock_storage):
        """Test rolling boss when campaign is complete."""
        from utils.helpers import roll_boss
        
        # Mock server stats with completed campaign
        mock_server_stats = Mock()
        mock_server_stats.campaign = "COMPLETE"
        mock_server_stats.campaign_completed = 3  # Odd number
        mock_storage.get_server_stats.return_value = mock_server_stats
        
        result = roll_boss("campaign", "testserver")
        
        assert result == "Tipp Tronix.jpg"

    @patch('utils.helpers.storage')
    @patch('utils.helpers.get_random_file')
    def test_roll_boss_classic_mode(self, mock_get_random_file, mock_storage):
        """Test rolling boss in classic mode."""
        from utils.helpers import roll_boss
        
        # Mock boss stats
        mock_boss_stats = Mock()
        mock_boss_stats.times_defeated = 5
        mock_storage.get_boss_stats.return_value = mock_boss_stats
        mock_get_random_file.return_value = "david.jpg"
        
        result = roll_boss("classic", "testserver")
        
        assert result == "david.jpg"
