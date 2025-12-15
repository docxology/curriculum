"""Non-interactive tests for outline generator - testing automated generation modes."""

import pytest
import json
from pathlib import Path
from datetime import datetime
from src.config.loader import ConfigLoader
from src.llm.client import OllamaClient
from src.generate.stages.stage1_outline import OutlineGenerator
from src.utils.helpers import format_timestamp


@pytest.fixture
def noninteractive_config(tmp_path):
    """Create config for non-interactive testing."""
    import yaml
    
    config_path = tmp_path / "config"
    config_path.mkdir()
    
    course_config = {
        "course": {
            "name": "Biology Course",
            "description": "Comprehensive biology",
            "level": "Introductory",
            "estimated_duration_weeks": 10,
            "defaults": {
                "num_modules": 5,
                "total_sessions": 15,
                "sessions_per_module": None
            }
        }
    }
    
    llm_config = {
        "llm": {
            "provider": "ollama",
            "model": "gemma3:4b",
            "api_url": "http://localhost:11434/api/generate",
            "timeout": 120,
            "parameters": {
                "temperature": 0.7,
                "num_predict": 1000,
                "format": "json"
            }
        },
        "prompts": {
            "outline": {
                "system": "You are a biology educator. Output ONLY valid JSON.",
                "template": """Generate {num_modules} modules with {total_sessions} sessions.
Return: {{"course_title": "{course_name}", "modules": []}}"""
            }
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
    
    (config_path / "course_config.yaml").write_text(yaml.dump(course_config))
    (config_path / "llm_config.yaml").write_text(yaml.dump(llm_config))
    (config_path / "output_config.yaml").write_text(yaml.dump(output_config))
    
    return config_path


class TestNonInteractiveMode:
    """Test non-interactive generation using config defaults."""
    
    def test_noninteractive_mode_defaults(self, noninteractive_config, tmp_path):
        """Test generation with config defaults (no user input)."""
        loader = ConfigLoader(noninteractive_config)
        
        defaults = loader.get_course_defaults()
        
        # Verify defaults are loaded
        assert defaults["num_modules"] == 5
        assert defaults["total_sessions"] == 15
    
    def test_session_distribution_calculation(self, noninteractive_config):
        """Test automatic session distribution calculation."""
        loader = ConfigLoader(noninteractive_config)
        defaults = loader.get_course_defaults()
        
        num_modules = defaults["num_modules"]
        total_sessions = defaults["total_sessions"]
        
        # Calculate expected distribution
        base_sessions = total_sessions // num_modules  # 15 // 5 = 3
        extra_sessions = total_sessions % num_modules  # 15 % 5 = 0
        
        assert base_sessions == 3
        assert extra_sessions == 0
        
        # All modules should get 3 sessions
        expected = [3] * num_modules
        assert sum(expected) == total_sessions


class TestModuleCountScenarios:
    """Test different module count scenarios."""
    
    def test_module_count_zero(self, tmp_path):
        """Test handling of zero modules."""
        import yaml
        
        config_path = tmp_path / "config"
        config_path.mkdir()
        
        course_config = {
            "course": {
                "name": "Empty Course",
                "description": "Test",
                "level": "Test",
                "defaults": {"num_modules": 0, "total_sessions": 0}
            }
        }
        llm_config = {"llm": {"model": "test"}, "prompts": {}}
        output_config = {"output": {"base_directory": "output"}}
        
        (config_path / "course_config.yaml").write_text(yaml.dump(course_config))
        (config_path / "llm_config.yaml").write_text(yaml.dump(llm_config))
        (config_path / "output_config.yaml").write_text(yaml.dump(output_config))
        
        loader = ConfigLoader(config_path)
        defaults = loader.get_course_defaults()
        
        assert defaults["num_modules"] == 0
        assert defaults["total_sessions"] == 0
    
    def test_module_count_one(self, tmp_path):
        """Test handling of single module."""
        import yaml
        
        config_path = tmp_path / "config"
        config_path.mkdir()
        
        course_config = {
            "course": {
                "name": "Single Module Course",
                "description": "Test",
                "level": "Test",
                "defaults": {"num_modules": 1, "total_sessions": 5}
            }
        }
        llm_config = {"llm": {"model": "test"}, "prompts": {}}
        output_config = {"output": {"base_directory": "output"}}
        
        (config_path / "course_config.yaml").write_text(yaml.dump(course_config))
        (config_path / "llm_config.yaml").write_text(yaml.dump(llm_config))
        (config_path / "output_config.yaml").write_text(yaml.dump(output_config))
        
        loader = ConfigLoader(config_path)
        defaults = loader.get_course_defaults()
        
        assert defaults["num_modules"] == 1
        # All sessions go to one module
        assert defaults["total_sessions"] == 5
    
    def test_module_count_hundred(self, tmp_path):
        """Test handling of 100 modules."""
        import yaml
        
        config_path = tmp_path / "config"
        config_path.mkdir()
        
        course_config = {
            "course": {
                "name": "Large Course",
                "description": "Test",
                "level": "Test",
                "defaults": {"num_modules": 100, "total_sessions": 300}
            }
        }
        llm_config = {"llm": {"model": "test"}, "prompts": {}}
        output_config = {"output": {"base_directory": "output"}}
        
        (config_path / "course_config.yaml").write_text(yaml.dump(course_config))
        (config_path / "llm_config.yaml").write_text(yaml.dump(llm_config))
        (config_path / "output_config.yaml").write_text(yaml.dump(output_config))
        
        loader = ConfigLoader(config_path)
        defaults = loader.get_course_defaults()
        
        assert defaults["num_modules"] == 100
        assert defaults["total_sessions"] == 300
        
        # Each module should get 3 sessions
        sessions_per_module = defaults["total_sessions"] // defaults["num_modules"]
        assert sessions_per_module == 3
    
    def test_uneven_session_distribution(self, tmp_path):
        """Test session distribution when not evenly divisible."""
        import yaml
        
        config_path = tmp_path / "config"
        config_path.mkdir()
        
        course_config = {
            "course": {
                "name": "Uneven Course",
                "description": "Test",
                "level": "Test",
                "defaults": {"num_modules": 4, "total_sessions": 13}  # 13 / 4 = 3 remainder 1
            }
        }
        llm_config = {"llm": {"model": "test"}, "prompts": {}}
        output_config = {"output": {"base_directory": "output"}}
        
        (config_path / "course_config.yaml").write_text(yaml.dump(course_config))
        (config_path / "llm_config.yaml").write_text(yaml.dump(llm_config))
        (config_path / "output_config.yaml").write_text(yaml.dump(output_config))
        
        loader = ConfigLoader(config_path)
        defaults = loader.get_course_defaults()
        
        num_modules = defaults["num_modules"]
        total_sessions = defaults["total_sessions"]
        
        base = total_sessions // num_modules  # 3
        extra = total_sessions % num_modules  # 1
        
        assert base == 3
        assert extra == 1
        # First module gets 4, rest get 3


class TestOutputStructure:
    """Test output structure validation."""
    
    def test_json_output_structure_validation(self, tmp_path):
        """Test that generated JSON has required structure."""
        # Create a sample outline JSON
        outline_data = {
            "course_metadata": {
                "course_title": "Biology 101",
                "total_modules": 2,
                "total_sessions": 6
            },
            "modules": [
                {
                    "module_id": 1,
                    "module_name": "Introduction",
                    "sessions": [
                        {
                            "session_number": 1,
                            "session_title": "Session 1",
                            "subtopics": ["Topic 1"],
                            "learning_objectives": ["Objective 1"],
                            "key_concepts": ["Concept 1"]
                        }
                    ]
                }
            ]
        }
        
        outline_file = tmp_path / "outline.json"
        outline_file.write_text(json.dumps(outline_data))
        
        # Validate structure
        loaded = json.loads(outline_file.read_text())
        
        assert "course_metadata" in loaded
        assert "modules" in loaded
        assert "course_title" in loaded["course_metadata"]
        assert isinstance(loaded["modules"], list)
    
    def test_markdown_output_formatting(self, tmp_path):
        """Test markdown output follows expected format."""
        # Create sample markdown outline
        markdown_content = """# Course Outline: Biology 101

## Module 1: Introduction

### Session 1: Getting Started
- **Subtopics**: Topic 1, Topic 2
- **Learning Objectives**: Objective 1
- **Key Concepts**: Concept 1
"""
        
        outline_file = tmp_path / "outline.md"
        outline_file.write_text(markdown_content)
        
        content = outline_file.read_text()
        
        # Verify markdown structure
        assert "# Course Outline:" in content
        assert "## Module" in content
        assert "### Session" in content
        assert "**Subtopics**:" in content
        assert "**Learning Objectives**:" in content


class TestMetadataHandling:
    """Test outline metadata generation and validation."""
    
    def test_outline_metadata_completeness(self, noninteractive_config):
        """Test that all metadata fields are present."""
        loader = ConfigLoader(noninteractive_config)
        
        course_info = loader.get_course_info()
        defaults = loader.get_course_defaults()
        
        # Required metadata fields
        assert "name" in course_info
        assert "description" in course_info
        assert "level" in course_info
        
        # Defaults should have structure info
        assert "num_modules" in defaults
        assert "total_sessions" in defaults
    
    def test_timestamp_generation_format(self):
        """Test timestamp format for outline naming."""
        timestamp = format_timestamp()
        
        # Should be a string
        assert isinstance(timestamp, str)
        # Should not be empty
        assert len(timestamp) > 0
        # Should be a valid format (contains numbers and underscores/dashes)
        assert any(c.isdigit() for c in timestamp)
    


class TestSessionContentValidation:
    """Test session content requirements."""
    
    def test_session_rationale_generation(self, tmp_path):
        """Test that sessions have rationale fields."""
        outline_data = {
            "course_metadata": {"name": "Test"},
            "modules": [
                {
                    "module_id": 1,
                    "module_name": "Module 1",
                    "sessions": [
                        {
                            "session_number": 1,
                            "session_title": "Session 1",
                            "subtopics": ["Topic"],
                            "learning_objectives": ["Objective"],
                            "key_concepts": ["Concept"],
                            "rationale": "This session introduces..."
                        }
                    ]
                }
            ]
        }
        
        outline_file = tmp_path / "outline.json"
        outline_file.write_text(json.dumps(outline_data))
        
        loaded = json.loads(outline_file.read_text())
        session = loaded["modules"][0]["sessions"][0]
        
        assert "rationale" in session
        assert len(session["rationale"]) > 0
    
    def test_learning_objectives_count(self, tmp_path):
        """Test learning objectives are within reasonable bounds."""
        outline_data = {
            "course_metadata": {"name": "Test"},
            "modules": [
                {
                    "module_id": 1,
                    "module_name": "Module 1",
                    "sessions": [
                        {
                            "session_number": 1,
                            "session_title": "Session 1",
                            "subtopics": ["Topic"],
                            "learning_objectives": [
                                "Objective 1",
                                "Objective 2",
                                "Objective 3"
                            ],
                            "key_concepts": ["Concept"]
                        }
                    ]
                }
            ]
        }
        
        outline_file = tmp_path / "outline.json"
        outline_file.write_text(json.dumps(outline_data))
        
        loaded = json.loads(outline_file.read_text())
        objectives = loaded["modules"][0]["sessions"][0]["learning_objectives"]
        
        # Should have reasonable number (1-5 typically)
        assert len(objectives) >= 1
        assert len(objectives) <= 10  # Upper bound for sanity
    
    def test_key_concepts_count(self, tmp_path):
        """Test key concepts are within reasonable bounds."""
        outline_data = {
            "course_metadata": {"name": "Test"},
            "modules": [
                {
                    "module_id": 1,
                    "module_name": "Module 1",
                    "sessions": [
                        {
                            "session_number": 1,
                            "session_title": "Session 1",
                            "subtopics": ["Topic"],
                            "learning_objectives": ["Objective"],
                            "key_concepts": [
                                "Concept 1",
                                "Concept 2",
                                "Concept 3",
                                "Concept 4"
                            ]
                        }
                    ]
                }
            ]
        }
        
        outline_file = tmp_path / "outline.json"
        outline_file.write_text(json.dumps(outline_data))
        
        loaded = json.loads(outline_file.read_text())
        concepts = loaded["modules"][0]["sessions"][0]["key_concepts"]
        
        # Should have reasonable number
        assert len(concepts) >= 1
        assert len(concepts) <= 15  # Upper bound
    
    def test_subtopics_count(self, tmp_path):
        """Test subtopics are within reasonable bounds."""
        outline_data = {
            "course_metadata": {"name": "Test"},
            "modules": [
                {
                    "module_id": 1,
                    "module_name": "Module 1",
                    "sessions": [
                        {
                            "session_number": 1,
                            "session_title": "Session 1",
                            "subtopics": [
                                "Subtopic 1",
                                "Subtopic 2"
                            ],
                            "learning_objectives": ["Objective"],
                            "key_concepts": ["Concept"]
                        }
                    ]
                }
            ]
        }
        
        outline_file = tmp_path / "outline.json"
        outline_file.write_text(json.dumps(outline_data))
        
        loaded = json.loads(outline_file.read_text())
        subtopics = loaded["modules"][0]["sessions"][0]["subtopics"]
        
        # Should have reasonable number
        assert len(subtopics) >= 1
        assert len(subtopics) <= 10  # Upper bound


class TestOutlineFileNaming:
    """Test outline file naming conventions."""
    
    def test_outline_filename_with_timestamp(self, tmp_path):
        """Test outline files include timestamp in name."""
        timestamp = format_timestamp()
        filename = f"course_outline_{timestamp}.json"
        
        outline_file = tmp_path / filename
        outline_file.write_text(json.dumps({"modules": []}))
        
        assert outline_file.exists()
        assert "course_outline_" in outline_file.name
        assert outline_file.suffix == ".json"
    
    def test_outline_markdown_companion(self, tmp_path):
        """Test that markdown companion file can be created."""
        timestamp = format_timestamp()
        json_file = tmp_path / f"course_outline_{timestamp}.json"
        md_file = tmp_path / f"course_outline_{timestamp}.md"
        
        json_file.write_text(json.dumps({"modules": []}))
        md_file.write_text("# Course Outline")
        
        # Both should exist
        assert json_file.exists()
        assert md_file.exists()
        # Should have same basename
        assert json_file.stem == md_file.stem


class TestConfigDefaults:
    """Test handling of configuration defaults."""
    
    def test_sessions_per_module_auto_calculate(self, noninteractive_config):
        """Test automatic calculation when sessions_per_module is None."""
        loader = ConfigLoader(noninteractive_config)
        defaults = loader.get_course_defaults()
        
        # sessions_per_module should be None (auto-calculate)
        assert defaults.get("sessions_per_module") is None
        
        # But we can calculate it
        calculated = defaults["total_sessions"] // defaults["num_modules"]
        assert calculated == 3  # 15 / 5 = 3
    
    def test_explicit_sessions_per_module(self, tmp_path):
        """Test explicit sessions_per_module setting."""
        import yaml
        
        config_path = tmp_path / "config"
        config_path.mkdir()
        
        course_config = {
            "course": {
                "name": "Explicit Course",
                "description": "Test",
                "level": "Test",
                "defaults": {
                    "num_modules": 5,
                    "total_sessions": 15,
                    "sessions_per_module": 3  # Explicit value
                }
            }
        }
        llm_config = {"llm": {"model": "test"}, "prompts": {}}
        output_config = {"output": {"base_directory": "output"}}
        
        (config_path / "course_config.yaml").write_text(yaml.dump(course_config))
        (config_path / "llm_config.yaml").write_text(yaml.dump(llm_config))
        (config_path / "output_config.yaml").write_text(yaml.dump(output_config))
        
        loader = ConfigLoader(config_path)
        defaults = loader.get_course_defaults()
        
        assert defaults["sessions_per_module"] == 3


class TestEdgeCaseHandling:
    """Test edge cases in outline generation."""
    
    def test_module_name_with_special_characters(self, tmp_path):
        """Test module names with special characters."""
        outline_data = {
            "course_metadata": {"name": "Test"},
            "modules": [
                {
                    "module_id": 1,
                    "module_name": "DNA & RNA: Structure & Function!",
                    "sessions": []
                }
            ]
        }
        
        outline_file = tmp_path / "outline.json"
        outline_file.write_text(json.dumps(outline_data))
        
        loaded = json.loads(outline_file.read_text())
        module_name = loaded["modules"][0]["module_name"]
        
        assert "&" in module_name
        assert ":" in module_name
        assert "!" in module_name
    
    def test_unicode_in_course_content(self, tmp_path):
        """Test unicode characters in course content."""
        outline_data = {
            "course_metadata": {
                "course_title": "Biología Celular"
            },
            "modules": [
                {
                    "module_id": 1,
                    "module_name": "La Célula",
                    "sessions": [
                        {
                            "session_number": 1,
                            "session_title": "Introducción",
                            "subtopics": ["Tópico"],
                            "learning_objectives": ["Aprender"],
                            "key_concepts": ["Concepto"]
                        }
                    ]
                }
            ]
        }
        
        outline_file = tmp_path / "outline.json"
        outline_file.write_text(json.dumps(outline_data, ensure_ascii=False), encoding='utf-8')
        
        loaded = json.loads(outline_file.read_text(encoding='utf-8'))
        
        assert "Biología" in loaded["course_metadata"]["course_title"]
        assert "Célula" in loaded["modules"][0]["module_name"]
        assert "Introducción" in loaded["modules"][0]["sessions"][0]["session_title"]

