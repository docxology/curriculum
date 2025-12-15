"""Tests for course selection edge cases.

Tests course template selection with various scenarios:
- 0 courses
- Many courses
- Keyboard interrupt handling
- Invalid input recovery
"""

import pytest
from unittest.mock import patch
import yaml
from pathlib import Path
from src.config.loader import ConfigLoader
from src.utils.course_selection import select_course_template, GENERATE_ALL_COURSES
import logging


class TestCourseSelectionEdgeCases:
    """Test course selection with edge cases."""
    
    def test_select_course_with_zero_courses(self, tmp_path):
        """Test selection when no course templates are available."""
        config_path = tmp_path / "config"
        config_path.mkdir()
        
        # Create basic config but no courses directory
        course_config = {"course": {"name": "Test"}}
        with open(config_path / "course_config.yaml", "w") as f:
            yaml.dump(course_config, f)
        
        loader = ConfigLoader(config_path)
        logger = logging.getLogger("test")
        
        result = select_course_template(loader, logger)
        # Should return None when no courses available
        assert result is None
    
    def test_select_course_with_many_courses(self, tmp_path):
        """Test selection with many course templates."""
        config_path = tmp_path / "config"
        config_path.mkdir()
        
        course_config = {"course": {"name": "Test"}}
        with open(config_path / "course_config.yaml", "w") as f:
            yaml.dump(course_config, f)
        
        courses_dir = config_path / "courses"
        courses_dir.mkdir()
        
        # Create 10 course templates
        for i in range(10):
            course_template = {
                "course": {
                    "name": f"Course {i}",
                    "description": f"Description for course {i}",
                    "level": "Intro",
                    "subject": "Biology"
                }
            }
            with open(courses_dir / f"course_{i}.yaml", "w") as f:
                yaml.dump(course_template, f)
        
        loader = ConfigLoader(config_path)
        logger = logging.getLogger("test")
        
        # Select first course
        with patch('builtins.input', return_value='1'):
            result = select_course_template(loader, logger)
            assert result == "course_0"
        
        # Select last course
        with patch('builtins.input', return_value='10'):
            result = select_course_template(loader, logger)
            assert result == "course_9"
        
        # Select generate all (option 12: 10 courses + default + generate all)
        with patch('builtins.input', return_value='12'):
            result = select_course_template(loader, logger)
            assert result == GENERATE_ALL_COURSES
    
    def test_select_course_keyboard_interrupt(self, tmp_path):
        """Test handling of keyboard interrupt during selection."""
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
        
        # Simulate keyboard interrupt
        with patch('builtins.input', side_effect=KeyboardInterrupt()):
            result = select_course_template(loader, logger)
            # Should return None on keyboard interrupt
            assert result is None
    
    def test_select_course_invalid_input_recovery(self, tmp_path):
        """Test recovery from invalid input."""
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
        
        # First input invalid, second valid
        with patch('builtins.input', side_effect=['invalid', 'abc', '1']):
            result = select_course_template(loader, logger)
            assert result == "biology"
    
    def test_select_course_empty_input_uses_default(self, tmp_path):
        """Test that empty input uses default course config."""
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
        
        # Empty input should use default
        with patch('builtins.input', return_value=''):
            result = select_course_template(loader, logger)
            assert result is None  # None means use default
    
    def test_select_course_out_of_range_input(self, tmp_path):
        """Test handling of out-of-range input."""
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
        
        # First input out of range, second valid
        with patch('builtins.input', side_effect=['100', '1']):
            result = select_course_template(loader, logger)
            assert result == "biology"
    
    def test_select_course_negative_input(self, tmp_path):
        """Test handling of negative input."""
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
        
        # First input negative, second valid
        with patch('builtins.input', side_effect=['-1', '1']):
            result = select_course_template(loader, logger)
            assert result == "biology"
    
    def test_select_course_default_option(self, tmp_path):
        """Test selecting the default option."""
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
        
        # With 1 course, option 2 is default
        with patch('builtins.input', return_value='2'):
            result = select_course_template(loader, logger)
            assert result is None  # None means use default
    
    def test_select_course_generate_all_option(self, tmp_path):
        """Test selecting generate all option."""
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
        
        # With 1 course, option 3 is generate all
        with patch('builtins.input', return_value='3'):
            result = select_course_template(loader, logger)
            assert result == GENERATE_ALL_COURSES

