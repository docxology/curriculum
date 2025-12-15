"""Tests for website scripts interaction behavior.

These tests verify that the JavaScript event handlers work correctly,
including content button clicks, module/session expansion, and event propagation.
"""

import json
import pytest

from src.website import scripts


class TestScriptsInteraction:
    """Test cases for JavaScript interaction behavior."""
    
    def test_content_button_handler_present(self):
        """Test that content button event handler is present in JavaScript."""
        modules_json = json.dumps([])
        js = scripts.get_javascript(modules_json)
        
        # Should use unified event delegation on sidebar
        assert "sidebar.addEventListener('click'" in js or 'sidebar.addEventListener("click"' in js
        assert ".content-button" in js
        assert "loadContent" in js
        assert "e.stopPropagation()" in js
        assert "e.preventDefault()" in js
    
    def test_module_button_handler_present(self):
        """Test that module button event handler is present."""
        modules_json = json.dumps([])
        js = scripts.get_javascript(modules_json)
        
        # Should use unified event delegation
        assert ".module-button" in js
        assert "session-list" in js or "sessionList" in js
    
    def test_session_button_handler_present(self):
        """Test that session button event handler is present."""
        modules_json = json.dumps([])
        js = scripts.get_javascript(modules_json)
        
        # Should use unified event delegation
        assert ".session-button" in js
        assert "content-list" in js or "contentList" in js
    
    def test_event_delegation_uses_sidebar(self):
        """Test that event delegation is attached to sidebar element."""
        modules_json = json.dumps([])
        js = scripts.get_javascript(modules_json)
        
        # Should check for sidebar before attaching (check for !sidebar and return)
        assert "if (!sidebar)" in js or 'if (!sidebar)' in js
        assert "sidebar.addEventListener" in js
    
    def test_content_button_handler_checks_first(self):
        """Test that content button handler is checked before module/session handlers."""
        modules_json = json.dumps([])
        js = scripts.get_javascript(modules_json)
        
        # Find the position of content button check vs session/module checks
        content_pos = js.find(".content-button")
        session_pos = js.find(".session-button")
        module_pos = js.find(".module-button")
        
        # Content button check should come first in the unified handler
        # (most specific handler should be checked first)
        assert content_pos < session_pos or content_pos < module_pos
    
    def test_event_propagation_stopped(self):
        """Test that event propagation is stopped for content buttons."""
        modules_json = json.dumps([])
        js = scripts.get_javascript(modules_json)
        
        # Should stop propagation to prevent parent handlers from interfering
        assert "e.stopPropagation()" in js
        assert "e.preventDefault()" in js
    
    def test_content_button_validation(self):
        """Test that content button handler validates data attributes."""
        modules_json = json.dumps([])
        js = scripts.get_javascript(modules_json)
        
        # Should validate moduleId, session, and contentType
        assert "moduleId" in js
        assert "session" in js
        assert "contentType" in js
        assert "console.warn" in js or "missing required data" in js.lower()
    
    def test_load_content_function_present(self):
        """Test that loadContent function is properly defined."""
        modules_json = json.dumps([])
        js = scripts.get_javascript(modules_json)
        
        # Should have loadContent function
        assert "function loadContent" in js or "loadContent = function" in js
        assert "welcomeScreen.style.display = 'none'" in js
        assert "contentView.style.display = 'block'" in js
    
    def test_unified_event_handler_structure(self):
        """Test that unified event handler has correct structure."""
        modules_json = json.dumps([])
        js = scripts.get_javascript(modules_json)
        
        # Should have event delegation on sidebar that routes clicks
        # Check for pattern: sidebar.addEventListener('click', (e) => { ... })
        sidebar_click_count = js.count("sidebar.addEventListener('click'") + js.count('sidebar.addEventListener("click"')
        assert sidebar_click_count >= 1  # At least one event handler on sidebar
    
    def test_button_target_checking(self):
        """Test that handlers check if click is on button itself or child."""
        modules_json = json.dumps([])
        js = scripts.get_javascript(modules_json)
        
        # Should check e.target to ensure clicks are on buttons, not nested elements
        assert "e.target" in js
        assert "closest" in js
    
    def test_content_button_active_class_management(self):
        """Test that active class is properly managed for content buttons."""
        modules_json = json.dumps([])
        js = scripts.get_javascript(modules_json)
        
        # Should remove active class from all buttons, then add to clicked one
        assert ".content-button" in js
        assert "classList.remove('active')" in js or "classList.remove(\"active\")" in js
        assert "classList.add('active')" in js or "classList.add(\"active\")" in js

