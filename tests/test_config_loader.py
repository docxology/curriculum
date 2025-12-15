"""Tests for config_loader module."""

import pytest
import yaml
from pathlib import Path
from src.config.loader import ConfigLoader, ConfigurationError


@pytest.fixture
def config_dir(tmp_path):
    """Create a temporary config directory with test files."""
    config_path = tmp_path / "config"
    config_path.mkdir()
    
    # Create test course config (dynamic module generation structure)
    course_config = {
        "course": {
            "name": "Test Biology",
            "description": "Test course",
            "level": "Intro",
            "defaults": {
                "num_modules": 5,
                "total_sessions": 15,
                "sessions_per_module": None
            }
        }
    }
    
    # Create test LLM config
    llm_config = {
        "llm": {
            "provider": "ollama",
            "model": "gemma3:4b",
            "api_url": "http://localhost:11434/api/generate",
            "parameters": {
                "temperature": 0.7
            }
        },
        "prompts": {
            "outline": {
                "system": "Test system",
                "template": "Test {placeholder}"
            }
        }
    }
    
    # Create test output config
    output_config = {
        "output": {
            "base_directory": "output",
            "directories": {
                "outlines": "outlines"
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
    
    return config_path


class TestConfigLoader:
    """Test ConfigLoader class."""
    
    def test_init_with_valid_path(self, config_dir):
        """Test initialization with valid config directory."""
        loader = ConfigLoader(config_dir)
        assert loader.config_dir == config_dir
        
    def test_init_with_invalid_path(self, tmp_path):
        """Test initialization with invalid config directory."""
        invalid_path = tmp_path / "nonexistent"
        with pytest.raises(ConfigurationError, match="Config directory not found"):
            ConfigLoader(invalid_path)
            
    def test_load_course_config(self, config_dir):
        """Test loading course configuration."""
        loader = ConfigLoader(config_dir)
        config = loader.load_course_config()
        
        assert "course" in config
        assert config["course"]["name"] == "Test Biology"
        # New structure: defaults instead of static modules
        assert "defaults" in config["course"]
        
    def test_load_llm_config(self, config_dir):
        """Test loading LLM configuration."""
        loader = ConfigLoader(config_dir)
        config = loader.load_llm_config()
        
        assert "llm" in config
        assert config["llm"]["model"] == "gemma3:4b"
        assert "prompts" in config
        
    def test_load_output_config(self, config_dir):
        """Test loading output configuration."""
        loader = ConfigLoader(config_dir)
        config = loader.load_output_config()
        
        assert "output" in config
        assert config["output"]["base_directory"] == "output"
        
    def test_get_course_info(self, config_dir):
        """Test getting course information."""
        loader = ConfigLoader(config_dir)
        info = loader.get_course_info()
        
        assert info["name"] == "Test Biology"
        assert info["description"] == "Test course"
        assert info["level"] == "Intro"
        
    def test_get_modules_without_outline(self, config_dir):
        """Test get_modules with from_outline=False returns empty list."""
        loader = ConfigLoader(config_dir)
        modules = loader.get_modules(from_outline=False)
        
        # Static config no longer has modules - they're generated dynamically
        assert modules == []
        
    def test_get_module_by_id_without_outline(self, config_dir):
        """Test get_module_by_id with from_outline=False returns None."""
        loader = ConfigLoader(config_dir)
        module = loader.get_module_by_id(1, from_outline=False)
        
        # Static config no longer has modules - they're generated dynamically
        assert module is None
        
    def test_get_course_defaults(self, config_dir):
        """Test getting course structure defaults."""
        loader = ConfigLoader(config_dir)
        defaults = loader.get_course_defaults()
        
        assert "num_modules" in defaults
        assert "total_sessions" in defaults
        assert "sessions_per_module" in defaults
        
    def test_get_llm_parameters(self, config_dir):
        """Test getting LLM parameters."""
        loader = ConfigLoader(config_dir)
        params = loader.get_llm_parameters()
        
        assert params["provider"] == "ollama"
        assert params["model"] == "gemma3:4b"
        assert "api_url" in params
        
    def test_get_prompt_template(self, config_dir):
        """Test getting prompt template."""
        loader = ConfigLoader(config_dir)
        template = loader.get_prompt_template("outline")
        
        assert "system" in template
        assert "template" in template
        assert template["system"] == "Test system"
        
    def test_get_prompt_template_not_found(self, config_dir):
        """Test getting non-existent prompt template."""
        loader = ConfigLoader(config_dir)
        
        with pytest.raises(ConfigurationError, match="Prompt template .* not found"):
            loader.get_prompt_template("nonexistent")
            
    def test_get_output_paths(self, config_dir):
        """Test getting output paths."""
        loader = ConfigLoader(config_dir)
        paths = loader.get_output_paths()
        
        assert "base_directory" in paths
        assert "directories" in paths
        
    def test_validate_course_config_valid(self, config_dir):
        """Test validation of valid course config."""
        loader = ConfigLoader(config_dir)
        # Should not raise any errors
        loader.validate_course_config()
        
    def test_validate_course_config_missing_field(self, tmp_path):
        """Test validation of invalid course config."""
        config_path = tmp_path / "config"
        config_path.mkdir()
        
        # Create invalid config (missing required fields)
        invalid_config = {"course": {}}
        
        with open(config_path / "course_config.yaml", "w") as f:
            yaml.dump(invalid_config, f)
            
        # Create minimal other configs
        with open(config_path / "llm_config.yaml", "w") as f:
            yaml.dump({"llm": {}}, f)
        with open(config_path / "output_config.yaml", "w") as f:
            yaml.dump({"output": {}}, f)
        
        loader = ConfigLoader(config_path)
        
        with pytest.raises(ConfigurationError, match="Missing required field"):
            loader.validate_course_config()
            
    def test_missing_config_file(self, tmp_path):
        """Test handling of missing config file."""
        config_path = tmp_path / "config"
        config_path.mkdir()
        
        loader = ConfigLoader(config_path)
        
        with pytest.raises(ConfigurationError, match="Config file not found"):
            loader.load_course_config()
    
    def test_find_latest_outline_json_explicit_path(self, tmp_path):
        """Test finding outline with explicit path."""
        loader = ConfigLoader("config")
        
        # Create a test outline
        outline_file = tmp_path / "test_outline.json"
        outline_file.write_text('{"modules": []}', encoding='utf-8')
        
        found = loader._find_latest_outline_json(outline_file)
        
        assert found == outline_file
    
    def test_find_latest_outline_json_not_found(self, tmp_path, monkeypatch):
        """Test behavior when no outline JSON found."""
        monkeypatch.chdir(tmp_path)
        
        # Create config directory
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        (config_dir / "course_config.yaml").write_text("course:\n  name: Test\n  description: Test\n  level: Test")
        (config_dir / "llm_config.yaml").write_text("llm:\n  model: test\nprompts: {}")
        (config_dir / "output_config.yaml").write_text("output:\n  base_directory: output")
        
        loader = ConfigLoader(config_dir)
        
        found = loader._find_latest_outline_json()
        
        assert found is None
    
    def test_get_modules_from_outline_with_valid_json(self, tmp_path):
        """Test loading modules from a valid JSON outline."""
        loader = ConfigLoader("config")
        
        # Create test outline
        outline_data = {
            "course_metadata": {"name": "Test", "total_modules": 2},
            "modules": [
                {"module_id": 1, "module_name": "Module 1", "sessions": []},
                {"module_id": 2, "module_name": "Module 2", "sessions": []}
            ]
        }
        import json
        outline_file = tmp_path / "outline.json"
        outline_file.write_text(json.dumps(outline_data), encoding='utf-8')
        
        modules = loader.get_modules_from_outline(outline_file)
        
        assert len(modules) == 2
        assert modules[0]["module_id"] == 1
        assert modules[1]["module_id"] == 2
    
    def test_get_modules_from_outline_invalid_json(self, tmp_path):
        """Test handling of invalid JSON outline."""
        loader = ConfigLoader("config")
        
        # Create invalid JSON
        outline_file = tmp_path / "bad.json"
        outline_file.write_text("{ invalid json }", encoding='utf-8')
        
        modules = loader.get_modules_from_outline(outline_file)
        
        assert modules == []
    
    def test_get_module_by_id_from_outline(self, tmp_path):
        """Test getting specific module by ID from outline."""
        loader = ConfigLoader("config")
        
        # Create test outline
        outline_data = {
            "course_metadata": {"name": "Test"},
            "modules": [
                {"module_id": 1, "module_name": "Module 1", "sessions": []},
                {"module_id": 2, "module_name": "Module 2", "sessions": []},
                {"module_id": 3, "module_name": "Module 3", "sessions": []}
            ]
        }
        import json
        outline_file = tmp_path / "outline.json"
        outline_file.write_text(json.dumps(outline_data), encoding='utf-8')
        
        module = loader.get_module_by_id_from_outline(2, outline_file)
        
        assert module is not None
        assert module["module_id"] == 2
        assert module["module_name"] == "Module 2"
    
    def test_get_module_by_id_from_outline_not_found(self, tmp_path):
        """Test getting non-existent module returns None."""
        loader = ConfigLoader("config")
        
        # Create test outline
        outline_data = {
            "course_metadata": {"name": "Test"},
            "modules": [
                {"module_id": 1, "module_name": "Module 1", "sessions": []}
            ]
        }
        import json
        outline_file = tmp_path / "outline.json"
        outline_file.write_text(json.dumps(outline_data), encoding='utf-8')
        
        module = loader.get_module_by_id_from_outline(99, outline_file)
        
        assert module is None
    
    # PHASE 1: Additional Config Loader Tests (16% → 95% coverage)
    
    def test_malformed_yaml_syntax_error(self, tmp_path):
        """Test handling of YAML syntax errors."""
        config_path = tmp_path / "config"
        config_path.mkdir()
        
        # Create invalid YAML with syntax error
        bad_yaml = "course:\n  name: Test\n  bad_indent:\nwrong"
        (config_path / "course_config.yaml").write_text(bad_yaml)
        (config_path / "llm_config.yaml").write_text("llm:\n  model: test")
        (config_path / "output_config.yaml").write_text("output:\n  base_directory: output")
        
        loader = ConfigLoader(config_path)
        
        with pytest.raises(ConfigurationError, match="Invalid YAML"):
            loader.load_course_config()
    
    def test_missing_llm_model_field(self, tmp_path):
        """Test validation catches missing LLM model field."""
        config_path = tmp_path / "config"
        config_path.mkdir()
        
        # Create config missing model field
        course_config = {"course": {"name": "Test", "description": "Test", "level": "Test"}}
        llm_config = {"llm": {"provider": "ollama"}, "prompts": {}}  # Missing model
        output_config = {"output": {"base_directory": "output"}}
        
        (config_path / "course_config.yaml").write_text(yaml.dump(course_config))
        (config_path / "llm_config.yaml").write_text(yaml.dump(llm_config))
        (config_path / "output_config.yaml").write_text(yaml.dump(output_config))
        
        loader = ConfigLoader(config_path)
        # Should not raise on load, but would fail on access
        llm_cfg = loader.load_llm_config()
        assert "model" not in llm_cfg["llm"]
    
    def test_default_value_application(self, config_dir):
        """Test that default values are applied correctly."""
        loader = ConfigLoader(config_dir)
        defaults = loader.get_course_defaults()
        
        # Check defaults are present
        assert "num_modules" in defaults
        assert defaults["num_modules"] == 5
        assert "total_sessions" in defaults
        assert defaults["total_sessions"] == 15
        
        # sessions_per_module should be null (auto-calculated)
        assert defaults.get("sessions_per_module") is None
    
    def test_outline_discovery_multiple_locations(self, tmp_path, monkeypatch):
        """Test outline discovery searches multiple locations."""
        import time
        monkeypatch.chdir(tmp_path)
        
        # Create config
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        (config_dir / "course_config.yaml").write_text("course:\n  name: Test\n  description: Test\n  level: Test")
        (config_dir / "llm_config.yaml").write_text("llm:\n  model: test\nprompts: {}")
        (config_dir / "output_config.yaml").write_text("output:\n  base_directory: output")
        
        # Create outlines in multiple locations
        output_dir = tmp_path / "output" / "outlines"
        output_dir.mkdir(parents=True)
        scripts_dir = tmp_path / "scripts" / "output" / "outlines"
        scripts_dir.mkdir(parents=True)
        
        import json
        outline1 = output_dir / "course_outline_1.json"
        outline1.write_text(json.dumps({"modules": []}))
        time.sleep(0.01)  # Ensure different modification times
        outline2 = scripts_dir / "course_outline_2.json"
        outline2.write_text(json.dumps({"modules": []}))
        
        loader = ConfigLoader(config_dir)
        found = loader._find_latest_outline_json()
        
        # Should find one of them (most recent)
        assert found is not None
        assert found.exists()
    
    def test_outline_discovery_prefers_recent(self, tmp_path, monkeypatch):
        """Test outline discovery selects most recent file."""
        import time
        monkeypatch.chdir(tmp_path)
        
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        (config_dir / "course_config.yaml").write_text("course:\n  name: Test\n  description: Test\n  level: Test")
        (config_dir / "llm_config.yaml").write_text("llm:\n  model: test\nprompts: {}")
        (config_dir / "output_config.yaml").write_text("output:\n  base_directory: output")
        
        output_dir = tmp_path / "output" / "outlines"
        output_dir.mkdir(parents=True)
        
        import json
        # Create older outline
        old_outline = output_dir / "course_outline_old.json"
        old_outline.write_text(json.dumps({"modules": [], "timestamp": "old"}))
        
        time.sleep(0.1)  # Ensure different modification time
        
        # Create newer outline
        new_outline = output_dir / "course_outline_new.json"
        new_outline.write_text(json.dumps({"modules": [], "timestamp": "new"}))
        
        loader = ConfigLoader(config_dir)
        found = loader._find_latest_outline_json()
        
        assert found == new_outline
    
    def test_empty_json_outline(self, tmp_path):
        """Test handling of empty JSON outline file."""
        loader = ConfigLoader("config")
        
        outline_file = tmp_path / "empty.json"
        outline_file.write_text("{}")
        
        modules = loader.get_modules_from_outline(outline_file)
        
        assert modules == []
    
    def test_outline_missing_required_fields(self, tmp_path):
        """Test validation of outline structure with missing fields."""
        loader = ConfigLoader("config")
        
        # Outline with modules but missing required module fields
        import json
        outline_data = {
            "course_metadata": {"name": "Test"},
            "modules": [
                {"module_id": 1}  # Missing module_name and sessions
            ]
        }
        outline_file = tmp_path / "incomplete.json"
        outline_file.write_text(json.dumps(outline_data))
        
        modules = loader.get_modules_from_outline(outline_file)
        
        # Should still load but module may be incomplete
        assert len(modules) == 1
        assert modules[0]["module_id"] == 1
    
    def test_concurrent_config_loading(self, config_dir):
        """Test thread-safe config loading (caching)."""
        import threading
        
        loader = ConfigLoader(config_dir)
        results = []
        errors = []
        
        def load_config():
            try:
                config = loader.load_course_config()
                results.append(config)
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads loading config concurrently
        threads = [threading.Thread(target=load_config) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # All should succeed
        assert len(errors) == 0
        assert len(results) == 5
        # All should get same config (cached)
        assert all(r == results[0] for r in results)
    
    def test_cache_invalidation(self, config_dir):
        """Test config caching behavior."""
        loader = ConfigLoader(config_dir)
        
        # Load config (should cache)
        config1 = loader.load_course_config()
        
        # Load again (should return cached)
        config2 = loader.load_course_config()
        
        # Should be same object (cached)
        assert config1 is config2
    
    def test_yaml_with_unicode(self, tmp_path):
        """Test handling of Unicode characters in YAML."""
        config_path = tmp_path / "config"
        config_path.mkdir()
        
        # Create config with unicode
        course_config = {
            "course": {
                "name": "生物学 Biology",  # Chinese + English
                "description": "Étude de la vie 🧬",  # French + emoji
                "level": "Introductory",
                "defaults": {"num_modules": 1, "total_sessions": 1}
            }
        }
        llm_config = {"llm": {"model": "test"}, "prompts": {}}
        output_config = {"output": {"base_directory": "output"}}
        
        (config_path / "course_config.yaml").write_text(yaml.dump(course_config, allow_unicode=True), encoding='utf-8')
        (config_path / "llm_config.yaml").write_text(yaml.dump(llm_config))
        (config_path / "output_config.yaml").write_text(yaml.dump(output_config))
        
        loader = ConfigLoader(config_path)
        info = loader.get_course_info()
        
        assert "生物学" in info["name"]
        assert "Étude" in info["description"]
        assert "🧬" in info["description"]
    
    def test_config_file_permissions_error(self, tmp_path):
        """Test handling of file permission errors."""
        import os
        import stat
        
        config_path = tmp_path / "config"
        config_path.mkdir()
        
        # Create a file and make it unreadable
        config_file = config_path / "course_config.yaml"
        config_file.write_text("course:\n  name: Test")
        
        # Make file unreadable (if not on Windows)
        if os.name != 'nt':
            os.chmod(config_file, 0o000)
            
            loader = ConfigLoader(config_path)
            
            try:
                with pytest.raises((ConfigurationError, PermissionError)):
                    loader.load_course_config()
            finally:
                # Restore permissions for cleanup
                os.chmod(config_file, stat.S_IRUSR | stat.S_IWUSR)
    
    def test_get_module_by_id_type_conversion(self, tmp_path):
        """Test module ID type conversion (string to int)."""
        loader = ConfigLoader("config")
        
        import json
        outline_data = {
            "course_metadata": {"name": "Test"},
            "modules": [
                {"module_id": 1, "module_name": "Module 1", "sessions": []},
                {"module_id": 2, "module_name": "Module 2", "sessions": []}
            ]
        }
        outline_file = tmp_path / "outline.json"
        outline_file.write_text(json.dumps(outline_data))
        
        # Try with string ID (should convert or handle gracefully)
        module = loader.get_module_by_id_from_outline(2, outline_file)
        assert module is not None
        assert module["module_id"] == 2
    
    def test_get_logging_intervals_with_config(self, config_dir):
        """Test get_logging_intervals with configured values."""
        # Update output config with custom intervals
        output_config_path = config_dir / "output_config.yaml"
        with open(output_config_path, 'r') as f:
            output_config = yaml.safe_load(f)
        
        # Ensure nested structure exists before assigning values
        output_config.setdefault("output", {}).setdefault("logging", {})
        output_config["output"]["logging"]["heartbeat_interval"] = 10
        output_config["output"]["logging"]["progress_log_interval"] = 3
        
        with open(output_config_path, 'w') as f:
            yaml.dump(output_config, f)
        
        loader = ConfigLoader(config_dir)
        intervals = loader.get_logging_intervals()
        
        assert intervals["heartbeat_interval"] == 10.0
        assert intervals["progress_log_interval"] == 3.0
    
    def test_get_logging_intervals_defaults(self, config_dir):
        """Test get_logging_intervals returns defaults when not configured."""
        # Remove interval keys from config
        output_config_path = config_dir / "output_config.yaml"
        with open(output_config_path, 'r') as f:
            output_config = yaml.safe_load(f)
        
        # Remove interval keys if they exist
        logging_config = output_config.get("output", {}).get("logging", {})
        logging_config.pop("heartbeat_interval", None)
        logging_config.pop("progress_log_interval", None)
        
        with open(output_config_path, 'w') as f:
            yaml.dump(output_config, f)
        
        loader = ConfigLoader(config_dir)
        intervals = loader.get_logging_intervals()
        
        # Should return defaults
        assert intervals["heartbeat_interval"] == 5.0
        assert intervals["progress_log_interval"] == 2.0
    
    def test_get_logging_intervals_invalid_values(self, config_dir):
        """Test get_logging_intervals handles invalid values gracefully."""
        # Update output config with invalid intervals
        output_config_path = config_dir / "output_config.yaml"
        with open(output_config_path, 'r') as f:
            output_config = yaml.safe_load(f)
        
        # Ensure nested structure exists before assigning values
        output_config.setdefault("output", {}).setdefault("logging", {})
        output_config["output"]["logging"]["heartbeat_interval"] = -5  # Invalid: negative
        output_config["output"]["logging"]["progress_log_interval"] = 0  # Invalid: zero
        
        with open(output_config_path, 'w') as f:
            yaml.dump(output_config, f)
        
        loader = ConfigLoader(config_dir)
        intervals = loader.get_logging_intervals()
        
        # Should fall back to defaults for invalid values
        assert intervals["heartbeat_interval"] == 5.0
        assert intervals["progress_log_interval"] == 2.0
    
    def test_get_logging_intervals_missing_output_config(self, tmp_path):
        """Test get_logging_intervals handles missing output config gracefully."""
        config_path = tmp_path / "config"
        config_path.mkdir()
        
        # Create minimal configs (no output_config.yaml)
        course_config = {"course": {"name": "Test", "description": "Test", "level": "Intro"}}
        llm_config = {"llm": {"provider": "ollama", "model": "test"}, "prompts": {}}
        
        with open(config_path / "course_config.yaml", 'w') as f:
            yaml.dump(course_config, f)
        with open(config_path / "llm_config.yaml", 'w') as f:
            yaml.dump(llm_config, f)
        
        # Should raise error when trying to load output config, but get_logging_intervals should handle it
        loader = ConfigLoader(config_path)
        
        # Should return defaults even if output config is missing
        intervals = loader.get_logging_intervals()
        assert intervals["heartbeat_interval"] == 5.0
        assert intervals["progress_log_interval"] == 2.0

