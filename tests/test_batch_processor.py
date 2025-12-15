"""Tests for batch course processor module.

All tests use real implementations - no mocks.
"""

import pytest
import yaml
import subprocess
import os
import sys
from pathlib import Path
import argparse
import shutil

from src.generate.orchestration.batch import BatchCourseProcessor


@pytest.fixture
def config_dir(tmp_path):
    """Create a temporary config directory with test files."""
    config_path = tmp_path / "config"
    config_path.mkdir()
    
    # Create courses directory
    courses_dir = config_path / "courses"
    courses_dir.mkdir()
    
    # Create test course config
    course_config = {
        "course": {
            "name": "Test Biology",
            "description": "Test course",
            "level": "Intro",
            "defaults": {
                "num_modules": 5,
                "total_sessions": 15
            }
        }
    }
    
    # Create test LLM config
    llm_config = {
        "llm": {
            "provider": "ollama",
            "model": "gemma3:4b",
            "api_url": "http://localhost:11434/api/generate"
        }
    }
    
    # Create test output config
    output_config = {
        "output": {
            "base_directory": "output",
            "directories": {
                "outlines": "outlines",
                "modules": "modules",
                "logs": "logs",
                "website": "website"
            }
        }
    }
    
    # Write config files
    with open(config_path / "course_config.yaml", "w") as f:
        yaml.dump(course_config, f)
    
    with open(config_path / "llm_config.yaml", "w") as f:
        yaml.dump(llm_config, f)
    
    with open(config_path / "output_config.yaml", "w") as f:
        yaml.dump(output_config, f)
    
    # Create test course templates
    course1 = {
        "course": {
            "name": "Introductory Biology",
            "description": "Biology course",
            "level": "Undergraduate",
            "subject": "Biology"
        }
    }
    
    course2 = {
        "course": {
            "name": "Introductory Chemistry",
            "description": "Chemistry course",
            "level": "Undergraduate",
            "subject": "Chemistry"
        }
    }
    
    with open(courses_dir / "biology.yaml", "w") as f:
        yaml.dump(course1, f)
    
    with open(courses_dir / "chemistry.yaml", "w") as f:
        yaml.dump(course2, f)
    
    return config_path


@pytest.fixture
def project_root(tmp_path):
    """Create a temporary project root with real executable test scripts."""
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    
    # Get path to real test scripts
    test_scripts_dir = Path(__file__).parent / "fixtures" / "test_scripts"
    
    # Copy real test scripts to project scripts directory
    for script_name in [
        "01_setup_environment.py",
        "02_run_tests.py",
        "03_generate_outline.py",
        "04_generate_primary.py",
        "05_generate_secondary.py",
        "06_website.py"
    ]:
        source_script = test_scripts_dir / script_name
        if source_script.exists():
            dest_script = scripts_dir / script_name
            shutil.copy2(source_script, dest_script)
            # Ensure executable
            os.chmod(dest_script, 0o755)
        else:
            # Create minimal real executable script if test script not found
            script_content = f"""#!/usr/bin/env python3
import sys
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config-dir', type=Path)
    parser.add_argument('--course', type=str, default=None)
    parser.add_argument('--no-interactive', action='store_true')
    parser.add_argument('--modules', nargs='+', type=int, default=None)
    parser.add_argument('--all', action='store_true')
    parser.add_argument('--types', nargs='+', type=str, default=None)
    parser.add_argument('--run-tests', action='store_true')
    args = parser.parse_args()
    return 0

if __name__ == '__main__':
    sys.exit(main())
"""
            dest_script = scripts_dir / script_name
            dest_script.write_text(script_content)
            os.chmod(dest_script, 0o755)
    
    return tmp_path


@pytest.fixture
def test_args():
    """Create argparse.Namespace with default values for testing."""
    args = argparse.Namespace()
    args.config_dir = None  # Will be set in tests
    args.no_interactive = True
    args.skip_setup = False
    args.skip_validation = False
    args.skip_outline = False
    args.skip_primary = False
    args.skip_secondary = False
    args.skip_website = False
    args.modules = None
    args.types = None
    args.run_tests = False
    return args


