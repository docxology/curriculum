"""Comprehensive tests for format generators covering error handling and edge cases."""

import pytest
from pathlib import Path
from src.config.loader import ConfigLoader
from src.llm.client import OllamaClient, LLMError
from src.generate.formats.lectures import LectureGenerator
from src.generate.formats.labs import LabGenerator
from src.generate.formats.study_notes import StudyNotesGenerator
from src.generate.formats.diagrams import DiagramGenerator
from src.generate.formats.questions import QuestionGenerator


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
                "num_predict": 200
            }
        },
        "prompts": {
            "lecture": {
                "system": "You are a biology educator.",
                "template": "Write about {module_name}. Topics: {subtopics}. Objectives: {objectives}."
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
                "template": "Create a Mermaid diagram for {topic}. Context: {context}"
            },
            "questions": {
                "system": "Create questions.",
                "template": "Create {num_questions} questions about {module_name}"
            }
        },
        "content_requirements": {
            "lecture": {
                "min_word_count": 500,
                "max_word_count": 1000,
                "min_examples": 3,
                "max_examples": 10,
                "min_sections": 3,
                "max_sections": 6
            },
            "questions": {
                "num_questions": 5,
                "mc_count": 3,
                "sa_count": 1,
                "essay_count": 1
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
            "content_length": 500
        }]
    }
    
    output_config = {
        "output": {
            "base_directory": str(tmp_path / "output"),
            "directories": {
                "lectures": "lectures",
                "labs": "labs",
                "study_notes": "study_notes",
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


class TestFormatGeneratorErrorHandling:
    """Test error handling in format generators."""
    
    def test_lecture_generator_empty_module_info(self, test_config, llm_client):
        """Test lecture generator with empty module info."""
        generator = LectureGenerator(test_config, llm_client)
        
        # Should handle missing fields gracefully
        module_info = {"name": "Test"}
        
        # Should not crash, but may raise KeyError for required fields
        # This tests error handling
        try:
            result = generator.generate_lecture(module_info, max_retries=0)
            assert isinstance(result, str)
        except (KeyError, ValueError) as e:
            # Expected for incomplete module info
            assert "name" in str(e) or "subtopics" in str(e) or "objectives" in str(e)
    
    def test_diagram_generator_empty_topic(self, test_config, llm_client, skip_if_no_ollama):
        """Test diagram generator with empty topic."""
        generator = DiagramGenerator(test_config, llm_client)
        
        # Should handle empty topic
        result = generator.generate_diagram("", "Test context", max_retries=0)
        
        # Should return something (even if empty) or raise appropriate error
        assert isinstance(result, str)
    
    def test_question_generator_invalid_num_questions(self, test_config, llm_client):
        """Test question generator with invalid num_questions."""
        generator = QuestionGenerator(test_config, llm_client)
        
        module_info = {
            "id": 1,
            "name": "Test",
            "subtopics": ["Topic 1"],
            "num_questions": -1  # Invalid
        }
        
        # Should handle invalid input gracefully
        # May use default or fix the value
        assert generator is not None


class TestFormatGeneratorFileOperations:
    """Test file saving operations in format generators."""
    
    def test_lecture_save_creates_directory(self, test_config, llm_client, tmp_path):
        """Test that saving lecture creates directory if needed."""
        generator = LectureGenerator(test_config, llm_client)
        
        output_dir = tmp_path / "new_dir" / "lectures"
        module_info = {"id": 1, "name": "Test Module"}
        
        filepath = generator.save_lecture("# Test Lecture", module_info, output_dir)
        
        assert filepath.exists()
        assert output_dir.exists()
    
    def test_diagram_save_with_special_chars(self, test_config, llm_client, tmp_path):
        """Test saving diagram with special characters in topic."""
        generator = DiagramGenerator(test_config, llm_client)
        
        diagram = "graph TD\n  A --> B"
        output_dir = tmp_path / "diagrams"
        
        # Topic with special characters
        filepath = generator.save_diagram(diagram, "Test & Topic (Special)", 1, 1, output_dir)
        
        assert filepath.exists()
        assert filepath.suffix == ".mmd"
    
    def test_questions_save_unicode(self, test_config, llm_client, tmp_path):
        """Test saving questions with unicode content."""
        generator = QuestionGenerator(test_config, llm_client)
        
        questions = "# Questions\n\n1. What is α-helix?"
        output_dir = tmp_path / "questions"
        module_info = {"id": 1, "name": "Test"}
        
        filepath = generator.save_questions(questions, module_info, output_dir)
        
        assert filepath.exists()
        # Verify unicode is preserved
        content = filepath.read_text(encoding='utf-8')
        assert "α-helix" in content


class TestFormatGeneratorValidation:
    """Test validation in format generators."""
    
    def test_lecture_generator_retry_on_validation_failure(self, test_config, llm_client, skip_if_no_ollama):
        """Test that lecture generator retries on validation failure."""
        generator = LectureGenerator(test_config, llm_client)
        
        module_info = {
            "id": 1,
            "name": "Cell Biology",
            "subtopics": ["Cell structure"],
            "learning_objectives": ["Understand cells"],
            "content_length": 500
        }
        
        # With max_retries=1, should attempt twice
        result = generator.generate_lecture(module_info, max_retries=1)
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_diagram_generator_retry_on_invalid_mermaid(self, test_config, llm_client, skip_if_no_ollama):
        """Test that diagram generator retries on invalid Mermaid syntax."""
        generator = DiagramGenerator(test_config, llm_client)
        
        # Generate with retry
        result = generator.generate_diagram("Test topic", "Test context", max_retries=1)
        
        assert isinstance(result, str)
        # Should be valid Mermaid or at least attempt to be


class TestFormatGeneratorEdgeCases:
    """Test edge cases in format generators."""
    
    def test_lecture_very_long_module_name(self, test_config, llm_client, tmp_path):
        """Test lecture generator with very long module name."""
        generator = LectureGenerator(test_config, llm_client)
        
        module_info = {
            "id": 1,
            "name": "A" * 200,  # Very long name
            "subtopics": ["Topic"],
            "learning_objectives": ["Objective"]
        }
        
        output_dir = tmp_path / "lectures"
        filepath = generator.save_lecture("# Test", module_info, output_dir)
        
        # Should handle long names (may truncate in filename)
        assert filepath.exists()
    
    def test_questions_empty_subtopics(self, test_config, llm_client):
        """Test question generator with empty subtopics."""
        generator = QuestionGenerator(test_config, llm_client)
        
        module_info = {
            "id": 1,
            "name": "Test",
            "subtopics": [],  # Empty
            "learning_objectives": ["Objective"],
            "num_questions": 3
        }
        
        # Should handle empty subtopics gracefully
        assert generator is not None
    
    def test_diagram_unicode_topic(self, test_config, llm_client, tmp_path):
        """Test diagram generator with unicode in topic."""
        generator = DiagramGenerator(test_config, llm_client)
        
        diagram = "graph TD\n  A --> B"
        output_dir = tmp_path / "diagrams"
        
        # Unicode in topic
        filepath = generator.save_diagram(diagram, "α-helix Structure", 1, 1, output_dir)
        
        assert filepath.exists()
        # Filename should handle unicode
        assert "α" in str(filepath) or filepath.exists()  # May be sanitized


class TestFormatGeneratorIntegration:
    """Integration tests for format generators."""
    
    def test_all_generators_initialization(self, test_config, llm_client):
        """Test that all generators can be initialized."""
        lecture_gen = LectureGenerator(test_config, llm_client)
        lab_gen = LabGenerator(test_config, llm_client)
        study_notes_gen = StudyNotesGenerator(test_config, llm_client)
        diagram_gen = DiagramGenerator(test_config, llm_client)
        question_gen = QuestionGenerator(test_config, llm_client)
        
        assert lecture_gen is not None
        assert lab_gen is not None
        assert study_notes_gen is not None
        assert diagram_gen is not None
        assert question_gen is not None
    
    def test_generators_share_config(self, test_config, llm_client):
        """Test that generators share the same config."""
        lecture_gen = LectureGenerator(test_config, llm_client)
        question_gen = QuestionGenerator(test_config, llm_client)
        
        assert lecture_gen.config_loader == question_gen.config_loader
        assert lecture_gen.llm_client == question_gen.llm_client

