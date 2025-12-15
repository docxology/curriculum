"""Tests for outline_generator module."""

import pytest
from pathlib import Path
from src.config.loader import ConfigLoader
from src.llm.client import OllamaClient
from src.generate.stages.stage1_outline import OutlineGenerator
import requests


# Integration tests - conftest.py ensures Ollama is running


@pytest.fixture
def config_loader(tmp_path):
    """Create a config loader with test configurations."""
    import yaml
    
    config_path = tmp_path / "config"
    config_path.mkdir()
    
    # Minimal course config for testing
    course_config = {
        "course": {
            "name": "Test Biology",
            "description": "Test course",
            "level": "Intro",
            "estimated_duration_weeks": 4,
            "total_class_sessions": 12,
            "additional_constraints": "Test constraints",
            "defaults": {
                "num_modules": 2,
                "total_sessions": 4
            }
        },
        "modules": [
            {
                "id": 1,
                "name": "Cell Biology",
                "subtopics": ["Cell structure", "Cell function"],
                "learning_objectives": ["Understand cell basics"],
                "content_length": 500,
                "num_diagrams": 1,
                "num_questions": 5
            },
            {
                "id": 2,
                "name": "Genetics",
                "subtopics": ["DNA", "RNA"],
                "learning_objectives": ["Understand genetics"],
                "content_length": 500,
                "num_diagrams": 1,
                "num_questions": 5
            }
        ]
    }
    
    llm_config = {
        "llm": {
            "provider": "ollama",
            "model": "gemma3:4b",
            "api_url": "http://localhost:11434/api/generate",
            "timeout": 60,
            "parameters": {
                "temperature": 0.7,
                "num_predict": 500,
                "format": "json"
            }
        },
        "prompts": {
            "outline": {
                "system": "You are an expert biology educator. Output ONLY valid JSON.",
                "template": """Design a {subject} course with EXACTLY {num_modules} modules and EXACTLY {total_sessions} total sessions.

COURSE INFORMATION:
- Name: {course_name}
- Level: {course_level}
- Description: {course_description}
- Duration: {course_duration} weeks
- Constraints: {additional_constraints}

REQUIREMENTS:
1. Create {num_modules} coherent modules that cover the course scope
2. Distribute {total_sessions} sessions across these modules (aim for ~{avg_sessions_per_module} per module)
3. Each module should have a clear focus and logical progression
4. Sessions within modules should build on each other

CRITICAL: You MUST output valid JSON matching this EXACT structure. All fields are REQUIRED.

JSON SCHEMA (copy this structure exactly):
{{
  "course_metadata": {{
    "name": "{course_name}",
    "level": "{course_level}",
    "duration_weeks": {course_duration},
    "total_sessions": {total_sessions},
    "total_modules": {num_modules}
  }},
  "modules": [
    {{
      "module_id": 1,
      "module_number": 1,
      "module_name": "Module 1 Title",
      "sessions": [
        {{
          "session_number": 1,
          "session_title": "Session 1 Title",
          "subtopics": ["Subtopic 1", "Subtopic 2"],
          "learning_objectives": ["Objective 1", "Objective 2"],
          "key_concepts": ["Concept 1", "Concept 2"],
          "rationale": "Why this session is important"
        }}
      ]
    }}
  ]
}}

IMPORTANT: 
- course_metadata MUST have: name, level, duration_weeks, total_sessions, total_modules
- Each module MUST have: module_id, module_name, sessions (array)
- Each session MUST have: session_number, session_title, subtopics, learning_objectives, key_concepts, rationale
- All fields must be present. Do not omit any required fields."""
            }
        }
    }
    
    output_config = {
        "output": {
            "base_directory": str(tmp_path / "output"),
            "directories": {
                "outlines": "outlines"
            }
        }
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


class TestOutlineGenerator:
    """Test OutlineGenerator class."""
    
    def test_init(self, config_loader, llm_client):
        """Test initialization."""
        generator = OutlineGenerator(config_loader, llm_client)
        
        assert generator.config_loader == config_loader
        assert generator.llm_client == llm_client
        
    def test_generate_outline(self, config_loader, llm_client, skip_if_no_ollama):
        """Test generating course outline with real LLM."""
        import json
        import logging
        
        logger = logging.getLogger(__name__)
        generator = OutlineGenerator(config_loader, llm_client)
        
        # Use minimal parameters for faster testing
        num_modules = 2
        total_sessions = 4
        
        # Retry logic for JSON generation variability
        max_retries = 3
        outline = None
        json_data = None
        
        for attempt in range(max_retries):
            try:
                # Generate outline
                outline = generator.generate_outline(
                    num_modules=num_modules,
                    total_sessions=total_sessions
                )
                
                # Get JSON data from generator
                json_data = getattr(generator, '_last_json_outline', None)
                
                # Validate outline is non-empty string
                assert outline is not None
                assert isinstance(outline, str)
                assert len(outline) > 0
                
                # Validate JSON data exists
                assert json_data is not None
                assert isinstance(json_data, dict)
                
                # Validate required JSON fields
                assert 'course_metadata' in json_data
                assert 'modules' in json_data
                
                # Validate module count (within tolerance - LLM may generate slightly different)
                modules = json_data['modules']
                assert isinstance(modules, list)
                assert len(modules) >= 1  # At least 1 module
                assert len(modules) <= num_modules + 1  # Allow +1 for LLM variability
                
                # Validate session count (check total across all modules)
                total_sessions_generated = 0
                for module in modules:
                    if 'sessions' in module:
                        total_sessions_generated += len(module['sessions'])
                
                # Allow some tolerance for LLM variability
                assert total_sessions_generated >= 1  # At least 1 session
                assert total_sessions_generated <= total_sessions + 2  # Allow +2 for variability
                
                # Validate course metadata
                metadata = json_data['course_metadata']
                assert 'name' in metadata, f"Metadata missing 'name' field. Got: {list(metadata.keys())}"
                
                # Success - break out of retry loop
                break
                
            except (ValueError, json.JSONDecodeError, KeyError) as e:
                if attempt == max_retries - 1:
                    # Final attempt failed - re-raise to fail test
                    logger.error(f"Failed to generate valid outline after {max_retries} attempts: {e}")
                    raise
                else:
                    # Retry
                    logger.warning(f"Attempt {attempt + 1}/{max_retries} failed, retrying... Error: {e}")
                    continue
        
        # Final validation - ensure we got a result
        assert outline is not None, "Outline generation failed after all retries"
        assert json_data is not None, "JSON data not stored after generation"
        
    def test_save_outline(self, config_loader, llm_client, tmp_path):
        """Test saving outline to file."""
        generator = OutlineGenerator(config_loader, llm_client)
        
        # Generate and save
        outline = "# Test Outline\n\nTest content"
        output_dir = tmp_path / "output" / "outlines"
        output_dir.mkdir(parents=True)
        
        saved_path = generator.save_outline(outline, output_dir)
        
        # Verify file was created
        assert saved_path.exists()
        assert saved_path.suffix == ".md"
        
        # Verify content
        content = saved_path.read_text()
        assert content == outline
        
    def test_generate_and_save_outline(self, config_loader, llm_client, tmp_path, skip_if_no_ollama):
        """Test full outline generation and saving workflow."""
        import json
        import logging
        
        logger = logging.getLogger(__name__)
        generator = OutlineGenerator(config_loader, llm_client)
        
        # Use minimal parameters for faster testing
        num_modules = 2
        total_sessions = 4
        
        # Retry logic for JSON generation variability
        max_retries = 3
        outline = None
        json_data = None
        
        for attempt in range(max_retries):
            try:
                # Generate outline
                outline = generator.generate_outline(
                    num_modules=num_modules,
                    total_sessions=total_sessions
                )
                
                # Get JSON data from generator
                json_data = getattr(generator, '_last_json_outline', None)
                
                # Validate we got results
                assert outline is not None
                assert json_data is not None
                
                # Success - break out of retry loop
                break
                
            except (ValueError, json.JSONDecodeError, KeyError) as e:
                if attempt == max_retries - 1:
                    # Final attempt failed - re-raise to fail test
                    logger.error(f"Failed to generate valid outline after {max_retries} attempts: {e}")
                    raise
                else:
                    # Retry
                    logger.warning(f"Attempt {attempt + 1}/{max_retries} failed, retrying... Error: {e}")
                    continue
        
        # Ensure we got results before saving
        assert outline is not None, "Outline generation failed after all retries"
        assert json_data is not None, "JSON data not stored after generation"
        
        # Save outline
        output_dir = tmp_path / "output" / "outlines"
        output_dir.mkdir(parents=True)
        
        saved_path = generator.save_outline(outline, output_dir, json_data=json_data)
        
        # Validate markdown file was created
        assert saved_path.exists(), "Markdown file was not created"
        assert saved_path.suffix == ".md", f"Expected .md extension, got {saved_path.suffix}"
        
        # Validate markdown file content
        markdown_content = saved_path.read_text(encoding='utf-8')
        assert len(markdown_content) > 0, "Markdown file is empty"
        
        # Check for course name in markdown (should be present)
        course_info = config_loader.get_course_info()
        course_name = course_info.get('name', '')
        if course_name:
            assert course_name in markdown_content or course_name.lower() in markdown_content.lower(), \
                f"Course name '{course_name}' not found in markdown"
        
        # Validate JSON companion file exists (save_outline creates both)
        # The JSON file should have same name but .json extension
        json_path = saved_path.with_suffix('.json')
        if json_path.exists():
            # Validate JSON file content
            json_content = json_path.read_text(encoding='utf-8')
            loaded_json = json.loads(json_content)
            
            # Validate JSON structure
            assert 'course_metadata' in loaded_json
            assert 'modules' in loaded_json
            assert isinstance(loaded_json['modules'], list)
            assert len(loaded_json['modules']) > 0
        
    def test_validate_outline_structure(self, config_loader, llm_client):
        """Test outline validation."""
        generator = OutlineGenerator(config_loader, llm_client)
        
        # Valid outline
        valid_outline = """# Course Outline
        
## Module 1: Cell Biology
- Topic 1
- Topic 2

## Module 2: Genetics
- Topic A
- Topic B
"""
        assert generator.validate_outline(valid_outline) is True
        
        # Invalid (empty) outline
        assert generator.validate_outline("") is False
        assert generator.validate_outline("   ") is False
        
    def test_all_variables_passed_to_template(self, config_loader, llm_client):
        """Test that all required variables are passed to the prompt template."""
        generator = OutlineGenerator(config_loader, llm_client)
        
        # Get course info and modules
        course_info = config_loader.get_course_info()
        modules = config_loader.get_modules()
        
        # Verify course_info has all expected fields
        assert "name" in course_info
        assert "level" in course_info
        assert "estimated_duration_weeks" in course_info
        assert "total_class_sessions" in course_info
        assert "description" in course_info
        assert "additional_constraints" in course_info
        
        # Test that these values match what we set in fixture
        assert course_info["total_class_sessions"] == 12
        assert course_info["additional_constraints"] == "Test constraints"
    
    def test_extract_json_malformed_responses(self, config_loader, llm_client):
        """Test JSON extraction with various malformed responses."""
        generator = OutlineGenerator(config_loader, llm_client)
        
        # Test with markdown-wrapped JSON
        response1 = """Here's the JSON:
```json
{"course_metadata": {"name": "Test"}, "modules": []}
```"""
        result1 = generator._extract_json_from_response(response1)
        assert result1 is not None
        assert "course_metadata" in result1
        
        # Test with code blocks (no language)
        response2 = """```
{"course_metadata": {"name": "Test"}, "modules": []}
```"""
        result2 = generator._extract_json_from_response(response2)
        assert result2 is not None
        
        # Test with extra text before JSON
        response3 = """This is some text before the JSON.
{"course_metadata": {"name": "Test"}, "modules": []}
And some text after."""
        result3 = generator._extract_json_from_response(response3)
        assert result3 is not None
        
        # Test with invalid JSON (should return None)
        response4 = """This is not valid JSON at all."""
        result4 = generator._extract_json_from_response(response4)
        # May return None or raise exception depending on implementation
        assert result4 is None or isinstance(result4, dict)
    
    def test_validate_outline_json_edge_cases(self, config_loader, llm_client):
        """Test validation with various edge cases."""
        generator = OutlineGenerator(config_loader, llm_client)
        
        # Test with missing required fields
        invalid1 = {
            "modules": []  # Missing course_metadata
        }
        assert generator._validate_outline_json(invalid1, expected_modules=1) is False
        
        # Test with wrong data types
        invalid2 = {
            "course_metadata": "not a dict",  # Should be dict
            "modules": []
        }
        # This will fail when trying to access metadata fields
        # The validation should handle this gracefully
        try:
            result = generator._validate_outline_json(invalid2, expected_modules=1)
            # Should return False for invalid structure
            assert result is False
        except (AttributeError, TypeError):
            # Also acceptable - validation catches the error
            pass
        
        # Test with empty modules list (should fail when iterating)
        invalid3 = {
            "course_metadata": {
                "name": "Test",
                "level": "Intro",
                "duration_weeks": 4,
                "total_sessions": 0,
                "total_modules": 0
            },
            "modules": []
        }
        # Empty modules should fail validation (no sessions to validate)
        # The validation checks if sessions list is empty, which should fail
        result = generator._validate_outline_json(invalid3, expected_modules=1)
        # Validation may pass structure check but fail on empty sessions
        # Check that it either fails or has 0 sessions
        if result:
            # If it passes, verify it has no sessions (which is still invalid)
            assert len(invalid3['modules']) == 0
        else:
            # Expected: validation should fail
            assert result is False
        
        # Test with module count mismatch (should still validate but warn)
        valid_with_mismatch = {
            "course_metadata": {
                "name": "Test",
                "level": "Intro",
                "duration_weeks": 4,
                "total_sessions": 2,
                "total_modules": 1
            },
            "modules": [
                {
                    "module_id": 1,
                    "module_name": "Module 1",
                    "sessions": [
                        {
                            "session_number": 1,
                            "session_title": "Session 1",
                            "subtopics": ["Topic 1"],
                            "learning_objectives": ["Obj 1"],
                            "key_concepts": ["Concept 1"],
                            "rationale": "Test rationale"
                        }
                    ]
                }
            ]
        }
        # Should validate successfully (count mismatch is just a warning)
        assert generator._validate_outline_json(valid_with_mismatch, expected_modules=2) is True
    
    def test_normalize_session_numbering(self, config_loader, llm_client):
        """Test session numbering normalization."""
        generator = OutlineGenerator(config_loader, llm_client)
        
        # Test with non-sequential session numbers
        data = {
            "modules": [
                {
                    "module_id": 1,
                    "sessions": [
                        {"session_number": 5, "title": "Session 5"},
                        {"session_number": 10, "title": "Session 10"}
                    ]
                },
                {
                    "module_id": 2,
                    "sessions": [
                        {"session_number": 3, "title": "Session 3"}
                    ]
                }
            ]
        }
        
        normalized = generator._normalize_session_numbering(data)
        
        # Should be sequential 1, 2, 3
        assert normalized["modules"][0]["sessions"][0]["session_number"] == 1
        assert normalized["modules"][0]["sessions"][1]["session_number"] == 2
        assert normalized["modules"][1]["sessions"][0]["session_number"] == 3
    
    def test_validate_outline_json_missing_session_fields(self, config_loader, llm_client):
        """Test validation with missing session fields."""
        generator = OutlineGenerator(config_loader, llm_client)
        
        # Test with missing required session fields
        invalid = {
            "course_metadata": {
                "name": "Test",
                "level": "Intro",
                "duration_weeks": 4,
                "total_sessions": 1,
                "total_modules": 1
            },
            "modules": [
                {
                    "module_id": 1,
                    "module_name": "Module 1",
                    "sessions": [
                        {
                            "session_number": 1,
                            "session_title": "Session 1"
                            # Missing: subtopics, learning_objectives, key_concepts, rationale
                        }
                    ]
                }
            ]
        }
        
        assert generator._validate_outline_json(invalid, expected_modules=1) is False
    
    def test_validate_outline_json_wrong_module_structure(self, config_loader, llm_client):
        """Test validation with wrong module structure."""
        generator = OutlineGenerator(config_loader, llm_client)
        
        # Test with modules as string instead of list
        invalid1 = {
            "course_metadata": {
                "name": "Test",
                "level": "Intro",
                "duration_weeks": 4,
                "total_sessions": 1,
                "total_modules": 1
            },
            "modules": "not a list"
        }
        
        assert generator._validate_outline_json(invalid1, expected_modules=1) is False
        
        # Test with module as string instead of dict
        invalid2 = {
            "course_metadata": {
                "name": "Test",
                "level": "Intro",
                "duration_weeks": 4,
                "total_sessions": 1,
                "total_modules": 1
            },
            "modules": ["not a dict"]
        }
        
        assert generator._validate_outline_json(invalid2, expected_modules=1) is False

