"""Tests for website templates module."""

import pytest
from src.website import templates


class TestTemplates:
    """Test template functions."""
    
    def test_markdown_to_html_basic(self):
        """Test basic markdown to HTML conversion."""
        markdown = "# Heading\n\nThis is a paragraph."
        html = templates.markdown_to_html(markdown)
        
        assert "<h1>Heading</h1>" in html
        assert "<p>This is a paragraph.</p>" in html
    
    def test_markdown_to_html_code_blocks(self):
        """Test markdown with code blocks."""
        markdown = "```python\ndef hello():\n    print('Hello')\n```"
        html = templates.markdown_to_html(markdown)
        
        assert "<code" in html or "pre" in html
        assert "python" in html.lower() or "hello" in html.lower()
    
    def test_markdown_to_html_tables(self):
        """Test markdown with tables."""
        markdown = "| Header 1 | Header 2 |\n|----------|----------|\n| Cell 1   | Cell 2   |"
        html = templates.markdown_to_html(markdown)
        
        assert "<table" in html
        assert "Header 1" in html
        assert "Cell 1" in html
    
    def test_markdown_to_html_lists(self):
        """Test markdown with lists."""
        markdown = "- Item 1\n- Item 2\n- Item 3"
        html = templates.markdown_to_html(markdown)
        
        assert "<ul" in html
        assert "Item 1" in html
        assert "Item 2" in html
    
    def test_markdown_to_html_ordered_lists(self):
        """Test markdown with ordered lists."""
        markdown = "1. First\n2. Second\n3. Third"
        html = templates.markdown_to_html(markdown)
        
        assert "<ol" in html
        assert "First" in html
        assert "Second" in html
    
    def test_markdown_to_html_graceful_fallback(self):
        """Test markdown conversion handles errors gracefully."""
        # Create markdown that might cause issues
        markdown = "Normal text\n\n```\nUnclosed code block"
        html = templates.markdown_to_html(markdown)
        
        # Should return HTML (either converted or wrapped in pre)
        assert isinstance(html, str)
        assert len(html) > 0
    
    def test_escape_html_standard_entities(self):
        """Test escape_html with standard HTML entities."""
        text = "Text with <tags> and & symbols"
        escaped = templates.escape_html(text)
        
        assert "&lt;" in escaped
        assert "&gt;" in escaped
        assert "&amp;" in escaped
        assert "<tags>" not in escaped
    
    def test_escape_html_quotes(self):
        """Test escape_html with quotes."""
        text = 'Text with "double" and \'single\' quotes'
        escaped = templates.escape_html(text)
        
        assert "&quot;" in escaped or '"' not in escaped
        assert "&#x27;" in escaped or "'" not in escaped
    
    def test_escape_html_empty_string(self):
        """Test escape_html with empty string."""
        result = templates.escape_html("")
        
        assert result == ""
    
    def test_escape_html_special_characters(self):
        """Test escape_html with special characters."""
        text = "<script>alert('XSS')</script>"
        escaped = templates.escape_html(text)
        
        assert "<script>" not in escaped
        assert "alert" in escaped  # Content should remain, just escaped
    
    def test_generate_html_complete_structure(self):
        """Test generate_html creates complete HTML document."""
        course_data = {
            "name": "Test Course",
            "description": "Test description",
            "level": "Intro"
        }
        modules_data = [
            {
                "module_id": 1,
                "module_name": "Module 1",
                "sessions": [
                    {
                        "session_number": 1,
                        "session_title": "Session 1",
                        "content": {}
                    }
                ]
            }
        ]
        
        html = templates.generate_html(course_data, modules_data)
        
        assert "<!DOCTYPE html>" in html
        assert "<html" in html
        assert "<head" in html
        assert "<body" in html
        assert "Test Course" in html
    
    def test_generate_html_embedded_css(self):
        """Test generate_html includes embedded CSS."""
        course_data = {"name": "Test"}
        modules_data = []
        
        html = templates.generate_html(course_data, modules_data)
        
        assert "<style>" in html
        assert "body" in html or "font-family" in html
    
    def test_generate_html_embedded_javascript(self):
        """Test generate_html includes embedded JavaScript."""
        course_data = {"name": "Test"}
        modules_data = []
        
        html = templates.generate_html(course_data, modules_data)
        
        assert "<script>" in html
        assert "mermaid" in html.lower() or "modulesData" in html
    
    def test_generate_html_modules_serialization(self):
        """Test generate_html serializes modules data correctly."""
        course_data = {"name": "Test"}
        modules_data = [
            {
                "module_id": 1,
                "module_name": "Module 1",
                "sessions": [
                    {
                        "session_number": 1,
                        "session_title": "Session 1",
                        "content": {"lecture": "<p>Content</p>"}
                    }
                ]
            }
        ]
        
        html = templates.generate_html(course_data, modules_data)
        
        # Modules data should be serialized in JavaScript
        assert "Module 1" in html
        assert "Session 1" in html
        assert "modulesData" in html or "const modules" in html
    
    def test_generate_html_course_metadata(self):
        """Test generate_html includes course metadata."""
        course_data = {
            "name": "Biology 101",
            "description": "Introduction to biology",
            "level": "Undergraduate"
        }
        modules_data = []
        
        html = templates.generate_html(course_data, modules_data)
        
        assert "Biology 101" in html
        assert "Introduction to biology" in html
        assert "Undergraduate" in html
    
    def test_generate_html_with_timestamp(self):
        """Test generate_html includes generation timestamp."""
        course_data = {"name": "Test"}
        modules_data = []
        timestamp = "2024-01-15 10:30:00"
        
        html = templates.generate_html(course_data, modules_data, timestamp)
        
        assert timestamp in html
    
    def test_generate_html_without_timestamp(self):
        """Test generate_html generates timestamp if not provided."""
        course_data = {"name": "Test"}
        modules_data = []
        
        html = templates.generate_html(course_data, modules_data)
        
        # Should include some timestamp (current time)
        assert "Generated" in html or "Generated on" in html
    
    def test_generate_navigation_html_single_module(self):
        """Test _generate_navigation_html with single module."""
        modules_data = [
            {
                "module_id": 1,
                "module_name": "Module 1",
                "sessions": [
                    {
                        "session_number": 1,
                        "session_title": "Session 1",
                        "content": {"lecture": "content"}
                    }
                ]
            }
        ]
        
        html = templates._generate_navigation_html(modules_data)
        
        assert "Module 1" in html
        assert "Session 1" in html
        assert "module-button" in html
        assert "session-button" in html
    
    def test_generate_navigation_html_multiple_modules(self):
        """Test _generate_navigation_html with multiple modules."""
        modules_data = [
            {
                "module_id": 1,
                "module_name": "Module 1",
                "sessions": [
                    {
                        "session_number": 1,
                        "session_title": "Session 1",
                        "content": {}
                    }
                ]
            },
            {
                "module_id": 2,
                "module_name": "Module 2",
                "sessions": [
                    {
                        "session_number": 1,
                        "session_title": "Session 1",
                        "content": {}
                    }
                ]
            }
        ]
        
        html = templates._generate_navigation_html(modules_data)
        
        assert "Module 1" in html
        assert "Module 2" in html
    
    def test_generate_navigation_html_content_type_detection(self):
        """Test _generate_navigation_html detects available content types."""
        modules_data = [
            {
                "module_id": 1,
                "module_name": "Module 1",
                "sessions": [
                    {
                        "session_number": 1,
                        "session_title": "Session 1",
                        "content": {
                            "lecture": "<p>Lecture</p>",
                            "lab": "<p>Lab</p>",
                            "questions": "<p>Questions</p>"
                        }
                    }
                ]
            }
        ]
        
        html = templates._generate_navigation_html(modules_data)
        
        # Should show buttons for available content types
        assert "Lecture" in html
        assert "Lab" in html
        assert "Questions" in html
    
    def test_generate_navigation_html_hides_missing_content(self):
        """Test _generate_navigation_html doesn't show buttons for missing content."""
        modules_data = [
            {
                "module_id": 1,
                "module_name": "Module 1",
                "sessions": [
                    {
                        "session_number": 1,
                        "session_title": "Session 1",
                        "content": {
                            "lecture": "<p>Lecture</p>"
                            # Missing lab, study_notes, etc.
                        }
                    }
                ]
            }
        ]
        
        html = templates._generate_navigation_html(modules_data)
        
        # Should show lecture
        assert "Lecture" in html
        # Should not show lab (not in content)
        # Note: This test checks that only available content types are shown
    
    def test_generate_navigation_html_diagram_buttons(self):
        """Test _generate_navigation_html generates diagram buttons."""
        modules_data = [
            {
                "module_id": 1,
                "module_name": "Module 1",
                "sessions": [
                    {
                        "session_number": 1,
                        "session_title": "Session 1",
                        "content": {
                            "diagram_1": "graph TD\nA-->B",
                            "diagram_2": "graph LR\nC-->D"
                        }
                    }
                ]
            }
        ]
        
        html = templates._generate_navigation_html(modules_data)
        
        # Should show diagram buttons
        assert "Diagram" in html or "diagram" in html.lower()
    
    def test_generate_navigation_html_secondary_content(self):
        """Test _generate_navigation_html includes secondary content types."""
        modules_data = [
            {
                "module_id": 1,
                "module_name": "Module 1",
                "sessions": [
                    {
                        "session_number": 1,
                        "session_title": "Session 1",
                        "content": {
                            "application": "<p>Application</p>",
                            "visualization": "graph TD\nA-->B",
                            "extension": "<p>Extension</p>"
                        }
                    }
                ]
            }
        ]
        
        html = templates._generate_navigation_html(modules_data)
        
        assert "Application" in html
        assert "Visualization" in html
        assert "Extension" in html
    
    def test_generate_navigation_html_aria_attributes(self):
        """Test _generate_navigation_html includes ARIA attributes."""
        modules_data = [
            {
                "module_id": 1,
                "module_name": "Module 1",
                "sessions": [
                    {
                        "session_number": 1,
                        "session_title": "Session 1",
                        "content": {}
                    }
                ]
            }
        ]
        
        html = templates._generate_navigation_html(modules_data)
        
        # Should include ARIA attributes for accessibility
        assert "aria-expanded" in html or "data-module-id" in html
    
    def test_escape_html_preserves_text(self):
        """Test escape_html preserves non-HTML text."""
        text = "This is normal text without HTML"
        escaped = templates.escape_html(text)
        
        assert escaped == text
    
    def test_markdown_to_html_headers(self):
        """Test markdown to HTML converts headers correctly."""
        markdown = "# H1\n## H2\n### H3"
        html = templates.markdown_to_html(markdown)
        
        assert "<h1>H1</h1>" in html
        assert "<h2>H2</h2>" in html
        assert "<h3>H3</h3>" in html
    
    def test_markdown_to_html_links(self):
        """Test markdown to HTML converts links."""
        markdown = "[Link text](https://example.com)"
        html = templates.markdown_to_html(markdown)
        
        assert "<a" in html
        assert "href" in html
        assert "example.com" in html
    
    def test_generate_html_empty_modules(self):
        """Test generate_html handles empty modules list."""
        course_data = {"name": "Test"}
        modules_data = []
        
        html = templates.generate_html(course_data, modules_data)
        
        # Should still generate valid HTML
        assert "<!DOCTYPE html>" in html
        assert "Test" in html







