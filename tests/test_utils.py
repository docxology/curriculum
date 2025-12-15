"""Tests for utils module."""

import pytest
from pathlib import Path
from src.utils.helpers import (
    ensure_directory,
    slugify,
    save_markdown,
    load_markdown,
    format_timestamp,
    sanitize_filename
)


class TestUtils:
    """Test utility functions."""
    
    def test_ensure_directory_creates_new(self, tmp_path):
        """Test creating a new directory."""
        new_dir = tmp_path / "test_dir"
        assert not new_dir.exists()
        
        result = ensure_directory(new_dir)
        
        assert new_dir.exists()
        assert new_dir.is_dir()
        assert result == new_dir
        
    def test_ensure_directory_existing(self, tmp_path):
        """Test with existing directory."""
        existing_dir = tmp_path / "existing"
        existing_dir.mkdir()
        
        result = ensure_directory(existing_dir)
        
        assert result == existing_dir
        assert existing_dir.exists()
        
    def test_slugify_simple(self):
        """Test slugify with simple text."""
        assert slugify("Hello World") == "hello_world"
        
    def test_slugify_special_chars(self):
        """Test slugify with special characters."""
        assert slugify("Cell Biology: Part 1") == "cell_biology_part_1"
        assert slugify("DNA & RNA") == "dna_rna"
        
    def test_slugify_multiple_spaces(self):
        """Test slugify with multiple spaces."""
        assert slugify("  Multiple   Spaces  ") == "multiple_spaces"
        
    def test_slugify_numbers(self):
        """Test slugify preserves numbers."""
        assert slugify("Module 01") == "module_01"
        
    def test_save_and_load_markdown(self, tmp_path):
        """Test saving and loading markdown files."""
        filepath = tmp_path / "test.md"
        content = "# Test Heading\n\nThis is a test."
        
        save_markdown(filepath, content)
        
        assert filepath.exists()
        loaded = load_markdown(filepath)
        assert loaded == content
        
    def test_save_markdown_creates_dirs(self, tmp_path):
        """Test that save_markdown creates parent directories."""
        filepath = tmp_path / "subdir" / "nested" / "test.md"
        content = "Test content"
        
        save_markdown(filepath, content)
        
        assert filepath.exists()
        assert filepath.read_text() == content
        
    def test_load_markdown_nonexistent(self, tmp_path):
        """Test loading nonexistent file raises error."""
        filepath = tmp_path / "nonexistent.md"
        
        with pytest.raises(FileNotFoundError):
            load_markdown(filepath)
            
    def test_format_timestamp(self):
        """Test timestamp formatting."""
        from datetime import datetime
        
        # Test with specific datetime
        dt = datetime(2024, 1, 15, 14, 30, 45)
        result = format_timestamp(dt)
        
        assert "2024" in result
        assert "01" in result or "15" in result
        
    def test_format_timestamp_current(self):
        """Test timestamp with current time."""
        result = format_timestamp()
        
        # Should return a string with current timestamp
        assert isinstance(result, str)
        assert len(result) > 0
        
    def test_sanitize_filename_simple(self):
        """Test sanitizing simple filenames."""
        assert sanitize_filename("test.txt") == "test.txt"
        
    def test_sanitize_filename_special_chars(self):
        """Test sanitizing with special characters."""
        assert sanitize_filename("test/file.txt") == "test_file.txt"
        assert sanitize_filename("bad:name.md") == "bad_name.md"
        
    def test_sanitize_filename_spaces(self):
        """Test sanitizing with spaces."""
        assert sanitize_filename("my file.txt") == "my_file.txt"
        
    def test_sanitize_filename_preserves_extension(self):
        """Test that file extension is preserved."""
        result = sanitize_filename("test file!.md")
        assert result.endswith(".md")
    
    # PHASE 1: Additional Helper Tests (32% → 90% coverage)
    
    def test_file_operation_permission_error(self, tmp_path):
        """Test handling of file permission errors."""
        import os
        import stat
        
        if os.name != 'nt':  # Skip on Windows
            # Create directory and make it read-only
            test_dir = tmp_path / "readonly"
            test_dir.mkdir()
            os.chmod(test_dir, stat.S_IRUSR | stat.S_IXUSR)  # Read + execute only
            
            try:
                filepath = test_dir / "test.md"
                # Should raise permission error
                with pytest.raises(PermissionError):
                    save_markdown(filepath, "test content")
            finally:
                # Restore permissions for cleanup
                os.chmod(test_dir, stat.S_IRWXU)
    
    def test_sanitize_path_traversal(self):
        """Test sanitize_filename prevents directory traversal."""
        # Attempt path traversal
        dangerous = "../../../etc/passwd"
        safe = sanitize_filename(dangerous)
        
        # Should not contain path separators
        assert "/" not in safe
        assert "\\" not in safe
        assert ".." not in safe
    
    def test_ensure_directory_race_condition(self, tmp_path):
        """Test concurrent directory creation."""
        import threading
        import time
        
        new_dir = tmp_path / "concurrent_dir"
        errors = []
        
        def create_dir():
            try:
                ensure_directory(new_dir)
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads trying to create same directory
        threads = [threading.Thread(target=create_dir) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Should succeed without errors (or handle gracefully)
        # At least the directory should exist
        assert new_dir.exists()
        # Errors should be minimal or none
        assert len(errors) <= 1  # At most one race condition error
    
    def test_save_markdown_with_encoding(self, tmp_path):
        """Test saving markdown with special characters."""
        filepath = tmp_path / "unicode.md"
        content = "# Test\n\nSpecial: é ñ 中文 🧬"
        
        save_markdown(filepath, content)
        
        loaded = load_markdown(filepath)
        assert loaded == content
        assert "é" in loaded
        assert "🧬" in loaded
    
    def test_slugify_very_long_strings(self):
        """Test slugify handles very long strings."""
        long_text = "A" * 1000 + " Biology " + "B" * 1000
        result = slugify(long_text)
        
        # Should handle without crashing
        assert isinstance(result, str)
        assert "biology" in result.lower()
        # Should be reasonably long
        assert len(result) > 100

