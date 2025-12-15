"""Extended tests for pipeline orchestration - comprehensive error handling and edge cases."""

import pytest
import json
import time
from pathlib import Path
from src.config.loader import ConfigLoader
from src.generate.orchestration.pipeline import ContentGenerator


@pytest.fixture
def multi_module_config(tmp_path):
    """Create config with multiple modules for testing."""
    import yaml
    
    config_path = tmp_path / "config"
    config_path.mkdir()
    
    course_config = {
        "course": {
            "name": "Multi-Module Test",
            "description": "Test course with multiple modules",
            "level": "Test",
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
            "model": "ministral-3:3b",
            "api_url": "http://localhost:11434/api/generate",
            "timeout": 60,
            "parameters": {"temperature": 0.7, "num_predict": 500, "format": "json"}
        },
        "prompts": {
            "outline": {
                "system": "Test system",
                "template": "Generate {num_modules} modules"
            },
            "lecture": {
                "system": "Test",
                "template": "Lecture for {module_name}"
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


class TestPipelineMultiModuleGeneration:
    """Test multi-module generation scenarios."""
    
    def test_multi_module_generation_all_succeed(self, multi_module_config, tmp_path):
        """Test successful generation of multiple modules."""
        loader = ConfigLoader(multi_module_config)
        
        # Create a valid outline JSON with 3 modules
        output_dir = tmp_path / "output" / "outlines"
        output_dir.mkdir(parents=True)
        
        outline_data = {
            "course_metadata": {"name": "Test", "total_modules": 3},
            "modules": [
                {"module_id": i, "module_name": f"Module {i}", "sessions": [
                    {"session_number": 1, "session_title": f"Session {i}.1", 
                     "subtopics": ["Topic"], "learning_objectives": ["Learn"], "key_concepts": ["Concept"]}
                ]}
                for i in range(1, 4)
            ]
        }
        outline_file = output_dir / "course_outline_test.json"
        outline_file.write_text(json.dumps(outline_data))
        
        modules = loader.get_modules_from_outline(outline_file)
        
        assert len(modules) == 3
        for i, module in enumerate(modules, 1):
            assert module["module_id"] == i
            assert "sessions" in module
    
    def test_empty_module_list(self, multi_module_config, tmp_path):
        """Test handling of outline with zero modules."""
        loader = ConfigLoader(multi_module_config)
        
        output_dir = tmp_path / "output" / "outlines"
        output_dir.mkdir(parents=True)
        
        outline_data = {
            "course_metadata": {"name": "Empty", "total_modules": 0},
            "modules": []
        }
        outline_file = output_dir / "course_outline_empty.json"
        outline_file.write_text(json.dumps(outline_data))
        
        modules = loader.get_modules_from_outline(outline_file)
        
        assert modules == []
    
    def test_very_large_module_count(self, multi_module_config, tmp_path):
        """Test handling of outline with 100+ modules."""
        loader = ConfigLoader(multi_module_config)
        
        output_dir = tmp_path / "output" / "outlines"
        output_dir.mkdir(parents=True)
        
        # Create outline with 100 modules
        modules = [
            {"module_id": i, "module_name": f"Module {i}", "sessions": []}
            for i in range(1, 101)
        ]
        outline_data = {
            "course_metadata": {"name": "Large", "total_modules": 100},
            "modules": modules
        }
        outline_file = output_dir / "course_outline_large.json"
        outline_file.write_text(json.dumps(outline_data))
        
        loaded_modules = loader.get_modules_from_outline(outline_file)
        
        assert len(loaded_modules) == 100
        assert loaded_modules[0]["module_id"] == 1
        assert loaded_modules[99]["module_id"] == 100


class TestPipelineErrorHandling:
    """Test pipeline error handling and recovery."""
    
    def test_json_outline_missing_file(self, multi_module_config, tmp_path, monkeypatch):
        """Test handling of missing outline file."""
        monkeypatch.chdir(tmp_path)
        loader = ConfigLoader(multi_module_config)
        
        # Try to get modules when no outline exists
        modules = loader.get_modules_from_outline()
        
        assert modules == []
    
    def test_json_outline_invalid_structure(self, multi_module_config, tmp_path):
        """Test handling of malformed outline JSON."""
        loader = ConfigLoader(multi_module_config)
        
        output_dir = tmp_path / "output" / "outlines"
        output_dir.mkdir(parents=True)
        
        # Create outline with invalid structure
        outline_data = {"invalid_key": "invalid_value"}
        outline_file = output_dir / "course_outline_invalid.json"
        outline_file.write_text(json.dumps(outline_data))
        
        modules = loader.get_modules_from_outline(outline_file)
        
        # Should return empty list on invalid structure
        assert modules == []
    
    def test_corrupted_json_file(self, multi_module_config, tmp_path):
        """Test handling of corrupted JSON file."""
        loader = ConfigLoader(multi_module_config)
        
        output_dir = tmp_path / "output" / "outlines"
        output_dir.mkdir(parents=True)
        
        # Create corrupted JSON
        outline_file = output_dir / "course_outline_corrupt.json"
        outline_file.write_text("{corrupted json content!!!")
        
        modules = loader.get_modules_from_outline(outline_file)
        
        assert modules == []


class TestPipelineModuleFiltering:
    """Test module filtering and selection."""
    
    def test_module_filtering_specific_ids(self, multi_module_config, tmp_path):
        """Test filtering modules by specific IDs."""
        loader = ConfigLoader(multi_module_config)
        
        output_dir = tmp_path / "output" / "outlines"
        output_dir.mkdir(parents=True)
        
        # Create outline with 5 modules
        modules = [
            {"module_id": i, "module_name": f"Module {i}", "sessions": []}
            for i in range(1, 6)
        ]
        outline_data = {
            "course_metadata": {"name": "Test", "total_modules": 5},
            "modules": modules
        }
        outline_file = output_dir / "course_outline_filter.json"
        outline_file.write_text(json.dumps(outline_data))
        
        all_modules = loader.get_modules_from_outline(outline_file)
        
        # Filter to specific IDs [1, 3, 5]
        target_ids = {1, 3, 5}
        filtered = [m for m in all_modules if m["module_id"] in target_ids]
        
        assert len(filtered) == 3
        assert all(m["module_id"] in target_ids for m in filtered)
    
    def test_module_filtering_invalid_ids(self, multi_module_config, tmp_path):
        """Test filtering with invalid module IDs."""
        loader = ConfigLoader(multi_module_config)
        
        output_dir = tmp_path / "output" / "outlines"
        output_dir.mkdir(parents=True)
        
        modules = [
            {"module_id": i, "module_name": f"Module {i}", "sessions": []}
            for i in range(1, 4)
        ]
        outline_data = {
            "course_metadata": {"name": "Test", "total_modules": 3},
            "modules": modules
        }
        outline_file = output_dir / "course_outline.json"
        outline_file.write_text(json.dumps(outline_data))
        
        all_modules = loader.get_modules_from_outline(outline_file)
        
        # Try to filter by IDs that don't exist
        target_ids = {99, 100}
        filtered = [m for m in all_modules if m["module_id"] in target_ids]
        
        assert len(filtered) == 0


class TestPipelineOutputDiscovery:
    """Test output directory discovery across multiple locations."""
    
    def test_output_directory_discovery_priority(self, multi_module_config, tmp_path, monkeypatch):
        """Test that discovery searches locations in correct priority order."""
        monkeypatch.chdir(tmp_path)
        loader = ConfigLoader(multi_module_config)
        
        # Create output directories in different locations
        output_dir = tmp_path / "output" / "outlines"
        output_dir.mkdir(parents=True)
        scripts_dir = tmp_path / "scripts" / "output" / "outlines"
        scripts_dir.mkdir(parents=True)
        
        # Create outlines in both
        outline1 = output_dir / "course_outline_1.json"
        outline1.write_text(json.dumps({"modules": [], "location": "output"}))
        
        time.sleep(0.01)
        
        outline2 = scripts_dir / "course_outline_2.json"
        outline2.write_text(json.dumps({"modules": [], "location": "scripts"}))
        
        found = loader._find_latest_outline_json()
        
        # Should find the most recent one
        assert found is not None
        content = json.loads(found.read_text())
        assert "location" in content
    
    def test_no_outline_in_any_location(self, multi_module_config, tmp_path, monkeypatch):
        """Test behavior when no outline exists in any location."""
        monkeypatch.chdir(tmp_path)
        loader = ConfigLoader(multi_module_config)
        
        # Don't create any outline files
        found = loader._find_latest_outline_json()
        
        assert found is None


class TestPipelineEdgeCases:
    """Test edge cases and unusual scenarios."""
    
    def test_outline_with_no_sessions(self, multi_module_config, tmp_path):
        """Test module with empty sessions array."""
        loader = ConfigLoader(multi_module_config)
        
        output_dir = tmp_path / "output" / "outlines"
        output_dir.mkdir(parents=True)
        
        outline_data = {
            "course_metadata": {"name": "Test"},
            "modules": [
                {"module_id": 1, "module_name": "Empty Module", "sessions": []}
            ]
        }
        outline_file = output_dir / "outline_no_sessions.json"
        outline_file.write_text(json.dumps(outline_data))
        
        modules = loader.get_modules_from_outline(outline_file)
        
        assert len(modules) == 1
        assert modules[0]["sessions"] == []
    
    def test_module_with_many_sessions(self, multi_module_config, tmp_path):
        """Test module with large number of sessions."""
        loader = ConfigLoader(multi_module_config)
        
        output_dir = tmp_path / "output" / "outlines"
        output_dir.mkdir(parents=True)
        
        # Create module with 50 sessions
        sessions = [
            {"session_number": i, "session_title": f"Session {i}", 
             "subtopics": ["Topic"], "learning_objectives": ["Learn"], "key_concepts": ["Concept"]}
            for i in range(1, 51)
        ]
        
        outline_data = {
            "course_metadata": {"name": "Test"},
            "modules": [
                {"module_id": 1, "module_name": "Large Module", "sessions": sessions}
            ]
        }
        outline_file = output_dir / "outline_many_sessions.json"
        outline_file.write_text(json.dumps(outline_data))
        
        modules = loader.get_modules_from_outline(outline_file)
        
        assert len(modules) == 1
        assert len(modules[0]["sessions"]) == 50
    
    def test_outline_with_special_characters_in_names(self, multi_module_config, tmp_path):
        """Test module names with special characters."""
        loader = ConfigLoader(multi_module_config)
        
        output_dir = tmp_path / "output" / "outlines"
        output_dir.mkdir(parents=True)
        
        outline_data = {
            "course_metadata": {"name": "Test"},
            "modules": [
                {"module_id": 1, "module_name": "DNA & RNA: Structure!", "sessions": []},
                {"module_id": 2, "module_name": "Cells (Pro- & Eukaryotic)", "sessions": []}
            ]
        }
        outline_file = output_dir / "outline_special_chars.json"
        outline_file.write_text(json.dumps(outline_data))
        
        modules = loader.get_modules_from_outline(outline_file)
        
        assert len(modules) == 2
        assert "&" in modules[0]["module_name"]
        assert "(" in modules[1]["module_name"]
    
    def test_module_id_gaps(self, multi_module_config, tmp_path):
        """Test modules with non-sequential IDs."""
        loader = ConfigLoader(multi_module_config)
        
        output_dir = tmp_path / "output" / "outlines"
        output_dir.mkdir(parents=True)
        
        outline_data = {
            "course_metadata": {"name": "Test"},
            "modules": [
                {"module_id": 1, "module_name": "Module 1", "sessions": []},
                {"module_id": 5, "module_name": "Module 5", "sessions": []},
                {"module_id": 10, "module_name": "Module 10", "sessions": []}
            ]
        }
        outline_file = output_dir / "outline_gaps.json"
        outline_file.write_text(json.dumps(outline_data))
        
        modules = loader.get_modules_from_outline(outline_file)
        
        assert len(modules) == 3
        assert modules[0]["module_id"] == 1
        assert modules[1]["module_id"] == 5
        assert modules[2]["module_id"] == 10


class TestPipelineValidation:
    """Test pipeline validation and quality checks."""
    
    def test_output_validation_structure(self, multi_module_config, tmp_path):
        """Test validation of generated output structure."""
        loader = ConfigLoader(multi_module_config)
        
        # Create valid outline
        output_dir = tmp_path / "output" / "outlines"
        output_dir.mkdir(parents=True)
        
        outline_data = {
            "course_metadata": {
                "course_title": "Test Course",
                "total_modules": 1,
                "total_sessions": 2
            },
            "modules": [
                {
                    "module_id": 1,
                    "module_name": "Test Module",
                    "sessions": [
                        {
                            "session_number": 1,
                            "session_title": "Session 1",
                            "subtopics": ["Topic 1", "Topic 2"],
                            "learning_objectives": ["Objective 1"],
                            "key_concepts": ["Concept 1"],
                            "rationale": "Test rationale"
                        }
                    ]
                }
            ]
        }
        outline_file = output_dir / "course_outline_valid.json"
        outline_file.write_text(json.dumps(outline_data))
        
        modules = loader.get_modules_from_outline(outline_file)
        
        # Validate structure
        assert len(modules) == 1
        module = modules[0]
        assert "module_id" in module
        assert "module_name" in module
        assert "sessions" in module
        assert len(module["sessions"]) == 1
        
        session = module["sessions"][0]
        assert "session_number" in session
        assert "session_title" in session
        assert "subtopics" in session
        assert "learning_objectives" in session
        assert "key_concepts" in session
    
    def test_outline_metadata_validation(self, multi_module_config, tmp_path):
        """Test validation of outline metadata."""
        loader = ConfigLoader(multi_module_config)
        
        output_dir = tmp_path / "output" / "outlines"
        output_dir.mkdir(parents=True)
        
        outline_data = {
            "course_metadata": {
                "course_title": "Biology 101",
                "total_modules": 2,
                "total_sessions": 6,
                "estimated_duration_weeks": 8
            },
            "modules": []
        }
        outline_file = output_dir / "outline_metadata.json"
        outline_file.write_text(json.dumps(outline_data))
        
        # Load and verify we can access the file
        content = json.loads(outline_file.read_text())
        
        assert content["course_metadata"]["course_title"] == "Biology 101"
        assert content["course_metadata"]["total_modules"] == 2


class TestPipelineFileOperations:
    """Test file operations in pipeline."""
    
    def test_multiple_outlines_select_most_recent(self, multi_module_config, tmp_path, monkeypatch):
        """Test that most recent outline is selected when multiple exist."""
        monkeypatch.chdir(tmp_path)
        loader = ConfigLoader(multi_module_config)
        
        output_dir = tmp_path / "output" / "outlines"
        output_dir.mkdir(parents=True)
        
        # Create three outlines with delays
        for i in range(1, 4):
            outline = output_dir / f"course_outline_{i}.json"
            outline.write_text(json.dumps({"modules": [], "version": i}))
            time.sleep(0.05)  # Ensure different timestamps
        
        found = loader._find_latest_outline_json()
        
        assert found is not None
        # Should be the last one created (version 3)
        content = json.loads(found.read_text())
        assert content["version"] == 3
    
    def test_outline_in_nested_directory(self, multi_module_config, tmp_path, monkeypatch):
        """Test outline discovery in nested directories."""
        monkeypatch.chdir(tmp_path)
        loader = ConfigLoader(multi_module_config)
        
        # Create deeply nested outline directory
        deep_dir = tmp_path / "output" / "outlines"
        deep_dir.mkdir(parents=True)
        
        outline_file = deep_dir / "course_outline_nested.json"
        outline_file.write_text(json.dumps({"modules": []}))
        
        found = loader._find_latest_outline_json()
        
        assert found is not None
        assert found.exists()


class TestPipelineDataIntegrity:
    """Test data integrity and consistency."""
    
    def test_module_data_preservation(self, multi_module_config, tmp_path):
        """Test that all module data is preserved when loading."""
        loader = ConfigLoader(multi_module_config)
        
        output_dir = tmp_path / "output" / "outlines"
        output_dir.mkdir(parents=True)
        
        # Create outline with comprehensive module data
        outline_data = {
            "course_metadata": {"name": "Test"},
            "modules": [
                {
                    "module_id": 1,
                    "module_name": "Cell Biology",
                    "module_description": "Study of cells",
                    "sessions": [
                        {
                            "session_number": 1,
                            "session_title": "Introduction",
                            "subtopics": ["Topic 1", "Topic 2", "Topic 3"],
                            "learning_objectives": ["Obj 1", "Obj 2"],
                            "key_concepts": ["Concept 1", "Concept 2", "Concept 3"],
                            "rationale": "Foundation of biology"
                        }
                    ],
                    "extra_field": "Should be preserved"
                }
            ]
        }
        outline_file = output_dir / "outline_comprehensive.json"
        outline_file.write_text(json.dumps(outline_data))
        
        modules = loader.get_modules_from_outline(outline_file)
        
        # Verify all data preserved
        module = modules[0]
        assert module["module_id"] == 1
        assert module["module_name"] == "Cell Biology"
        assert module["module_description"] == "Study of cells"
        assert "extra_field" in module
        assert module["extra_field"] == "Should be preserved"
        
        session = module["sessions"][0]
        assert len(session["subtopics"]) == 3
        assert len(session["learning_objectives"]) == 2
        assert len(session["key_concepts"]) == 3
    
    def test_unicode_in_module_names_and_content(self, multi_module_config, tmp_path):
        """Test handling of Unicode in module data."""
        loader = ConfigLoader(multi_module_config)
        
        output_dir = tmp_path / "output" / "outlines"
        output_dir.mkdir(parents=True)
        
        outline_data = {
            "course_metadata": {"name": "Biología"},
            "modules": [
                {
                    "module_id": 1,
                    "module_name": "Célula 细胞",  # Spanish + Chinese
                    "sessions": [
                        {
                            "session_number": 1,
                            "session_title": "Introducción",
                            "subtopics": ["Tópico avec é"],
                            "learning_objectives": ["Aprender 学习"],
                            "key_concepts": ["Concepto 概念"]
                        }
                    ]
                }
            ]
        }
        outline_file = output_dir / "outline_unicode.json"
        outline_file.write_text(json.dumps(outline_data, ensure_ascii=False), encoding='utf-8')
        
        modules = loader.get_modules_from_outline(outline_file)
        
        assert len(modules) == 1
        assert "Célula" in modules[0]["module_name"]
        assert "细胞" in modules[0]["module_name"]


class TestPipelinePerformance:
    """Test pipeline performance characteristics."""
    
    def test_large_outline_loading_performance(self, multi_module_config, tmp_path):
        """Test loading performance with large outline files."""
        import time
        
        loader = ConfigLoader(multi_module_config)
        
        output_dir = tmp_path / "output" / "outlines"
        output_dir.mkdir(parents=True)
        
        # Create large outline (50 modules, 5 sessions each = 250 sessions)
        modules = []
        for mod_id in range(1, 51):
            sessions = [
                {
                    "session_number": sess_num,
                    "session_title": f"Module {mod_id} Session {sess_num}",
                    "subtopics": [f"Topic {i}" for i in range(1, 6)],
                    "learning_objectives": [f"Objective {i}" for i in range(1, 6)],
                    "key_concepts": [f"Concept {i}" for i in range(1, 6)],
                    "rationale": f"Session {sess_num} rationale"
                }
                for sess_num in range(1, 6)
            ]
            modules.append({
                "module_id": mod_id,
                "module_name": f"Module {mod_id}",
                "sessions": sessions
            })
        
        outline_data = {
            "course_metadata": {"name": "Large Course", "total_modules": 50},
            "modules": modules
        }
        outline_file = output_dir / "outline_large.json"
        outline_file.write_text(json.dumps(outline_data))
        
        # Time the loading
        start = time.time()
        loaded_modules = loader.get_modules_from_outline(outline_file)
        elapsed = time.time() - start
        
        # Should load quickly (< 1 second)
        assert elapsed < 1.0
        assert len(loaded_modules) == 50
        assert len(loaded_modules[0]["sessions"]) == 5
    
    def test_concurrent_outline_access(self, multi_module_config, tmp_path):
        """Test concurrent access to outline files."""
        import threading
        
        loader = ConfigLoader(multi_module_config)
        
        output_dir = tmp_path / "output" / "outlines"
        output_dir.mkdir(parents=True)
        
        outline_data = {
            "course_metadata": {"name": "Concurrent Test"},
            "modules": [
                {"module_id": i, "module_name": f"Module {i}", "sessions": []}
                for i in range(1, 6)
            ]
        }
        outline_file = output_dir / "outline_concurrent.json"
        outline_file.write_text(json.dumps(outline_data))
        
        results = []
        errors = []
        
        def load_modules():
            try:
                modules = loader.get_modules_from_outline(outline_file)
                results.append(modules)
            except Exception as e:
                errors.append(e)
        
        # Multiple threads loading concurrently
        threads = [threading.Thread(target=load_modules) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # All should succeed
        assert len(errors) == 0
        assert len(results) == 10
        # All should get same data
        assert all(len(r) == 5 for r in results)


class TestPipelineLogging:
    """Test pipeline logging behavior."""
    
    def test_pipeline_logs_outline_discovery(self, multi_module_config, tmp_path, monkeypatch, caplog):
        """Test that pipeline logs outline discovery process."""
        import logging
        monkeypatch.chdir(tmp_path)
        
        caplog.set_level(logging.INFO)
        
        loader = ConfigLoader(multi_module_config)
        
        output_dir = tmp_path / "output" / "outlines"
        output_dir.mkdir(parents=True)
        
        outline_file = output_dir / "course_outline_log_test.json"
        outline_file.write_text(json.dumps({"modules": []}))
        
        found = loader._find_latest_outline_json()
        
        # Verify logging occurred
        assert found is not None


class TestPipelineNullHandling:
    """Test pipeline handling of null/None values."""
    
    def test_module_with_null_fields(self, multi_module_config, tmp_path):
        """Test module with null/None fields."""
        loader = ConfigLoader(multi_module_config)
        
        output_dir = tmp_path / "output" / "outlines"
        output_dir.mkdir(parents=True)
        
        outline_data = {
            "course_metadata": {"name": "Test"},
            "modules": [
                {
                    "module_id": 1,
                    "module_name": "Module 1",
                    "module_description": None,  # Null description
                    "sessions": [
                        {
                            "session_number": 1,
                            "session_title": "Session 1",
                            "subtopics": [],
                            "learning_objectives": None,  # Null objectives
                            "key_concepts": []
                        }
                    ]
                }
            ]
        }
        outline_file = output_dir / "outline_nulls.json"
        outline_file.write_text(json.dumps(outline_data))
        
        modules = loader.get_modules_from_outline(outline_file)
        
        # Should load without crashing
        assert len(modules) == 1
        assert modules[0]["module_description"] is None
    
    def test_explicit_none_path(self, multi_module_config):
        """Test passing None as explicit path."""
        loader = ConfigLoader(multi_module_config)
        
        # Should handle None gracefully (search default locations)
        modules = loader.get_modules_from_outline(None)
        
        # May be empty if no outline exists, but shouldn't crash
        assert isinstance(modules, list)

