"""Tests for website styles module."""

import pytest

from src.website import styles


class TestStyles:
    """Test cases for styles module."""
    
    def test_get_css_returns_string(self):
        """Test that get_css returns a string."""
        css = styles.get_css()
        assert isinstance(css, str)
        assert len(css) > 0
    
    def test_get_css_contains_css_variables(self):
        """Test that CSS contains CSS variables."""
        css = styles.get_css()
        assert ":root" in css
        assert "--primary-color" in css
        assert "--text-color" in css
        assert "--bg-color" in css
    
    def test_get_css_contains_dark_mode(self):
        """Test that CSS contains dark mode styles."""
        css = styles.get_css()
        assert '[data-theme="dark"]' in css
    
    def test_get_css_contains_responsive_design(self):
        """Test that CSS contains responsive design media queries."""
        css = styles.get_css()
        assert "@media" in css
        assert "max-width" in css
    
    def test_get_css_contains_print_styles(self):
        """Test that CSS contains print styles."""
        css = styles.get_css()
        assert "@media print" in css
    
    def test_get_css_contains_key_classes(self):
        """Test that CSS contains key class definitions."""
        css = styles.get_css()
        assert ".sidebar" in css
        assert ".content-body" in css
        assert ".search-input" in css
        assert ".table-of-contents" in css
        assert ".progress-indicator" in css







