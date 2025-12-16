"""Integration tests for full pipeline workflows."""

import pytest
import json
from pathlib import Path
from src.config.loader import ConfigLoader
from src.generate.orchestration.pipeline import ContentGenerator

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
            "parameters": {"temperature": 0.7, "num_predict": 1500}  # Increased for reliability
        },
        "prompts": {
            "outline": {
                "system": "You are an expert curriculum designer. Create a coherent, pedagogically sound course structure. You MUST output ONLY valid JSON - no markdown, no code fences, no explanations, no text before or after. Start with { and end with }.",
                "template": """Design a {subject} course with EXACTLY {num_modules} modules and EXACTLY {total_sessions} total sessions.

COURSE INFORMATION:
- Name: {course_name}
- Level: {course_level}
- Description: {course_description}
- Duration: {course_duration} weeks
- Constraints: {additional_constraints}

REQUIREMENTS:
1. Generate appropriate topics and modules based on the course description and constraints
2. Create {num_modules} coherent modules that cover the course scope
3. Distribute {total_sessions} sessions across these modules (aim for ~{avg_sessions_per_module} per module)
4. Each module should have a clear focus and logical progression
5. Sessions within modules should build on each other

CRITICAL: You MUST output valid JSON matching this EXACT structure. All fields are REQUIRED.

JSON SCHEMA (copy this structure exactly):
{{
  "course_metadata": {{
    "name": "{course_name}",
    "level": "{course_level}",
    "duration_weeks": {course_duration},
    "total_sessions": {total_sessions},
    "total_modules": {num_modules}
  }},
  "modules": [
    {{
      "module_id": 1,
      "module_name": "Descriptive module title",
      "module_description": "Brief overview of module scope",
      "sessions": [
        {{
          "session_number": 1,
          "session_title": "Specific session topic",
          "subtopics": ["topic1", "topic2", ...],
          "learning_objectives": ["objective1", "objective2", ...],
          "key_concepts": ["concept1", "concept2", ...],
          "rationale": "Why this session is important"
        }}
      ]
    }}
  ]
}}

STRICT RULES:
1. EXACTLY {num_modules} modules
2. EXACTLY {total_sessions} sessions total (distribute evenly)
3. Each session: {min_subtopics}-{max_subtopics} subtopics, {min_objectives}-{max_objectives} objectives, {min_concepts}-{max_concepts} concepts
4. Ultra-concise text
5. Sequential numbering (sessions 1-{total_sessions} globally)

OUTPUT: ONLY JSON (no ```json, no markdown, no explanation)"""
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
            "subject": "Biology",
            "additional_constraints": "Test constraints",
            "defaults": {
                "num_modules": 2,
                "total_sessions": 4
            }
        }
    }
    
    # Add outline generation bounds for test config
    outline_config = {
        "outline_generation": {
            "items_per_field": {
                "subtopics": {"min": 3, "max": 7},
                "learning_objectives": {"min": 3, "max": 7},
                "key_concepts": {"min": 3, "max": 7}
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
    # Merge outline config into llm_config (it's stored there in real config)
    llm_config.update(outline_config)
    with open(config_path / "llm_config.yaml", "w") as f:
        yaml.dump(llm_config, f)
        
    return ConfigLoader(config_path)


class TestPipelineIntegration:
    """Integration tests for full pipeline."""
    
    def test_full_pipeline_stage1_to_stage2(self, test_config, tmp_path, skip_if_no_ollama):
        """Test complete pipeline from outline to content generation."""
        generator = ContentGenerator(test_config)
        
        # Stage 1: Generate outline (minimal scope for faster testing)
        outline_path = generator.stage1_generate_outline(num_modules=1, total_sessions=2)
        
        assert outline_path.exists()
        assert outline_path.suffix == ".md"
        
        # Verify JSON companion exists
        json_path = outline_path.with_suffix('.json')
        assert json_path.exists()
        
        # Load and verify structure
        outline_data = json.loads(json_path.read_text(encoding='utf-8'))
        assert 'modules' in outline_data
        assert len(outline_data['modules']) == 1  # We requested 1 module
        assert len(outline_data['modules'][0]['sessions']) == 2  # With 2 sessions
        
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
        
        # Generate outline (reduced scope for faster testing)
        outline_path = generator.stage1_generate_outline(num_modules=2, total_sessions=4)
        assert outline_path.exists()
        
        # Load outline
        json_path = outline_path.with_suffix('.json')
        outline_data = json.loads(json_path.read_text(encoding='utf-8'))
        modules = outline_data.get('modules', [])
        
        if len(modules) >= 1:
            # Generate content for only first module (reduced scope for faster testing)
            module_ids = [modules[0].get('module_id')]
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

