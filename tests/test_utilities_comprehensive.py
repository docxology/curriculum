"""Comprehensive tests for utility modules with low coverage."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.utils.course_selection import select_course_template, GENERATE_ALL_COURSES
from src.utils.prompt_helpers import (
    get_constraint_summary,
    categorize_warnings,
    generate_retry_feedback,
    validate_constraint_consistency
)
from src.config.loader import ConfigLoader


class TestCourseSelection:
    """Tests for course_selection module."""
    
    def test_select_course_template_no_courses(self, tmp_path):
        """Test selection when no course templates exist."""
        import yaml
        from src.config.loader import ConfigLoader
        import logging
        
        # Create minimal config
        config_path = tmp_path / "config"
        config_path.mkdir()
        
        course_config = {"course": {"name": "Test"}}
        with open(config_path / "course_config.yaml", "w") as f:
            yaml.dump(course_config, f)
        
        # Create empty courses directory
        courses_dir = config_path / "courses"
        courses_dir.mkdir()
        
        loader = ConfigLoader(config_path)
        logger = logging.getLogger("test")
        
        result = select_course_template(loader, logger)
        
        assert result is None
    
    def test_select_course_template_with_courses(self, tmp_path):
        """Test selection with available courses."""
        import yaml
        from src.config.loader import ConfigLoader
        import logging
        
        # Create config with course templates
        config_path = tmp_path / "config"
        config_path.mkdir()
        
        course_config = {"course": {"name": "Test"}}
        with open(config_path / "course_config.yaml", "w") as f:
            yaml.dump(course_config, f)
        
        courses_dir = config_path / "courses"
        courses_dir.mkdir()
        
        # Create a course template
        course_template = {
            "course": {
                "name": "Test Biology",
                "subject": "Biology",
                "level": "Intro",
                "description": "Test course"
            }
        }
        with open(courses_dir / "biology.yaml", "w") as f:
            yaml.dump(course_template, f)
        
        loader = ConfigLoader(config_path)
        logger = logging.getLogger("test")
        
        # Mock input to select first course
        with patch('builtins.input', return_value='1'):
            result = select_course_template(loader, logger)
            assert result == "biology"
    
    def test_select_course_template_default(self, tmp_path):
        """Test selection of default option."""
        import yaml
        from src.config.loader import ConfigLoader
        import logging
        
        config_path = tmp_path / "config"
        config_path.mkdir()
        
        course_config = {"course": {"name": "Test"}}
        with open(config_path / "course_config.yaml", "w") as f:
            yaml.dump(course_config, f)
        
        courses_dir = config_path / "courses"
        courses_dir.mkdir()
        
        course_template = {"course": {"name": "Test Biology"}}
        with open(courses_dir / "biology.yaml", "w") as f:
            yaml.dump(course_template, f)
        
        loader = ConfigLoader(config_path)
        logger = logging.getLogger("test")
        
        # Mock input to select default (empty input)
        with patch('builtins.input', return_value=''):
            result = select_course_template(loader, logger)
            assert result is None
    
    def test_select_course_template_generate_all(self, tmp_path):
        """Test selection of generate all option."""
        import yaml
        from src.config.loader import ConfigLoader
        import logging
        
        config_path = tmp_path / "config"
        config_path.mkdir()
        
        course_config = {"course": {"name": "Test"}}
        with open(config_path / "course_config.yaml", "w") as f:
            yaml.dump(course_config, f)
        
        courses_dir = config_path / "courses"
        courses_dir.mkdir()
        
        course_template = {"course": {"name": "Test Biology"}}
        with open(courses_dir / "biology.yaml", "w") as f:
            yaml.dump(course_template, f)
        
        loader = ConfigLoader(config_path)
        logger = logging.getLogger("test")
        
        # With 1 course: option 1 = course, option 2 = default, option 3 = generate all
        # Mock input to select generate all (option 3)
        with patch('builtins.input', return_value='3'):
            result = select_course_template(loader, logger)
            assert result == GENERATE_ALL_COURSES
    
    def test_select_course_template_invalid_input(self, tmp_path):
        """Test handling of invalid input."""
        import yaml
        from src.config.loader import ConfigLoader
        import logging
        
        config_path = tmp_path / "config"
        config_path.mkdir()
        
        course_config = {"course": {"name": "Test"}}
        with open(config_path / "course_config.yaml", "w") as f:
            yaml.dump(course_config, f)
        
        courses_dir = config_path / "courses"
        courses_dir.mkdir()
        
        course_template = {"course": {"name": "Test Biology"}}
        with open(courses_dir / "biology.yaml", "w") as f:
            yaml.dump(course_template, f)
        
        loader = ConfigLoader(config_path)
        logger = logging.getLogger("test")
        
        # Mock input with invalid then valid input
        with patch('builtins.input', side_effect=['invalid', '1']):
            result = select_course_template(loader, logger)
            assert result == "biology"
    
    def test_select_course_template_keyboard_interrupt(self, tmp_path):
        """Test handling of keyboard interrupt."""
        import yaml
        from src.config.loader import ConfigLoader
        import logging
        
        config_path = tmp_path / "config"
        config_path.mkdir()
        
        course_config = {"course": {"name": "Test"}}
        with open(config_path / "course_config.yaml", "w") as f:
            yaml.dump(course_config, f)
        
        courses_dir = config_path / "courses"
        courses_dir.mkdir()
        
        course_template = {"course": {"name": "Test Biology"}}
        with open(courses_dir / "biology.yaml", "w") as f:
            yaml.dump(course_template, f)
        
        loader = ConfigLoader(config_path)
        logger = logging.getLogger("test")
        
        # Mock keyboard interrupt
        with patch('builtins.input', side_effect=KeyboardInterrupt()):
            result = select_course_template(loader, logger)
            assert result is None


class TestPromptHelpers:
    """Tests for prompt_helpers module."""
    
    def test_get_constraint_summary_lecture(self):
        """Test constraint summary for lectures."""
        requirements = {
            'min_word_count': 1000,
            'max_word_count': 1500,
            'min_examples': 5,
            'max_examples': 15,
            'min_sections': 4,
            'max_sections': 8
        }
        
        result = get_constraint_summary("lecture", requirements)
        
        assert "Word Count: 1000-1500 words" in result
        assert "Examples: 5-15" in result
        assert "Sections: 4-8" in result
    
    def test_get_constraint_summary_study_notes(self):
        """Test constraint summary for study notes."""
        requirements = {
            'min_key_concepts': 3,
            'max_key_concepts': 10,
            'max_word_count': 1200
        }
        
        result = get_constraint_summary("study_notes", requirements)
        
        assert "Key Concepts: 3-10" in result
        assert "Max Words: 1200" in result
    
    def test_get_constraint_summary_questions(self):
        """Test constraint summary for questions."""
        requirements = {
            'num_questions': 10,
            'mc_count': 5,
            'sa_count': 3,
            'essay_count': 2
        }
        
        result = get_constraint_summary("questions", requirements)
        
        assert "Total Questions: 10" in result
        assert "MC: 5" in result
        assert "SA: 3" in result
        assert "Essay: 2" in result
    
    def test_get_constraint_summary_generic(self):
        """Test constraint summary for generic content type."""
        requirements = {
            'count': 5,
            'length': 100
        }
        
        result = get_constraint_summary("unknown", requirements)
        
        assert "count: 5" in result
        assert "length: 100" in result
    
    def test_categorize_warnings(self):
        """Test warning categorization."""
        warnings = [
            "Missing question marks",
            "Format issue with headings",
            "Only 3 questions, need 5",
            "Word count below minimum"
        ]
        
        categorized = categorize_warnings(warnings)
        
        assert "Missing question marks" in categorized['critical']
        assert "Format issue with headings" in categorized['format']
        assert "Only 3 questions, need 5" in categorized['count']
        assert "Word count below minimum" in categorized['quality']
    
    def test_categorize_warnings_empty(self):
        """Test categorization with empty warnings."""
        categorized = categorize_warnings([])
        
        assert categorized['critical'] == []
        assert categorized['format'] == []
        assert categorized['count'] == []
        assert categorized['quality'] == []
    
    def test_generate_retry_feedback_no_warnings(self):
        """Test retry feedback with no warnings."""
        result = generate_retry_feedback([], "lecture")
        
        assert result == ""
    
    def test_generate_retry_feedback_questions(self):
        """Test retry feedback for questions."""
        warnings = [
            "Missing question marks in some questions",
            "MC questions need 4 options",
            "Only 3 questions generated, need 5"
        ]
        
        result = generate_retry_feedback(warnings, "questions")
        
        assert "VALIDATION FEEDBACK" in result
        assert "Missing question marks" in result
        assert "Question N:" in result
        assert "4 options" in result
    
    def test_generate_retry_feedback_study_notes(self):
        """Test retry feedback for study notes."""
        warnings = [
            "Key concepts missing",
            "Word count too high"
        ]
        
        result = generate_retry_feedback(warnings, "study_notes")
        
        assert "VALIDATION FEEDBACK" in result
        assert "Key concepts" in result
        assert "word count" in result
    
    def test_generate_retry_feedback_lecture(self):
        """Test retry feedback for lectures."""
        warnings = [
            "Word count below minimum",
            "Not enough examples",
            "Too few sections"
        ]
        
        result = generate_retry_feedback(warnings, "lecture")
        
        assert "VALIDATION FEEDBACK" in result
        assert "word count" in result
        assert "examples" in result
        assert "sections" in result
    
    def test_validate_constraint_consistency_valid(self):
        """Test constraint validation with valid constraints."""
        requirements = {
            'lecture': {
                'min_word_count': 1000,
                'max_word_count': 1500,
                'min_examples': 5,
                'max_examples': 15
            }
        }
        
        issues = validate_constraint_consistency(requirements)
        
        assert len(issues) == 0
    
    def test_validate_constraint_consistency_invalid_min_max(self):
        """Test constraint validation with invalid min > max."""
        requirements = {
            'lecture': {
                'min_word_count': 1500,
                'max_word_count': 1000  # Invalid: min > max
            }
        }
        
        issues = validate_constraint_consistency(requirements)
        
        assert len(issues) > 0
        assert "min_word_count" in issues[0]
        assert "max_word_count" in issues[0]
    
    def test_validate_constraint_consistency_multiple_issues(self):
        """Test constraint validation with multiple issues."""
        requirements = {
            'lecture': {
                'min_word_count': 1500,
                'max_word_count': 1000,
                'min_examples': 20,
                'max_examples': 10
            }
        }
        
        issues = validate_constraint_consistency(requirements)
        
        assert len(issues) == 2
    
    def test_validate_constraint_consistency_specific_types(self):
        """Test constraint validation for specific content types."""
        requirements = {
            'lecture': {
                'min_word_count': 1000,
                'max_word_count': 1500
            },
            'study_notes': {
                'min_key_concepts': 10,
                'max_key_concepts': 5  # Invalid
            }
        }
        
        issues = validate_constraint_consistency(requirements, content_types=['study_notes'])
        
        assert len(issues) == 1
        assert "study_notes" in issues[0]
        assert "min_key_concepts" in issues[0]

