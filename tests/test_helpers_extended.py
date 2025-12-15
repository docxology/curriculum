"""Extended tests for utils.helpers module to improve coverage."""

import pytest
from pathlib import Path
from datetime import datetime
from src.utils.helpers import (
    ensure_directory,
    slugify,
    save_markdown,
    load_markdown,
    format_timestamp,
    sanitize_filename,
    format_module_filename,
)


class TestFormatModuleFilename:
    """Test format_module_filename function."""
    
    def test_format_module_filename_simple(self):
        """Test formatting module filename without suffix."""
        filename = format_module_filename(
            module_id=1,
            module_name="Cell Biology"
        )
        
        assert "module_01" in filename or "01" in filename
        assert "cell" in filename.lower() or "biology" in filename.lower()
        assert filename.endswith(".md")
        
    def test_format_module_filename_with_suffix(self):
        """Test formatting module filename with suffix."""
        filename = format_module_filename(
            module_id=5,
            module_name="Genetics and Heredity",
            suffix="lecture"
        )
        
        assert "05" in filename or "5" in filename
        assert "genetics" in filename.lower() or "heredity" in filename.lower()
        assert "lecture" in filename.lower()
        
    def test_format_module_filename_special_chars(self):
        """Test formatting with special characters in name."""
        filename = format_module_filename(
            module_id=10,
            module_name="DNA & RNA: Structure!",
            suffix="notes"
        )
        
        assert "10" in filename
        # Special characters should be handled
        assert filename.endswith(".md")


class TestTimestampFormatting:
    """Test timestamp formatting edge cases."""
    
    def test_format_timestamp_with_datetime(self):
        """Test timestamp with specific datetime."""
        dt = datetime(2024, 1, 15, 14, 30, 45)
        formatted = format_timestamp(dt)
        
        # Should contain date information
        assert "2024" in formatted or "20240115" in formatted
        
    def test_format_timestamp_current(self):
        """Test timestamp with current time (None)."""
        formatted = format_timestamp(None)
        
        # Should be a non-empty string
        assert isinstance(formatted, str)
        assert len(formatted) > 0


class TestSanitizeFilenameEdgeCases:
    """Test edge cases for sanitize_filename."""
    
    def test_sanitize_filename_unicode(self):
        """Test sanitizing filename with unicode characters."""
        filename = "résumé_données.txt"
        sanitized = sanitize_filename(filename)
        
        # Should handle unicode appropriately
        assert sanitized.endswith(".txt")
        
    def test_sanitize_filename_multiple_dots(self):
        """Test filename with multiple dots."""
        filename = "test.file.name.md"
        sanitized = sanitize_filename(filename)
        
        assert sanitized.endswith(".md")
        
    def test_sanitize_filename_empty_extension(self):
        """Test filename with no extension."""
        filename = "noextension"
        sanitized = sanitize_filename(filename)
        
        assert sanitized == "noextension"


# PHASE 1: Additional Helper Tests for Extended Coverage

class TestSlugifyUnicode:
    """Test slugify with unicode characters."""
    
    def test_slugify_unicode_to_ascii(self):
        """Test slugify converts unicode to ASCII equivalents."""
        # French characters
        assert "resume" in slugify("Résumé").lower() or "r_sum_" in slugify("Résumé")
        
        # German characters
        result = slugify("Über die Zelle")
        assert "ber" in result.lower() or "uber" in result.lower()
        
        # Should not crash with any unicode
        result = slugify("细胞生物学")  # Chinese
        assert isinstance(result, str)
    
    def test_slugify_mixed_unicode_ascii(self):
        """Test slugify with mixed unicode and ASCII."""
        result = slugify("Cell Biología 101")
        assert "cell" in result.lower()
        assert "101" in result


class TestErrorRecovery:
    """Test error recovery scenarios."""
    
    def test_load_markdown_corrupted_encoding(self, tmp_path):
        """Test loading file with encoding issues."""
        filepath = tmp_path / "corrupted.md"
        # Write binary data that's not valid UTF-8
        filepath.write_bytes(b'\x80\x81\x82\x83')
        
        # Should handle encoding error gracefully
        with pytest.raises((UnicodeDecodeError, OSError)):
            load_markdown(filepath)
    
    def test_ensure_directory_with_file_conflict(self, tmp_path):
        """Test ensure_directory when path exists as file."""
        # Create a file where directory is expected
        conflict_path = tmp_path / "conflict"
        conflict_path.write_text("I am a file")
        
        # Attempting to create directory should fail or handle gracefully
        with pytest.raises((FileExistsError, OSError, Exception)):
            ensure_directory(conflict_path)


class TestTimezoneHandling:
    """Test timestamp formatting with timezones."""
    
    def test_format_timestamp_timezone_aware(self):
        """Test format_timestamp with timezone-aware datetime."""
        from datetime import timezone, timedelta
        
        # Create timezone-aware datetime
        tz = timezone(timedelta(hours=5))
        dt = datetime(2024, 6, 15, 10, 30, 0, tzinfo=tz)
        
        result = format_timestamp(dt)
        
        # Should format without crashing
        assert isinstance(result, str)
        assert "2024" in result
    
    def test_format_timestamp_naive_datetime(self):
        """Test format_timestamp with naive (no timezone) datetime."""
        dt = datetime(2024, 6, 15, 10, 30, 0)
        
        result = format_timestamp(dt)
        
        assert isinstance(result, str)
        assert "2024" in result