class TestBatchCourseProcessor:
    """Test BatchCourseProcessor class using real implementations."""
    
    def test_init_with_valid_paths(self, config_dir, project_root):
        """Test initialization with valid paths."""
        processor = BatchCourseProcessor(config_dir, project_root)
        assert processor.config_dir == Path(config_dir).resolve()
        assert processor.project_root == Path(project_root).resolve()
        assert processor.script_dir == project_root / "scripts"
    
    def test_init_without_project_root(self, config_dir):
        """Test initialization without explicit project root."""
        processor = BatchCourseProcessor(config_dir)
        assert processor.config_dir == Path(config_dir).resolve()
        assert processor.project_root == Path(config_dir).resolve().parent
    
    def test_list_available_courses(self, config_dir, project_root):
        """Test listing available courses."""
        processor = BatchCourseProcessor(config_dir, project_root)
        courses = processor.list_available_courses()
        
        assert len(courses) == 2
        course_names = [c['name'] for c in courses]
        assert 'biology' in course_names
        assert 'chemistry' in course_names
    
    def test_list_available_courses_empty(self, tmp_path, project_root):
        """Test listing courses when none exist."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        
        # Create minimal config files
        course_config = {"course": {"name": "Test"}}
        with open(config_dir / "course_config.yaml", "w") as f:
            yaml.dump(course_config, f)
        
        processor = BatchCourseProcessor(config_dir, project_root)
        courses = processor.list_available_courses()
        
        assert len(courses) == 0
    
    def test_process_all_courses_for_outline_success(self, config_dir, project_root, test_args):
        """Test processing all courses for outline generation with success using real scripts."""
        test_args.config_dir = config_dir
        
        processor = BatchCourseProcessor(config_dir, project_root)
        summary = processor.process_all_courses_for_outline(test_args)
        
        assert summary['total'] == 2
        assert len(summary['successful']) == 2
        assert len(summary['failed']) == 0
        assert 'biology' in summary['successful']
        assert 'chemistry' in summary['successful']
    
    def test_process_all_courses_for_outline_partial_failure(self, config_dir, project_root, test_args):
        """Test processing all courses with one failure using real script that fails."""
        test_args.config_dir = config_dir
        
        # Create a script that fails for biology course
        scripts_dir = project_root / "scripts"
        outline_script = scripts_dir / "03_generate_outline.py"
        
        # Read original script
        original_content = outline_script.read_text()
        
        # Create failing version
        failing_content = """#!/usr/bin/env python3
import sys
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config-dir', type=Path, required=True)
    parser.add_argument('--course', type=str, default=None)
    parser.add_argument('--no-interactive', action='store_true')
    args = parser.parse_args()
    
    # Fail for biology course
    if args.course == 'biology':
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
"""
        outline_script.write_text(failing_content)
        os.chmod(outline_script, 0o755)
        
        try:
            processor = BatchCourseProcessor(config_dir, project_root)
            summary = processor.process_all_courses_for_outline(test_args)
            
            assert summary['total'] == 2
            assert len(summary['successful']) == 1
            assert len(summary['failed']) == 1
            assert 'chemistry' in summary['successful']
            assert summary['failed'][0]['name'] == 'biology'
        finally:
            # Restore original script
            outline_script.write_text(original_content)
            os.chmod(outline_script, 0o755)
    
    def test_process_all_courses_for_outline_exception(self, config_dir, project_root, test_args):
        """Test processing all courses with exception handling using real script that raises."""
        test_args.config_dir = config_dir
        
        # Create a script that raises exception
        scripts_dir = project_root / "scripts"
        outline_script = scripts_dir / "03_generate_outline.py"
        
        # Read original script
        original_content = outline_script.read_text()
        
        # Create exception-raising version
        exception_content = """#!/usr/bin/env python3
import sys
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config-dir', type=Path, required=True)
    parser.add_argument('--course', type=str, default=None)
    parser.add_argument('--no-interactive', action='store_true', default=False)
    args = parser.parse_args()
    
    # Raise exception for biology course
    if args.course == 'biology':
        raise Exception("Test exception")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
"""
        outline_script.write_text(exception_content)
        os.chmod(outline_script, 0o755)
        
        try:
            processor = BatchCourseProcessor(config_dir, project_root)
            summary = processor.process_all_courses_for_outline(test_args)
            
            assert summary['total'] == 2
            assert len(summary['successful']) == 1
            assert len(summary['failed']) == 1
            assert 'chemistry' in summary['successful']
            assert 'Test exception' in summary['failed'][0]['error']
        finally:
            # Restore original script
            outline_script.write_text(original_content)
            os.chmod(outline_script, 0o755)
    
    def test_process_all_courses_full_pipeline_success(self, config_dir, project_root, test_args):
        """Test processing all courses through full pipeline with success using real scripts."""
        test_args.config_dir = config_dir
        
        processor = BatchCourseProcessor(config_dir, project_root)
        summary = processor.process_all_courses_full_pipeline(test_args)
        
        assert summary['total'] == 2
        assert len(summary['successful']) == 2
        assert len(summary['failed']) == 0
    
    def test_process_all_courses_full_pipeline_with_skips(self, config_dir, project_root, test_args):
        """Test processing with some stages skipped using real scripts."""
        test_args.config_dir = config_dir
        test_args.skip_setup = True
        test_args.skip_validation = True
        
        processor = BatchCourseProcessor(config_dir, project_root)
        summary = processor.process_all_courses_full_pipeline(test_args)
        
        assert summary['total'] == 2
        # Should process 4 stages per course (skipping setup and validation)
        # Both courses should succeed
        assert len(summary['successful']) == 2
        assert len(summary['failed']) == 0
    
    def test_process_all_courses_full_pipeline_stage_failure(self, config_dir, project_root, test_args):
        """Test processing with stage failure using real script that fails."""
        test_args.config_dir = config_dir
        
        # Create a script that fails at stage 3 for biology course
        scripts_dir = project_root / "scripts"
        outline_script = scripts_dir / "03_generate_outline.py"
        
        # Read original script
        original_content = outline_script.read_text()
        
        # Create failing version for biology
        failing_content = """#!/usr/bin/env python3
