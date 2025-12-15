"""Tests for website generator module."""

import json
import pytest
from pathlib import Path
from src.config.loader import ConfigLoader
from src.website.generator import WebsiteGenerator


@pytest.fixture
def config_dir(tmp_path):
    """Create a temporary config directory with test files."""
    config_path = tmp_path / "config"
    config_path.mkdir()
    
    # Create test course config
    course_config = {
        "course": {
            "name": "Test Biology",
            "description": "Test course",
            "level": "Intro",
            "defaults": {
                "num_modules": 2,
                "total_sessions": 6,
                "sessions_per_module": None
            }
        }
    }
    
    # Create test LLM config
    llm_config = {
        "llm": {
            "provider": "ollama",
            "model": "ministral-3:3b",
            "api_url": "http://localhost:11434/api/generate",
            "parameters": {"temperature": 0.7}
        },
        "prompts": {"outline": {"system": "Test", "template": "Test"}}
    }
    
    # Create test output config
    output_config = {
        "output": {
            "base_directory": "output",
            "directories": {
                "outlines": "outlines",
                "modules": "modules",
                "website": "website"
            }
        }
    }
    
    import yaml
    with open(config_path / "course_config.yaml", "w") as f:
        yaml.dump(course_config, f)
    with open(config_path / "llm_config.yaml", "w") as f:
        yaml.dump(llm_config, f)
    with open(config_path / "output_config.yaml", "w") as f:
        yaml.dump(output_config, f)
    
    return config_path


@pytest.fixture
def sample_outline(tmp_path):
    """Create a sample outline JSON file."""
    outline_data = {
        "course_metadata": {
            "name": "Test Biology",
            "description": "Test course",
            "level": "Intro"
        },
        "modules": [
            {
                "module_id": 1,
                "module_name": "Cell Biology",
                "module_description": "Introduction to cells",
                "sessions": [
                    {
                        "session_number": 1,
                        "session_title": "Introduction to Cells",
                        "subtopics": ["Cell theory"],
                        "learning_objectives": ["Understand cells"],
                        "key_concepts": ["Cell membrane"]
                    }
                ]
            }
        ]
    }
    
    outline_file = tmp_path / "outline.json"
    outline_file.write_text(json.dumps(outline_data), encoding='utf-8')
    return outline_file


@pytest.fixture
def sample_module_structure(tmp_path):
    """Create a sample module directory structure with content files."""
    module_dir = tmp_path / "modules" / "module_01_cell_biology"
    session_dir = module_dir / "session_01"
    session_dir.mkdir(parents=True)
    
    # Create sample content files
    (session_dir / "lecture.md").write_text("# Lecture\n\nContent here")
    (session_dir / "lab.md").write_text("# Lab\n\nLab content")
    (session_dir / "study_notes.md").write_text("# Notes\n\nNotes content")
    (session_dir / "questions.md").write_text("# Questions\n\nQ1: Test?")
    (session_dir / "diagram_1.mmd").write_text("graph TD\nA-->B")
    
    return module_dir


