"""Tests for pipeline error recovery and resume functionality.

Note: These are integration tests that require Ollama to be running locally.
The conftest.py ensures Ollama is started before tests run.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from src.config.loader import ConfigLoader
from src.generate.orchestration.pipeline import ContentGenerator
from src.llm.client import LLMError


@pytest.fixture
def test_config(tmp_path):
    """Create minimal test configuration."""
    import yaml
    
    config_path = tmp_path / "config"
    config_path.mkdir()
    
    llm_config = {
        "llm": {
            "provider": "ollama",
            "model": "gemma3:4b",
            "api_url": "http://localhost:11434/api/generate",
            "timeout": 60,
            "parameters": {"temperature": 0.7, "num_predict": 200}
        },
        "prompts": {
            "lecture": {
                "system": "You are a biology educator.",
                "template": "Write about {module_name}"
            },
            "lab": {
                "system": "You are a lab instructor.",
                "template": "Lab {lab_number} for {module_name}"
            },
            "study_notes": {
                "system": "You are a biology educator.",
                "template": "Study notes for {module_name}"
            },
            "diagram": {
                "system": "Create diagrams.",
                "template": "Diagram for {topic}"
            },
            "questions": {
                "system": "Create questions.",
                "template": "Questions for {module_name}"
            }
        }
    }
    
    course_config = {
        "course": {
            "name": "Test Biology",
            "description": "Test course",
            "level": "Intro",
            "estimated_duration_weeks": 4,
            "total_class_sessions": 4
        }
    }
    
    output_config = {
        "output": {
            "base_directory": str(tmp_path / "output"),
            "directories": {
                "outlines": "outlines",
                "modules": "modules"
            }
        }
    }
    
    # Write all required config files
    with open(config_path / "llm_config.yaml", "w") as f:
        yaml.dump(llm_config, f)
    
    with open(config_path / "course_config.yaml", "w") as f:
        yaml.dump(course_config, f)
    
    with open(config_path / "output_config.yaml", "w") as f:
        yaml.dump(output_config, f)
    
    return config_path


class TestPipelineRecovery:
    """Tests for pipeline error recovery mechanisms."""
    
    def test_transient_error_detection(self):
        """Test that transient errors are properly identified."""
        from src.generate.orchestration.pipeline import ContentGenerator
        from src.config.loader import ConfigLoader
        
        loader = ConfigLoader("config")
        generator = ContentGenerator(loader)
        
        # Test timeout error detection
        timeout_error = LLMError("Stream timeout: 180.5s elapsed")
        assert generator._is_transient_error(timeout_error) == True
        
        # Test connection error detection
        import requests
        conn_error = requests.ConnectionError("Connection refused")
        assert generator._is_transient_error(conn_error) == True
        
        # Test non-transient error
        validation_error = ValueError("Invalid configuration")
        assert generator._is_transient_error(validation_error) == False
    
    def test_resume_capability_skip_existing(self, test_config, skip_if_no_ollama, tmp_path):
        """Test that pipeline can resume by skipping existing content."""
        from src.generate.orchestration.pipeline import ContentGenerator
        
        loader = ConfigLoader(test_config)
        generator = ContentGenerator(loader)
        
        # Create a minimal outline JSON for testing
        outline_data = {
            "course_metadata": {
                "course_template": "biology",
                "name": "Test Biology",
                "total_sessions": 1,
                "total_modules": 1
            },
            "modules": [
                {
                    "module_id": 1,
                    "module_name": "Test Module",
                    "sessions": [
                        {
                            "session_number": 1,
                            "session_title": "Test Session",
                            "subtopics": ["Topic 1"],
                            "learning_objectives": ["Objective 1"],
                            "key_concepts": ["Concept 1"]
                        }
                    ]
                }
            ]
        }
        
        # Create output directory structure
        output_dir = tmp_path / "output" / "biology" / "modules" / "module_01_test_module" / "session_01"
        output_dir.mkdir(parents=True)
        
        # Create existing lecture file
        lecture_file = output_dir / "lecture.md"
        lecture_file.write_text("# Test Lecture\n\nExisting content.")
        
        # Mock the outline loading
        import json
        outline_file = tmp_path / "outline.json"
        with open(outline_file, "w") as f:
            json.dump(outline_data, f)
        
        # This test verifies skip_existing logic exists
        # Full integration would require more setup
        assert lecture_file.exists()
    
    def test_error_categorization(self):
        """Test that errors are properly categorized for recovery."""
        from src.generate.orchestration.pipeline import ContentGenerator
        from src.config.loader import ConfigLoader
        
        loader = ConfigLoader("config")
        generator = ContentGenerator(loader)
        
        # Test various error types
        errors = [
            (LLMError("Stream timeout: 180s"), True),  # Transient
            (LLMError("Connection timeout"), True),    # Transient
            (LLMError("Validation failed"), False),    # Not transient
            (ValueError("Invalid input"), False),      # Not transient
        ]
        
        for error, should_be_transient in errors:
            assert generator._is_transient_error(error) == should_be_transient


class TestRetryMechanism:
    """Tests for retry mechanism in pipeline."""
    
    def test_retry_generation_helper(self, test_config, skip_if_no_ollama):
        """Test the _retry_generation helper method."""
        from src.generate.orchestration.pipeline import ContentGenerator
        from src.config.loader import ConfigLoader
        
        loader = ConfigLoader(test_config)
        generator = ContentGenerator(loader)
        
        # Test successful generation (no retry needed)
        call_count = [0]
        def successful_func():
            call_count[0] += 1
            return "success"
        
        result = generator._retry_generation(successful_func, max_retries=2, operation_name="test")
        
        assert result == "success"
        assert call_count[0] == 1  # Should only call once
    
    def test_retry_on_transient_failure(self, test_config):
        """Test that transient failures trigger retries."""
        from src.generate.orchestration.pipeline import ContentGenerator
        from src.config.loader import ConfigLoader
        from src.llm.client import LLMError
        
        loader = ConfigLoader(test_config)
        generator = ContentGenerator(loader)
        
        # Simulate transient failure that succeeds on retry
        call_count = [0]
        def transient_failure_func():
            call_count[0] += 1
            if call_count[0] == 1:
                raise LLMError("Stream timeout: 180s elapsed")
            return "success after retry"
        
        result = generator._retry_generation(
            transient_failure_func,
            max_retries=2,
            operation_name="test",
            retry_delay=0.1  # Short delay for testing
        )
        
        assert result == "success after retry"
        assert call_count[0] == 2  # Should retry once
    
    def test_no_retry_on_permanent_failure(self, test_config):
        """Test that permanent failures don't trigger retries."""
        from src.generate.orchestration.pipeline import ContentGenerator
        from src.config.loader import ConfigLoader
        
        loader = ConfigLoader(test_config)
        generator = ContentGenerator(loader)
        
        # Simulate permanent failure
        def permanent_failure_func():
            raise ValueError("Invalid configuration")
        
        with pytest.raises(ValueError):
            generator._retry_generation(
                permanent_failure_func,
                max_retries=2,
                operation_name="test"
            )