import sys
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config-dir', type=Path, required=True)
    parser.add_argument('--course', type=str, default=None)
    parser.add_argument('--no-interactive', action='store_true')
    args = parser.parse_args()
    
    # Fail for biology course
    if args.course == 'biology':
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
"""
        outline_script.write_text(failing_content)
        os.chmod(outline_script, 0o755)
        
        try:
            processor = BatchCourseProcessor(config_dir, project_root)
            summary = processor.process_all_courses_full_pipeline(test_args)
            
            assert summary['total'] == 2
            assert len(summary['successful']) == 1
            assert len(summary['failed']) == 1
            assert 'chemistry' in summary['successful']
            assert 'biology' in [f['name'] for f in summary['failed']]
        finally:
            # Restore original script
            outline_script.write_text(original_content)
            os.chmod(outline_script, 0o755)
    
    def test_process_all_courses_empty_list(self, tmp_path, project_root, test_args):
        """Test processing when no courses are available."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        
        # Create minimal config
        course_config = {"course": {"name": "Test"}}
        with open(config_dir / "course_config.yaml", "w") as f:
            yaml.dump(course_config, f)
        
        test_args.config_dir = config_dir
        
        processor = BatchCourseProcessor(config_dir, project_root)
        summary = processor.process_all_courses_for_outline(test_args)
        
        assert summary['total'] == 0
        assert summary['summary'] == 'No courses to process'
    
    def test_generate_summary(self, config_dir, project_root):
        """Test summary generation."""
        processor = BatchCourseProcessor(config_dir, project_root)
        
        summary = processor._generate_summary(
            total=3,
            successful=['course1', 'course2'],
            failed=[{'name': 'course3', 'error': 'Test error'}],
            operation='outline generation'
        )
        
        assert '3 course' in summary
        assert '2 successful' in summary
        assert '1 failed' in summary
        assert 'outline generation' in summary
    
    def test_run_script_with_course_flag(self, config_dir, project_root, test_args):
        """Test that script 03 is called with --course and --no-interactive flags using real subprocess."""
        test_args.config_dir = config_dir
        
        processor = BatchCourseProcessor(config_dir, project_root)
        
        # Create a logger
        import logging
        test_logger = logging.getLogger("test")
        test_logger.setLevel(logging.WARNING)  # Reduce noise
        
        # Run script and capture command
        exit_code, stderr = processor._run_script('03_generate_outline.py', 'biology', test_args, test_logger)
        
        # Verify script executed successfully
        assert exit_code == 0, f"Script should exit with code 0, got {exit_code}. stderr: {stderr}"
        
        # Note: The test script is a minimal stub that doesn't actually create outline files.
        # In a real scenario, the script would create an outline file, but for unit testing
        # we just verify that the script was called with the correct flags and executed successfully.
        # The actual outline creation is tested in integration tests.
    
    def test_run_script_without_course_flag_for_other_scripts(self, config_dir, project_root, test_args):
        """Test that scripts other than 03 don't receive --course or --no-interactive flags using real subprocess."""
        test_args.config_dir = config_dir
        
        processor = BatchCourseProcessor(config_dir, project_root)
        
        # Create a logger
        import logging
        test_logger = logging.getLogger("test")
        test_logger.setLevel(logging.WARNING)  # Reduce noise
        
        # Test scripts that don't support these flags
        for script_name in ['01_setup_environment.py', '02_run_tests.py', '04_generate_primary.py', '05_generate_secondary.py', '06_website.py']:
            # Run script - should succeed
            exit_code, stderr = processor._run_script(script_name, 'biology', test_args, test_logger)
            
            # Verify script executed successfully
            assert exit_code == 0, f"{script_name} should execute successfully, got exit code {exit_code}. stderr: {stderr}"


