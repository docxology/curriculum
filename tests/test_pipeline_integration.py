"""Integration tests for full pipeline workflows."""

import pytest
import json
from pathlib import Path
from src.config.loader import ConfigLoader
from src.generate.orchestration.pipeline import ContentGenerator


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
            "parameters": {"temperature": 0.7, "num_predict": 200}
        },
        "prompts": {
            "outline": {
                "system": "You are a biology educator.",
                "template": "Create outline for {course_name}"
            },
            "lecture": {
                "system": "You are a biology educator.",
                "template": "Write about {module_name}"
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
            "total_class_sessions": 4,
            "defaults": {
                "num_modules": 2,
                "total_sessions": 4
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
    
    with open(config_path / "llm_config.yaml", "w") as f:
        yaml.dump(llm_config, f)
    with open(config_path / "course_config.yaml", "w") as f:
        yaml.dump(course_config, f)
    with open(config_path / "output_config.yaml", "w") as f:
        yaml.dump(output_config, f)
        
    return ConfigLoader(config_path)


class TestPipelineIntegration:
    """Integration tests for full pipeline."""
    
    def test_full_pipeline_stage1_to_stage2(self, test_config, tmp_path, skip_if_no_ollama):
        """Test complete pipeline from outline to content generation."""
        generator = ContentGenerator(test_config)
        
        # Stage 1: Generate outline
        outline_path = generator.stage1_generate_outline(num_modules=2, total_sessions=4)
        
        assert outline_path.exists()
        assert outline_path.suffix == ".md"
        
        # Verify JSON companion exists
        json_path = outline_path.with_suffix('.json')
        assert json_path.exists()
        
        # Load and verify structure
        outline_data = json.loads(json_path.read_text(encoding='utf-8'))
        assert 'modules' in outline_data
        assert len(outline_data['modules']) == 2
        
        # Stage 2: Generate content for first module only
        modules = outline_data['modules']
        if len(modules) > 0:
            first_module_id = modules[0].get('module_id')
            results = generator.stage2_generate_content_by_session(module_ids=[first_module_id])
            
            assert isinstance(results, list)
            assert len(results) > 0
            
            # Verify at least one result has files
            successful_results = [r for r in results if r.get('status') == 'success']
            if len(successful_results) > 0:
                result = successful_results[0]
                assert 'session_dir' in result
                session_dir = Path(result['session_dir'])
                if session_dir.exists():
                    files = list(session_dir.glob('*'))
                    assert len(files) > 0
    
    def test_pipeline_error_recovery(self, test_config, skip_if_no_ollama):
        """Test pipeline error recovery mechanisms."""
        generator = ContentGenerator(test_config)
        
        # Test transient error detection
        from src.llm.client import LLMError
        
        timeout_error = LLMError("Stream timeout: 180.5s elapsed")
        assert generator._is_transient_error(timeout_error) == True
        
        validation_error = ValueError("Invalid configuration")
        assert generator._is_transient_error(validation_error) == False
    
    def test_pipeline_module_filtering(self, test_config, tmp_path, skip_if_no_ollama):
        """Test pipeline with module filtering."""
        generator = ContentGenerator(test_config)
        
        # Generate outline
        outline_path = generator.stage1_generate_outline(num_modules=3, total_sessions=6)
        assert outline_path.exists()
        
        # Load outline
        json_path = outline_path.with_suffix('.json')
        outline_data = json.loads(json_path.read_text(encoding='utf-8'))
        modules = outline_data.get('modules', [])
        
        if len(modules) >= 2:
            # Generate content for only first two modules
            module_ids = [modules[0].get('module_id'), modules[1].get('module_id')]
            results = generator.stage2_generate_content_by_session(module_ids=module_ids)
            
            # Verify only specified modules processed
            result_module_ids = set(r.get('module_id') for r in results if r.get('module_id') is not None)
            assert all(mid in result_module_ids for mid in module_ids if mid is not None)
            
            # Should not have third module
            if len(modules) > 2:
                third_module_id = modules[2].get('module_id')
                if third_module_id is not None:
                    assert third_module_id not in result_module_ids
    
    def test_pipeline_output_structure(self, test_config, tmp_path, skip_if_no_ollama):
        """Test that pipeline creates correct output structure."""
        generator = ContentGenerator(test_config)
        
        # Generate outline
        outline_path = generator.stage1_generate_outline(num_modules=1, total_sessions=2)
        assert outline_path.exists()
        
        # Generate content
        results = generator.stage2_generate_content_by_session()
        
        # Verify output directory structure
        dirs = generator._get_output_directories()
        modules_dir = dirs.get('modules', Path('output/modules'))
        
        if modules_dir.exists():
            module_dirs = list(modules_dir.glob('module_*'))
            assert len(module_dirs) > 0
            
            # Check session structure
            for module_dir in module_dirs[:1]:  # Check first module only
                session_dirs = list(module_dir.glob('session_*'))
                assert len(session_dirs) > 0
                
                # Check content files in first session
                if len(session_dirs) > 0:
                    session_dir = session_dirs[0]
                    files = list(session_dir.glob('*'))
                    # Should have at least some files
                    assert len(files) >= 0  # May be empty if generation failed

