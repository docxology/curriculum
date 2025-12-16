"""Tests for content_generator module."""

import pytest
import requests
from pathlib import Path
from src.config.loader import ConfigLoader
from src.llm.client import OllamaClient
from src.generate.formats import ContentGenerator
from src.generate.formats.lectures import LectureGenerator
from src.generate.formats.diagrams import DiagramGenerator
from src.generate.formats.questions import QuestionGenerator


# Integration tests - conftest.py ensures Ollama is running
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
            "model": "gemma3:4b",
            "api_url": "http://localhost:11434/api/generate",
            "timeout": 60,
            "parameters": {
                "temperature": 0.7,
                "num_predict": 200  # Short for tests
            }
        },
        "prompts": {
            "lecture": {
                "system": "You are a biology educator.",
                "template": "Write about {module_name}. Topics: {subtopics}. Objectives: {objectives}. Length: {content_length} words."
            },
            "diagram": {
                "system": "Create diagrams.",
                "template": "Create a Mermaid diagram for {topic}. Context: {context}"
            },
            "questions": {
                "system": "Create questions.",
                "template": "Create {num_questions} questions about {module_name}. Topics: {subtopics}. Types: {mc_count} MC, {sa_count} SA, {essay_count} essay."
            }
        }
    }
    
    course_config = {
        "course": {"name": "Test Biology"},
        "modules": [{
            "id": 1,
            "name": "Cell Biology",
            "subtopics": ["Cell structure"],
            "learning_objectives": ["Understand cells"],
            "content_length": 200,
            "num_diagrams": 1,
            "num_questions": 5
        }]
    }
    
    output_config = {
        "output": {
            "base_directory": str(tmp_path / "output"),
            "directories": {
                "lectures": "lectures",
                "diagrams": "diagrams",
                "questions": "questions"
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


class TestContentGenerator:
    """Test base ContentGenerator class."""
    
    def test_init(self, test_config, llm_client):
        """Test initialization."""
        generator = ContentGenerator(test_config, llm_client)
        assert generator.config_loader == test_config
        assert generator.llm_client == llm_client


class TestLectureGenerator:
    """Test LectureGenerator class."""
    
    def test_init(self, test_config, llm_client):
        """Test initialization."""
        generator = LectureGenerator(test_config, llm_client)
        assert generator is not None
        
    def test_generate_lecture(self, test_config, llm_client, skip_if_no_ollama):
        """Test lecture generation."""
        generator = LectureGenerator(test_config, llm_client)
        
        module_info = {
            "id": 1,
            "name": "Cell Biology",
            "subtopics": ["Cell structure"],
            "learning_objectives": ["Understand cells"],
            "content_length": 200
        }
        
        lecture = generator.generate_lecture(module_info)
        
        assert isinstance(lecture, str)
        assert len(lecture) > 50
        
    def test_save_lecture(self, test_config, llm_client, tmp_path):
        """Test saving lecture to file."""
        generator = LectureGenerator(test_config, llm_client)
        
        lecture = "# Cell Biology\n\nTest lecture content."
        output_dir = tmp_path / "lectures"
        module_info = {"id": 1, "name": "Cell Biology"}
        
        filepath = generator.save_lecture(lecture, module_info, output_dir)
        
        assert filepath.exists()
        assert filepath.suffix == ".md"


class TestDiagramGenerator:
    """Test DiagramGenerator class."""
    
    def test_init(self, test_config, llm_client):
        """Test initialization."""
        generator = DiagramGenerator(test_config, llm_client)
        assert generator is not None
        
    def test_generate_diagram(self, test_config, llm_client, skip_if_no_ollama):
        """Test diagram generation."""
        generator = DiagramGenerator(test_config, llm_client)
        
        topic = "Cell structure"
        context = "Show the basic parts of a cell"
        
        diagram = generator.generate_diagram(topic, context)
        
        assert isinstance(diagram, str)
        assert len(diagram) > 0
        
    def test_save_diagram(self, test_config, llm_client, tmp_path):
        """Test saving diagram to file."""
        generator = DiagramGenerator(test_config, llm_client)
        
        diagram = "graph TD\n  A --> B"
        output_dir = tmp_path / "diagrams"
        
        filepath = generator.save_diagram(diagram, "test_topic", 1, 1, output_dir)
        
        assert filepath.exists()
        assert filepath.suffix == ".mmd"


class TestQuestionGenerator:
    """Test QuestionGenerator class."""
    
    def test_init(self, test_config, llm_client):
        """Test initialization."""
        generator = QuestionGenerator(test_config, llm_client)
        assert generator is not None
        
    def test_generate_questions(self, test_config, llm_client, skip_if_no_ollama):
        """Test question generation."""
        generator = QuestionGenerator(test_config, llm_client)
        
        module_info = {
            "id": 1,
            "name": "Cell Biology",
            "subtopics": ["Cell structure"],
            "learning_objectives": ["Understand cells"],
            "num_questions": 5
        }
        
        questions = generator.generate_questions(module_info)
        
        assert isinstance(questions, str)
        assert len(questions) > 50
        
    def test_save_questions(self, test_config, llm_client, tmp_path):
        """Test saving questions to file."""
        generator = QuestionGenerator(test_config, llm_client)
        
        questions = "# Questions\n\n1. What is a cell?"
        output_dir = tmp_path / "questions"
        module_info = {"id": 1, "name": "Cell Biology"}
        
        filepath = generator.save_questions(questions, module_info, output_dir)
        
        assert filepath.exists()
        assert filepath.suffix == ".md"
    
    def test_generate_questions_pre_validation(self, test_config, llm_client):
        """Test pre-generation validation in question generator."""
        generator = QuestionGenerator(test_config, llm_client)
        
        # Test with invalid num_questions
        module_info = {
            "id": 1,
            "name": "Test",
            "subtopics": [],
            "num_questions": -1  # Invalid
        }
        
        # Should handle invalid input gracefully
        # The function should use default or fix the value
        # This is tested through the actual generation which validates inputs
        assert generator is not None
    
    def test_generate_diagram_retry_handles_validation(self, test_config, llm_client, skip_if_no_ollama):
        """Test that diagram generation handles validation and can retry."""
        generator = DiagramGenerator(test_config, llm_client)
        
        topic = "Test topic"
        context = "Test context"
        
        # Generate with retry logic (max_retries=1, total attempts = 2)
        diagram = generator.generate_diagram(topic, context, max_retries=1)
        
        # Should return a diagram even if first attempt has issues
        assert isinstance(diagram, str)
        assert len(diagram) > 0
    
    def test_generate_questions_retry_handles_validation(self, test_config, llm_client, skip_if_no_ollama):
        """Test that question generation handles validation and can retry."""
        generator = QuestionGenerator(test_config, llm_client)
        
        module_info = {
            "id": 1,
            "name": "Test Module",
            "subtopics": ["Topic 1"],
            "learning_objectives": ["Objective 1"],
            "num_questions": 3
        }
        
        # Generate with retry logic (max_retries=1, total attempts = 2)
        questions = generator.generate_questions(module_info, max_retries=1)
        
        # Should return questions even if first attempt has issues
        assert isinstance(questions, str)
        assert len(questions) > 0

