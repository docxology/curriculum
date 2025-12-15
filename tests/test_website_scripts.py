"""Tests for website scripts module."""

import json
import pytest

from src.website import scripts


class TestScripts:
    """Test cases for scripts module."""
    
    def test_get_javascript_returns_string(self):
        """Test that get_javascript returns a string."""
        modules_json = json.dumps([{"module_id": 1, "module_name": "Test"}])
        js = scripts.get_javascript(modules_json)
        assert isinstance(js, str)
        assert len(js) > 0
    
    def test_get_javascript_includes_modules_data(self):
        """Test that JavaScript includes modules data."""
        modules_data = [{"module_id": 1, "module_name": "Test Module"}]
        modules_json = json.dumps(modules_data)
        js = scripts.get_javascript(modules_json)
        assert "modulesData" in js
        assert "Test Module" in js
    
    def test_get_javascript_includes_mermaid_init(self):
        """Test that JavaScript includes Mermaid initialization."""
        modules_json = json.dumps([])
        js = scripts.get_javascript(modules_json)
        assert "mermaid.initialize" in js
    
    def test_get_javascript_includes_highlight_init(self):
        """Test that JavaScript includes Highlight.js initialization."""
        modules_json = json.dumps([])
        js = scripts.get_javascript(modules_json)
        assert "hljs" in js
    
    def test_get_javascript_includes_search_functionality(self):
        """Test that JavaScript includes search functionality."""
        modules_json = json.dumps([])
        js = scripts.get_javascript(modules_json)
        assert "performSearch" in js
        assert "searchInput" in js
    
    def test_get_javascript_includes_dark_mode(self):
        """Test that JavaScript includes dark mode functionality."""
        modules_json = json.dumps([])
        js = scripts.get_javascript(modules_json)
        assert "toggleDarkMode" in js
        assert "initDarkMode" in js
        assert "darkMode" in js
    
    def test_get_javascript_includes_progress_tracking(self):
        """Test that JavaScript includes progress tracking."""
        modules_json = json.dumps([])
        js = scripts.get_javascript(modules_json)
        assert "updateProgress" in js
        assert "markSessionViewed" in js
        assert "localStorage" in js
    
    def test_get_javascript_includes_content_loading(self):
        """Test that JavaScript includes content loading functionality."""
        modules_json = json.dumps([])
        js = scripts.get_javascript(modules_json)
        assert "loadContent" in js
        assert "showWelcome" in js
    
    def test_get_javascript_includes_toc_generation(self):
        """Test that JavaScript includes table of contents generation."""
        modules_json = json.dumps([])
        js = scripts.get_javascript(modules_json)
        assert "generateTOC" in js
    
    def test_get_javascript_includes_breadcrumbs(self):
        """Test that JavaScript includes breadcrumb functionality."""
        modules_json = json.dumps([])
        js = scripts.get_javascript(modules_json)
        assert "updateBreadcrumbs" in js
    
    def test_get_javascript_includes_keyboard_navigation(self):
        """Test that JavaScript includes keyboard navigation."""
        modules_json = json.dumps([])
        js = scripts.get_javascript(modules_json)
        assert "keydown" in js
        assert "Escape" in js
    
    def test_get_javascript_handles_empty_modules(self):
        """Test that JavaScript handles empty modules list."""
        modules_json = json.dumps([])
        js = scripts.get_javascript(modules_json)
        assert "modulesData" in js
        assert isinstance(js, str)
    
    def test_get_javascript_handles_complex_modules(self):
        """Test that JavaScript handles complex module structures."""
        modules_data = [
            {
                "module_id": 1,
                "module_name": "Module 1",
                "sessions": [
                    {
                        "session_number": 1,
                        "session_title": "Session 1",
                        "content": {
                            "lecture": "<p>Content</p>",
                            "lab": "<p>Lab content</p>"
                        }
                    }
                ]
            }
        ]
        modules_json = json.dumps(modules_data)
        js = scripts.get_javascript(modules_json)
        assert "Module 1" in js
        assert "Session 1" in js







