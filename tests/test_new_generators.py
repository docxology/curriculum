"""Tests for new content generators (study notes and labs)."""

import pytest
from pathlib import Path
from src.config.loader import ConfigLoader
from src.llm.client import OllamaClient
from src.generate.formats.study_notes import StudyNotesGenerator
from src.generate.formats.labs import LabGenerator

# All tests in this file require Ollama and are slow (>10s each)
pytestmark = [pytest.mark.integration, pytest.mark.slow]


@pytest.fixture
def test_config(tmp_path):
    """Create test configuration."""
    import yaml
    
    config_path = tmp_path / "config"
    config_path.mkdir()
    
    llm_config = {
        "llm": {
            "provider": "ollama",
            "model": "ministral-3:3b",
            "api_url": "http://localhost:11434/api/generate",
            "timeout": 60,
            "parameters": {"temperature": 0.7, "num_predict": 200}
        },
        "prompts": {
            "study_notes": {
                "system": "You are a biology educator.",
                "template": "Create study notes for {module_name}. Topics: {subtopics}."
            },
            "lab": {
                "system": "You are a lab instructor.",
                "template": "Create lab {lab_number} for {module_name}. Focus: {lab_focus}."
            }
        }
    }
    
    course_config = {
        "course": {"name": "Test Biology"},
        "modules": [{
            "id": 1,
            "name": "Cell Biology",
            "subtopics": ["Cell structure", "Cell function"],
            "learning_objectives": ["Understand cells"],
            "content_length": 200,
            "num_lectures": 2,
            "num_labs": 2,
            "num_diagrams": 1,
            "num_questions": 5
        }]
    }
    
    output_config = {
        "output": {
            "base_directory": str(tmp_path / "output"),
            "directories": {
                "study_notes": "study_notes",
                "labs": "labs"
            }
        }
    }
    
    with open(config_path / "llm_config.yaml", "w") as f:
        yaml.dump(llm_config, f)
    with open(config_path / "course_config.yaml", "w") as f:
        yaml.dump(course_config, f)
    with open(config_path / "output_config.yaml", "w") as f:
        yaml.dump(output_config, f)
        
    return ConfigLoader(config_path)


@pytest.fixture
def llm_client(test_config):
    """Create LLM client."""
    return OllamaClient(test_config.get_llm_parameters())


class TestStudyNotesGenerator:
    """Test StudyNotesGenerator class."""
    
    def test_init(self, test_config, llm_client):
        """Test initialization."""
        generator = StudyNotesGenerator(test_config, llm_client)
        assert generator is not None
        assert generator.config_loader == test_config
        assert generator.llm_client == llm_client
        
    def test_generate_study_notes(self, test_config, llm_client, skip_if_no_ollama):
        """Test study notes generation."""
        generator = StudyNotesGenerator(test_config, llm_client)
        
        module_info = {
            "id": 1,
            "name": "Cell Biology",
            "subtopics": ["Cell structure", "Cell function"],
            "learning_objectives": ["Understand cells"]
        }
        
        notes = generator.generate_study_notes(module_info)
        
        assert isinstance(notes, str)
        assert len(notes) > 50
        assert "Cell Biology" in notes
        
    def test_save_study_notes(self, test_config, llm_client, tmp_path):
        """Test saving study notes to file."""
        generator = StudyNotesGenerator(test_config, llm_client)
        
        notes = "# Cell Biology - Study Notes\n\nKey concepts..."
        output_dir = tmp_path / "study_notes"
        module_info = {"id": 1, "name": "Cell Biology"}
        
        filepath = generator.save_study_notes(notes, module_info, output_dir)
        
        assert filepath.exists()
        assert filepath.suffix == ".md"
        assert "study_notes" in str(filepath)


class TestLabGenerator:
    """Test LabGenerator class."""
    
    def test_init(self, test_config, llm_client):
        """Test initialization."""
        generator = LabGenerator(test_config, llm_client)
        assert generator is not None
        assert generator.config_loader == test_config
        assert generator.llm_client == llm_client
        
    def test_generate_lab(self, test_config, llm_client, skip_if_no_ollama):
        """Test lab generation."""
        generator = LabGenerator(test_config, llm_client)
        
        module_info = {
            "id": 1,
            "name": "Cell Biology",
            "subtopics": ["Cell structure", "Microscopy"],
            "learning_objectives": ["Use microscope", "Identify cells"]
        }
        
        lab = generator.generate_lab(module_info, lab_number=1)
        
        assert isinstance(lab, str)
        assert len(lab) > 50
        assert "Cell Biology" in lab
        assert "Laboratory Exercise 1" in lab
        
    def test_generate_multiple_labs(self, test_config, llm_client, skip_if_no_ollama):
        """Test generating multiple labs for same module."""
        generator = LabGenerator(test_config, llm_client)
        
        module_info = {
            "id": 1,
            "name": "Cell Biology",
            "subtopics": ["Cell structure", "Microscopy", "Staining"],
            "learning_objectives": ["Lab skills"]
        }
        
        lab1 = generator.generate_lab(module_info, lab_number=1)
        lab2 = generator.generate_lab(module_info, lab_number=2)
        
        assert isinstance(lab1, str)
        assert isinstance(lab2, str)
        assert "Laboratory Exercise 1" in lab1
        assert "Laboratory Exercise 2" in lab2
        
    def test_save_lab(self, test_config, llm_client, tmp_path):
        """Test saving lab to file."""
        generator = LabGenerator(test_config, llm_client)
        
        lab = "# Cell Biology - Laboratory Exercise 1\n\nProcedure..."
        output_dir = tmp_path / "labs"
        module_info = {"id": 1, "name": "Cell Biology"}
        
        filepath = generator.save_lab(lab, module_info, 1, output_dir)
        
        assert filepath.exists()
        assert filepath.suffix == ".md"
        assert "lab1" in str(filepath)

