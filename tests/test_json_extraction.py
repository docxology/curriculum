"""Tests for JSON extraction from LLM responses.

Tests the _extract_json_from_response method with various response formats
that the LLM might return, including edge cases.
"""

import pytest
import yaml
from pathlib import Path
from src.generate.stages.stage1_outline import OutlineGenerator
from src.config.loader import ConfigLoader
from src.llm.client import OllamaClient


@pytest.fixture
def config_loader(tmp_path):
    """Create a config loader with test configurations."""
    config_path = tmp_path / "config"
    config_path.mkdir()
    
    # Minimal course config for testing
    course_config = {
        "course": {
            "name": "Test Course",
            "level": "Introductory",
            "duration_weeks": 4,
            "description": "Test course for JSON extraction testing"
        },
        "structure": {
            "num_modules": 2,
            "total_sessions": 4
        },
        "content_bounds": {
            "subtopics_per_session": {"min": 3, "max": 5},
            "learning_objectives_per_session": {"min": 3, "max": 5},
            "key_concepts_per_session": {"min": 5, "max": 8}
        }
    }
    
    # Minimal LLM config for testing
    llm_config = {
        "llm": {
            "provider": "ollama",
            "model": "gemma3:4b",
            "api_url": "http://localhost:11434/api/generate",
            "timeout": 60,
            "parameters": {
                "temperature": 0.7,
                "top_p": 0.9,
                "num_predict": 100
            }
        }
    }
    
    # Minimal output config
    output_config = {
        "base_directory": str(tmp_path / "output")
    }
    
    # Write configs
    with open(config_path / "course_config.yaml", "w") as f:
        yaml.dump(course_config, f)
    with open(config_path / "llm_config.yaml", "w") as f:
        yaml.dump(llm_config, f)
    with open(config_path / "output_config.yaml", "w") as f:
        yaml.dump(output_config, f)
    
    return ConfigLoader(config_path)


@pytest.fixture
def llm_client(config_loader):
    """Create an LLM client for testing."""
    llm_config = config_loader.get_llm_parameters()
    return OllamaClient(llm_config)


@pytest.fixture
def outline_generator(config_loader, llm_client):
    """Create OutlineGenerator instance for testing."""
    return OutlineGenerator(config_loader, llm_client)


class TestJSONExtraction:
    """Test JSON extraction from various response formats."""
    
    def test_extract_json_from_markdown_code_block(self, outline_generator):
        """Test extraction from markdown code block with json tag."""
        response = """
        Here's the outline:
        ```json
        {"course_metadata": {"name": "Test"}, "modules": []}
        ```
        That's the complete outline.
        """
        result = outline_generator._extract_json_from_response(response)
        assert result is not None
        assert "course_metadata" in result
        assert result["course_metadata"]["name"] == "Test"
    
    def test_extract_json_from_plain_code_block(self, outline_generator):
        """Test extraction from plain markdown code block."""
        response = """
        ``` 
        {"course_metadata": {"name": "Test"}, "modules": []}
        ```
        """
        result = outline_generator._extract_json_from_response(response)
        assert result is not None
        assert "course_metadata" in result
    
    def test_extract_json_from_raw_response(self, outline_generator):
        """Test extraction from raw JSON response."""
        response = '{"course_metadata": {"name": "Test"}, "modules": []}'
        result = outline_generator._extract_json_from_response(response)
        assert result is not None
        assert "course_metadata" in result
    
    def test_extract_json_embedded_in_text(self, outline_generator):
        """Test extraction when JSON is embedded in explanatory text."""
        response = """
        Okay, here's the outline for the course.
        {"course_metadata": {"name": "Test"}, "modules": []}
        This should work for your needs.
        """
        result = outline_generator._extract_json_from_response(response)
        assert result is not None
        assert "course_metadata" in result
    
    def test_extract_json_with_nested_structure(self, outline_generator):
        """Test extraction with deeply nested JSON structure."""
        response = """
        {
            "course_metadata": {
                "name": "Test",
                "level": "Intro",
                "duration_weeks": 4
            },
            "modules": [
                {
                    "module_id": 1,
                    "module_name": "Module 1",
                    "sessions": [
                        {
                            "session_number": 1,
                            "session_title": "Session 1",
                            "subtopics": ["topic1", "topic2"]
                        }
                    ]
                }
            ]
        }
        """
        result = outline_generator._extract_json_from_response(response)
        assert result is not None
        assert "modules" in result
        assert len(result["modules"]) == 1
        assert len(result["modules"][0]["sessions"]) == 1
    
    def test_extract_json_finds_largest_object(self, outline_generator):
        """Test that extraction finds the largest valid JSON object."""
        response = """
        Some text with {invalid json}
        {"course_metadata": {"name": "Test"}, "modules": []}
        More text with {another invalid}
        """
        result = outline_generator._extract_json_from_response(response)
        assert result is not None
        assert "course_metadata" in result
    
    def test_extract_json_from_response_with_course_metadata_keyword(self, outline_generator):
        """Test extraction using course_metadata keyword search."""
        response = """
        Here's the response:
        {
            "course_metadata": {"name": "Test"},
            "modules": []
        }
        """
        result = outline_generator._extract_json_from_response(response)
        assert result is not None
        assert "course_metadata" in result
    
    def test_extract_json_from_response_with_modules_keyword(self, outline_generator):
        """Test extraction using modules keyword search."""
        response = """
        Response:
        {
            "modules": [{"module_id": 1}],
            "course_metadata": {"name": "Test"}
        }
        """
        result = outline_generator._extract_json_from_response(response)
        assert result is not None
        assert "modules" in result
    
    def test_extract_json_handles_multiple_objects(self, outline_generator):
        """Test that extraction handles multiple JSON objects correctly."""
        response = """
        {"invalid": "object"}
        {"course_metadata": {"name": "Test"}, "modules": []}
        {"another": "object"}
        """
        result = outline_generator._extract_json_from_response(response)
        assert result is not None
        # Should extract the valid course outline, not the invalid objects
        assert "course_metadata" in result
    
    def test_extract_json_returns_none_for_invalid_json(self, outline_generator):
        """Test that extraction returns None for completely invalid responses."""
        response = "This is just plain text with no JSON at all."
        result = outline_generator._extract_json_from_response(response)
        assert result is None
    
    def test_extract_json_returns_none_for_malformed_json(self, outline_generator):
        """Test that extraction returns None for malformed JSON."""
        response = '{"course_metadata": {"name": "Test", "modules": []}'  # Missing closing brace
        result = outline_generator._extract_json_from_response(response)
        assert result is None
    
    def test_extract_json_handles_whitespace(self, outline_generator):
        """Test that extraction handles various whitespace patterns."""
        response = """
        
        
        {
            "course_metadata": {"name": "Test"},
            "modules": []
        }
        
        
        """
        result = outline_generator._extract_json_from_response(response)
        assert result is not None
        assert "course_metadata" in result
    
    def test_extract_json_handles_newlines_in_strings(self, outline_generator):
        """Test that extraction handles JSON with newlines in string values."""
        response = """
        {
            "course_metadata": {
                "name": "Test Course",
                "description": "A course\\nwith newlines"
            },
            "modules": []
        }
        """
        result = outline_generator._extract_json_from_response(response)
        assert result is not None
        assert "course_metadata" in result