class TestWebsiteGenerator:
    """Test WebsiteGenerator class."""
    
    def test_init_with_config_loader(self, config_dir):
        """Test initialization with ConfigLoader."""
        config_loader = ConfigLoader(config_dir)
        generator = WebsiteGenerator(config_loader)
        
        assert generator.config_loader == config_loader
    
    def test_generate_with_custom_outline_and_output(self, config_dir, sample_outline, tmp_path):
        """Test generate with custom outline and output paths."""
        config_loader = ConfigLoader(config_dir)
        generator = WebsiteGenerator(config_loader)
        
        output_path = tmp_path / "custom_website.html"
        
        # Create minimal module structure
        modules_dir = tmp_path / "output" / "modules"
        module_dir = modules_dir / "module_01_cell_biology"
        session_dir = module_dir / "session_01"
        session_dir.mkdir(parents=True)
        (session_dir / "lecture.md").write_text("# Test Lecture")
        
        # Update output config to point to test modules directory
        import yaml
        output_config_path = config_dir / "output_config.yaml"
        with open(output_config_path) as f:
            output_config = yaml.safe_load(f)
        output_config["output"]["base_directory"] = str(tmp_path / "output")
        with open(output_config_path, "w") as f:
            yaml.dump(output_config, f)
        
        config_loader = ConfigLoader(config_dir)
        generator = WebsiteGenerator(config_loader)
        
        result_path = generator.generate(
            outline_path=sample_outline,
            output_path=output_path
        )
        
        assert result_path == output_path
        assert output_path.exists()
        assert output_path.is_file()
        
        # Check HTML content
        html_content = output_path.read_text(encoding='utf-8')
        assert "<!DOCTYPE html>" in html_content
        assert "Test Biology" in html_content
    
    def test_generate_auto_discovers_outline(self, config_dir, tmp_path, monkeypatch):
        """Test generate auto-discovers latest outline."""
        monkeypatch.chdir(tmp_path)
        
        config_loader = ConfigLoader(config_dir)
        generator = WebsiteGenerator(config_loader)
        
        # Create outline in expected location
        outlines_dir = tmp_path / "output" / "outlines"
        outlines_dir.mkdir(parents=True)
        
        outline_data = {
            "course_metadata": {"name": "Test", "description": "Test", "level": "Test"},
            "modules": [
                {
                    "module_id": 1,
                    "module_name": "Test Module",
                    "sessions": []
                }
            ]
        }
        outline_file = outlines_dir / "course_outline_test.json"
        outline_file.write_text(json.dumps(outline_data), encoding='utf-8')
        
        # Create output config pointing to tmp_path
        import yaml
        output_config_path = config_dir / "output_config.yaml"
        with open(output_config_path) as f:
            output_config = yaml.safe_load(f)
        output_config["output"]["base_directory"] = str(tmp_path / "output")
        with open(output_config_path, "w") as f:
            yaml.dump(output_config, f)
        
        config_loader = ConfigLoader(config_dir)
        generator = WebsiteGenerator(config_loader)
        
        result_path = generator.generate()
        
        assert result_path.exists()
        assert result_path.name == "index.html"
    
    def test_generate_raises_file_not_found_no_outline(self, config_dir, tmp_path, monkeypatch):
        """Test generate raises FileNotFoundError when no outline found."""
        monkeypatch.chdir(tmp_path)
        
        config_loader = ConfigLoader(config_dir)
        generator = WebsiteGenerator(config_loader)
        
        with pytest.raises(FileNotFoundError, match="No outline JSON found"):
            generator.generate()
    
    def test_generate_raises_value_error_empty_modules(self, config_dir, sample_outline, tmp_path):
        """Test generate raises ValueError when outline has no modules."""
        config_loader = ConfigLoader(config_dir)
        generator = WebsiteGenerator(config_loader)
        
        # Create outline with empty modules
        empty_outline = tmp_path / "empty_outline.json"
        empty_outline.write_text(
            json.dumps({"course_metadata": {}, "modules": []}),
            encoding='utf-8'
        )
        
        with pytest.raises(ValueError, match="No modules found in outline"):
            generator.generate(outline_path=empty_outline)
    
    def test_generate_handles_missing_content_files(self, config_dir, sample_outline, tmp_path):
        """Test generate handles missing content files gracefully."""
        config_loader = ConfigLoader(config_dir)
        generator = WebsiteGenerator(config_loader)
        
        # Create module directory but no content files
        import yaml
        output_config_path = config_dir / "output_config.yaml"
        with open(output_config_path) as f:
            output_config = yaml.safe_load(f)
        output_config["output"]["base_directory"] = str(tmp_path / "output")
        with open(output_config_path, "w") as f:
            yaml.dump(output_config, f)
        
        modules_dir = tmp_path / "output" / "modules"
        module_dir = modules_dir / "module_01_cell_biology"
        session_dir = module_dir / "session_01"
        session_dir.mkdir(parents=True)
        # No content files created
        
        config_loader = ConfigLoader(config_dir)
        generator = WebsiteGenerator(config_loader)
        
        # Should not raise, but generate HTML with empty content
        result_path = generator.generate(
            outline_path=sample_outline,
            output_path=tmp_path / "test.html"
        )
        
        assert result_path.exists()
        html_content = result_path.read_text(encoding='utf-8')
        assert "<!DOCTYPE html>" in html_content
    
    def test_process_module_with_content(self, config_dir, sample_module_structure):
        """Test _process_module with existing content."""
        config_loader = ConfigLoader(config_dir)
        generator = WebsiteGenerator(config_loader)
        
        module_data = {
            "module_id": 1,
            "module_name": "Cell Biology",
            "module_description": "Introduction to cells",
            "sessions": [
                {
                    "session_number": 1,
                    "session_title": "Introduction to Cells",
                    "subtopics": ["Cell theory"],
                    "learning_objectives": ["Understand cells"],
                    "key_concepts": ["Cell membrane"]
                }
            ]
        }
        
        modules_dir = sample_module_structure.parent
        result = generator._process_module(module_data, modules_dir)
        
        assert result["module_id"] == 1
        assert result["module_name"] == "Cell Biology"
        assert len(result["sessions"]) == 1
        
        session = result["sessions"][0]
        assert session["session_number"] == 1
        assert "content" in session
        # Should have loaded content for available files
        assert "lecture" in session["content"] or len(session["content"]) > 0
    
    def test_process_module_missing_sessions(self, config_dir, tmp_path):
        """Test _process_module with missing session directories."""
        config_loader = ConfigLoader(config_dir)
        generator = WebsiteGenerator(config_loader)
        
        module_data = {
            "module_id": 1,
            "module_name": "Test Module",
            "sessions": [
                {
                    "session_number": 1,
                    "session_title": "Session 1",
                    "subtopics": [],
                    "learning_objectives": [],
                    "key_concepts": []
                }
            ]
        }
        
        modules_dir = tmp_path / "modules"
        modules_dir.mkdir()
        # Don't create session directory
        
        result = generator._process_module(module_data, modules_dir)
        
        assert result["module_id"] == 1
        assert len(result["sessions"]) == 1
        # Session should exist but with empty or minimal content
        session = result["sessions"][0]
        assert session["session_number"] == 1
    
    def test_process_module_partial_content(self, config_dir, tmp_path):
        """Test _process_module with partial content (some files missing)."""
        config_loader = ConfigLoader(config_dir)
        generator = WebsiteGenerator(config_loader)
        
        # Create module with only some content files
        # Use slugify pattern: module_{id:02d}_{name}
        from src.utils.helpers import slugify
        module_slug = slugify("module_01_Test Module")
        module_dir = tmp_path / "modules" / module_slug
        session_dir = module_dir / "session_01"
        session_dir.mkdir(parents=True)
        (session_dir / "lecture.md").write_text("# Lecture")
        # Missing lab.md, study_notes.md, etc.
        
        module_data = {
            "module_id": 1,
            "module_name": "Test Module",
            "sessions": [
                {
                    "session_number": 1,
                    "session_title": "Session 1",
                    "subtopics": [],
                    "learning_objectives": [],
                    "key_concepts": []
                }
            ]
        }
        
        result = generator._process_module(module_data, tmp_path / "modules")
        
        assert len(result["sessions"]) == 1
        session = result["sessions"][0]
        # Should have loaded lecture content
        assert "lecture" in session.get("content", {})
    
    def test_process_module_with_diagrams(self, config_dir, tmp_path):
        """Test _process_module loads diagram files."""
        config_loader = ConfigLoader(config_dir)
        generator = WebsiteGenerator(config_loader)
        
        # Create module with diagram files
        from src.utils.helpers import slugify
        module_slug = slugify("module_01_Test Module")
        module_dir = tmp_path / "modules" / module_slug
        session_dir = module_dir / "session_01"
        session_dir.mkdir(parents=True)
        (session_dir / "diagram_1.mmd").write_text("graph TD\nA-->B")
        (session_dir / "diagram_2.mmd").write_text("graph LR\nC-->D")
        
        module_data = {
            "module_id": 1,
            "module_name": "Test Module",
            "sessions": [
                {
                    "session_number": 1,
                    "session_title": "Session 1",
                    "subtopics": [],
                    "learning_objectives": [],
                    "key_concepts": []
                }
            ]
        }
        
        result = generator._process_module(module_data, tmp_path / "modules")
        
        session = result["sessions"][0]
        content = session.get("content", {})
        # Should have loaded diagram content
        assert "diagram_1" in content
        assert "diagram_2" in content
    
    def test_process_module_with_secondary_content(self, config_dir, tmp_path):
        """Test _process_module loads secondary content types."""
        config_loader = ConfigLoader(config_dir)
        generator = WebsiteGenerator(config_loader)
        
        # Create module with secondary content
        from src.utils.helpers import slugify
        module_slug = slugify("module_01_Test Module")
        module_dir = tmp_path / "modules" / module_slug
        session_dir = module_dir / "session_01"
        session_dir.mkdir(parents=True)
        (session_dir / "application.md").write_text("# Application")
        (session_dir / "visualization.mmd").write_text("graph TD\nA-->B")
        
        module_data = {
            "module_id": 1,
            "module_name": "Test Module",
            "sessions": [
                {
                    "session_number": 1,
                    "session_title": "Session 1",
                    "subtopics": [],
                    "learning_objectives": [],
                    "key_concepts": []
                }
            ]
        }
        
        result = generator._process_module(module_data, tmp_path / "modules")
        
        session = result["sessions"][0]
        content = session.get("content", {})
        # Should have loaded secondary content
        assert "application" in content
        assert "visualization" in content

