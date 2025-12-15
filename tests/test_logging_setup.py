"""Tests for logging setup utilities."""

import pytest
import logging
from pathlib import Path
from src.utils.logging_setup import (
    setup_logging,
    log_section_header,
    log_section_clean,
    log_info_box,
    log_status_item,
    log_parameters,
    log_validation_results,
    log_summary_box,
    get_logging_config,
    SEPARATOR_LINE
)
from src.config.loader import ConfigLoader


class TestSetupLogging:
    """Test setup_logging function."""
    
    def test_setup_logging_defaults(self, tmp_path, caplog):
        """Test setup_logging with default parameters."""
        log_dir = tmp_path / "logs"
        
        with caplog.at_level(logging.INFO):
            result = setup_logging("test_script", log_dir=log_dir)
        
        assert result is not None
        assert result.exists()
        assert "test_script" in result.name
        assert result.suffix == ".log"
        assert log_dir.exists()
    
    def test_setup_logging_different_levels(self, tmp_path, caplog):
        """Test setup_logging with different log levels."""
        log_dir = tmp_path / "logs"
        
        for level in ["DEBUG", "INFO", "WARNING", "ERROR"]:
            with caplog.at_level(getattr(logging, level)):
                result = setup_logging("test_script", log_dir=log_dir, log_level=level)
                assert result.exists()
                
                # Verify log level is set correctly
                root_logger = logging.getLogger()
                assert root_logger.level == getattr(logging, level)
    
    def test_setup_logging_console_only(self, tmp_path):
        """Test setup_logging with console output only."""
        log_dir = tmp_path / "logs"
        
        result = setup_logging(
            "test_script",
            log_dir=log_dir,
            console_output=True,
            file_output=False
        )
        
        assert result is None  # No file created
        # Verify console handler is set up
        root_logger = logging.getLogger()
        handlers = root_logger.handlers
        assert len(handlers) == 1  # Only console handler
        assert isinstance(handlers[0], logging.StreamHandler)
        # Verify no log file was created
        log_files = list(log_dir.glob("*.log"))
        assert len(log_files) == 0
    
    def test_setup_logging_file_only(self, tmp_path, caplog):
        """Test setup_logging with file output only."""
        log_dir = tmp_path / "logs"
        
        with caplog.at_level(logging.INFO):
            result = setup_logging(
                "test_script",
                log_dir=log_dir,
                console_output=False,
                file_output=True
            )
        
        assert result is not None
        assert result.exists()
        # Verify file contains log content
        log_content = result.read_text(encoding='utf-8')
        assert "Logging to file" in log_content
    
    def test_setup_logging_custom_format(self, tmp_path, caplog):
        """Test setup_logging with custom log format."""
        log_dir = tmp_path / "logs"
        custom_format = "%(levelname)s - %(message)s"
        
        with caplog.at_level(logging.INFO):
            result = setup_logging(
                "test_script",
                log_dir=log_dir,
                log_format=custom_format
            )
            # Log a message after setup to verify format
            logging.info("Test message")
        
        assert result.exists()
        # Verify custom format is used - read file after logging
        log_content = result.read_text(encoding='utf-8')
        # Should contain the custom format (levelname - message)
        assert "Test message" in log_content
    
    def test_setup_logging_creates_directory(self, tmp_path):
        """Test that setup_logging creates log directory if it doesn't exist."""
        log_dir = tmp_path / "new_logs" / "subdir"
        assert not log_dir.exists()
        
        result = setup_logging("test_script", log_dir=log_dir)
        
        assert log_dir.exists()
        assert log_dir.is_dir()
        assert result.exists()
    
    def test_setup_logging_default_directory(self, tmp_path, monkeypatch):
        """Test setup_logging with default directory (output/logs)."""
        # Change to tmp_path to avoid creating actual output directory
        original_cwd = Path.cwd()
        monkeypatch.chdir(tmp_path)
        
        try:
            result = setup_logging("test_script", log_dir=None)
            # Should create output/logs directory
            expected_dir = tmp_path / "output" / "logs"
            assert expected_dir.exists()
            assert result is not None
        finally:
            monkeypatch.chdir(original_cwd)
    
    def test_setup_logging_clears_existing_handlers(self, tmp_path):
        """Test that setup_logging clears existing handlers."""
        log_dir = tmp_path / "logs"
        
        # Add a handler manually
        root_logger = logging.getLogger()
        handler = logging.StreamHandler()
        root_logger.addHandler(handler)
        initial_handler_count = len(root_logger.handlers)
        
        # Setup logging should clear and add new handlers
        result = setup_logging("test_script", log_dir=log_dir)
        
        # Should have new handlers (console + file = 2)
        assert len(root_logger.handlers) == 2
        assert result.exists()


class TestLogSectionHeader:
    """Test log_section_header function."""
    
    def test_log_section_header_major(self, caplog):
        """Test log_section_header with major separator."""
        logger = logging.getLogger(__name__)
        
        with caplog.at_level(logging.INFO):
            log_section_header(logger, "Test Section", major=True)
        
        assert len(caplog.records) == 3
        assert "═" * 80 in caplog.text
        assert "Test Section" in caplog.text
    
    def test_log_section_header_minor(self, caplog):
        """Test log_section_header with minor separator."""
        logger = logging.getLogger(__name__)
        
        with caplog.at_level(logging.INFO):
            log_section_header(logger, "Test Section", major=False)
        
        assert len(caplog.records) == 3
        assert "─" * 80 in caplog.text
        assert "Test Section" in caplog.text


class TestLogSectionClean:
    """Test log_section_clean function."""
    
    def test_log_section_clean_default_emoji(self, caplog):
        """Test log_section_clean with default emoji."""
        logger = logging.getLogger(__name__)
        
        with caplog.at_level(logging.INFO):
            log_section_clean(logger, "Test Section")
        
        assert len(caplog.records) == 3
        assert "📋 Test Section" in caplog.text
        assert SEPARATOR_LINE in caplog.text
    
    def test_log_section_clean_custom_emoji(self, caplog):
        """Test log_section_clean with custom emoji."""
        logger = logging.getLogger(__name__)
        
        with caplog.at_level(logging.INFO):
            log_section_clean(logger, "Test Section", emoji="✅")
        
        assert len(caplog.records) == 3
        assert "✅ Test Section" in caplog.text
        assert SEPARATOR_LINE in caplog.text


class TestLogInfoBox:
    """Test log_info_box function."""
    
    def test_log_info_box_basic(self, caplog):
        """Test log_info_box with basic items."""
        logger = logging.getLogger(__name__)
        items = {
            "Key1": "Value1",
            "Key2": "Value2"
        }
        
        with caplog.at_level(logging.INFO):
            log_info_box(logger, "Test Box", items)
        
        assert "ℹ️ Test Box" in caplog.text
        assert "• Key1: Value1" in caplog.text
        assert "• Key2: Value2" in caplog.text
        assert SEPARATOR_LINE in caplog.text
    
    def test_log_info_box_custom_emoji(self, caplog):
        """Test log_info_box with custom emoji."""
        logger = logging.getLogger(__name__)
        items = {"Key": "Value"}
        
        with caplog.at_level(logging.INFO):
            log_info_box(logger, "Test Box", items, emoji="⚠️")
        
        assert "⚠️ Test Box" in caplog.text
    
    def test_log_info_box_empty_dict(self, caplog):
        """Test log_info_box with empty dictionary."""
        logger = logging.getLogger(__name__)
        
        with caplog.at_level(logging.INFO):
            log_info_box(logger, "Test Box", {})
        
        assert "ℹ️ Test Box" in caplog.text
        assert SEPARATOR_LINE in caplog.text


class TestLogStatusItem:
    """Test log_status_item function."""
    
    def test_log_status_item_success(self, caplog):
        """Test log_status_item with success status."""
        logger = logging.getLogger(__name__)
        
        with caplog.at_level(logging.INFO):
            log_status_item(logger, "Test Label", "Test Value", status="success")
        
        assert "✅ Test Label: Test Value" in caplog.text
    
    def test_log_status_item_error(self, caplog):
        """Test log_status_item with error status."""
        logger = logging.getLogger(__name__)
        
        with caplog.at_level(logging.INFO):
            log_status_item(logger, "Test Label", "Test Value", status="error")
        
        assert "❌ Test Label: Test Value" in caplog.text
    
    def test_log_status_item_warning(self, caplog):
        """Test log_status_item with warning status."""
        logger = logging.getLogger(__name__)
        
        with caplog.at_level(logging.INFO):
            log_status_item(logger, "Test Label", "Test Value", status="warning")
        
        assert "⚠️ Test Label: Test Value" in caplog.text
    
    def test_log_status_item_info(self, caplog):
        """Test log_status_item with info status."""
        logger = logging.getLogger(__name__)
        
        with caplog.at_level(logging.INFO):
            log_status_item(logger, "Test Label", "Test Value", status="info")
        
        assert "ℹ️ Test Label: Test Value" in caplog.text
    
    def test_log_status_item_check(self, caplog):
        """Test log_status_item with check status."""
        logger = logging.getLogger(__name__)
        
        with caplog.at_level(logging.INFO):
            log_status_item(logger, "Test Label", "Test Value", status="check")
        
        assert "✓ Test Label: Test Value" in caplog.text
    
    def test_log_status_item_default(self, caplog):
        """Test log_status_item with default/unknown status."""
        logger = logging.getLogger(__name__)
        
        with caplog.at_level(logging.INFO):
            log_status_item(logger, "Test Label", "Test Value", status="unknown")
        
        assert "• Test Label: Test Value" in caplog.text


class TestLogParameters:
    """Test log_parameters function."""
    
    def test_log_parameters_basic(self, caplog):
        """Test log_parameters with basic parameters."""
        logger = logging.getLogger(__name__)
        params = {
            "param1": "value1",
            "param2": "value2"
        }
        
        with caplog.at_level(logging.INFO):
            log_parameters(logger, params)
        
        assert "Parameters (2 provided):" in caplog.text
        assert "✓ param1" in caplog.text
        assert "✓ param2" in caplog.text
    
    def test_log_parameters_different_types(self, caplog):
        """Test log_parameters with different data types."""
        logger = logging.getLogger(__name__)
        params = {
            "string": "test",
            "int": 42,
            "float": 3.14,
            "bool": True,
            "none": None
        }
        
        with caplog.at_level(logging.INFO):
            log_parameters(logger, params)
        
        assert "✓ string" in caplog.text
        assert "✓ int" in caplog.text
        assert "✓ float" in caplog.text
        assert "✓ bool" in caplog.text
        assert "✓ none" in caplog.text
    
    def test_log_parameters_long_string(self, caplog):
        """Test log_parameters with long string truncation."""
        logger = logging.getLogger(__name__)
        long_string = "a" * 100
        params = {"long_param": long_string}
        
        with caplog.at_level(logging.INFO):
            log_parameters(logger, params)
        
        assert "..." in caplog.text  # Should be truncated
    
    def test_log_parameters_empty(self, caplog):
        """Test log_parameters with empty dictionary."""
        logger = logging.getLogger(__name__)
        
        with caplog.at_level(logging.INFO):
            log_parameters(logger, {})
        
        assert "Parameters (0 provided):" in caplog.text
    
    def test_log_parameters_custom_title(self, caplog):
        """Test log_parameters with custom title."""
        logger = logging.getLogger(__name__)
        params = {"key": "value"}
        
        with caplog.at_level(logging.INFO):
            log_parameters(logger, params, title="Custom Title")
        
        assert "Custom Title (1 provided):" in caplog.text


class TestLogValidationResults:
    """Test log_validation_results function."""
    
    def test_log_validation_results_success(self, caplog):
        """Test log_validation_results with all variables provided."""
        logger = logging.getLogger(__name__)
        required = {"var1", "var2"}
        provided = {"var1", "var2"}
        missing = set()
        extra = set()
        
        with caplog.at_level(logging.INFO):
            log_validation_results(logger, required, provided, missing, extra)
        
        assert "✓ All 2 required variables provided" in caplog.text
        assert "✓ No missing variables" in caplog.text
        assert "✓ No extra variables" in caplog.text
    
    def test_log_validation_results_missing_vars(self, caplog):
        """Test log_validation_results with missing variables."""
        logger = logging.getLogger(__name__)
        required = {"var1", "var2", "var3"}
        provided = {"var1"}
        missing = {"var2", "var3"}
        extra = set()
        
        with caplog.at_level(logging.INFO):
            log_validation_results(logger, required, provided, missing, extra)
        
        assert "✗ Missing 2 required variables:" in caplog.text
        assert "- var2" in caplog.text
        assert "- var3" in caplog.text
    
    def test_log_validation_results_extra_vars(self, caplog):
        """Test log_validation_results with extra variables."""
        logger = logging.getLogger(__name__)
        required = {"var1"}
        provided = {"var1", "var2", "var3"}
        missing = set()
        extra = {"var2", "var3"}
        
        with caplog.at_level(logging.INFO):
            log_validation_results(logger, required, provided, missing, extra)
        
        assert "✓ All 1 required variables provided" in caplog.text
        assert "⚠️  Extra 2 variables provided" in caplog.text
        assert "- var2" in caplog.text
        assert "- var3" in caplog.text
    
    def test_log_validation_results_both_missing_and_extra(self, caplog):
        """Test log_validation_results with both missing and extra variables."""
        logger = logging.getLogger(__name__)
        required = {"var1", "var2"}
        provided = {"var1", "var3"}
        missing = {"var2"}
        extra = {"var3"}
        
        with caplog.at_level(logging.INFO):
            log_validation_results(logger, required, provided, missing, extra)
        
        assert "✗ Missing 1 required variables:" in caplog.text
        assert "⚠️  Extra 1 variables provided" in caplog.text


class TestLogSummaryBox:
    """Test log_summary_box function."""
    
    def test_log_summary_box_success(self, caplog):
        """Test log_summary_box with success status."""
        logger = logging.getLogger(__name__)
        items = {
            "Item1": "Value1",
            "Item2": 42
        }
        
        with caplog.at_level(logging.INFO):
            log_summary_box(logger, "Test Summary", items, status="success")
        
        assert "═" * 80 in caplog.text
        assert "✅ Test Summary" in caplog.text
        assert "• Item1: Value1" in caplog.text
        assert "• Item2: 42" in caplog.text
    
    def test_log_summary_box_warning(self, caplog):
        """Test log_summary_box with warning status."""
        logger = logging.getLogger(__name__)
        items = {"Item": "Value"}
        
        with caplog.at_level(logging.INFO):
            log_summary_box(logger, "Test Summary", items, status="warning")
        
        assert "⚠️ Test Summary" in caplog.text
    
    def test_log_summary_box_error(self, caplog):
        """Test log_summary_box with error status."""
        logger = logging.getLogger(__name__)
        items = {"Item": "Value"}
        
        with caplog.at_level(logging.INFO):
            log_summary_box(logger, "Test Summary", items, status="error")
        
        assert "✗ Test Summary" in caplog.text
    
    def test_log_summary_box_info(self, caplog):
        """Test log_summary_box with info status."""
        logger = logging.getLogger(__name__)
        items = {"Item": "Value"}
        
        with caplog.at_level(logging.INFO):
            log_summary_box(logger, "Test Summary", items, status="info")
        
        assert "📊 Test Summary" in caplog.text
    
    def test_log_summary_box_numeric_formatting(self, caplog):
        """Test log_summary_box with numeric value formatting."""
        logger = logging.getLogger(__name__)
        items = {
            "Count": 1000,
            "Price": 99.99
        }
        
        with caplog.at_level(logging.INFO):
            log_summary_box(logger, "Test Summary", items)
        
        # Numeric values should be formatted with commas
        assert "• Count: 1,000" in caplog.text or "• Count: 1000" in caplog.text
        assert "• Price: 99.99" in caplog.text


class TestGetLoggingConfig:
    """Test get_logging_config function."""
    
    def test_get_logging_config_with_valid_config(self, tmp_path):
        """Test get_logging_config with valid ConfigLoader."""
        # Create a minimal config structure
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        
        output_config = {
            "output": {
                "logging": {
                    "level": "DEBUG",
                    "format": "%(message)s",
                    "console": False,
                    "file": "custom.log"
                }
            }
        }
        
        import yaml
        output_config_path = config_dir / "output_config.yaml"
        with open(output_config_path, 'w') as f:
            yaml.dump(output_config, f)
        
        config_loader = ConfigLoader(str(config_dir))
        result = get_logging_config(config_loader)
        
        assert result['level'] == 'DEBUG'
        assert result['format'] == '%(message)s'
        assert result['console'] is False
        assert result['file'] == 'custom.log'
    
    def test_get_logging_config_with_missing_config(self, tmp_path):
        """Test get_logging_config with missing config (should return defaults)."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        
        # Create empty or minimal config
        output_config = {"output": {}}
        import yaml
        output_config_path = config_dir / "output_config.yaml"
        with open(output_config_path, 'w') as f:
            yaml.dump(output_config, f)
        
        config_loader = ConfigLoader(str(config_dir))
        result = get_logging_config(config_loader)
        
        # Should return defaults
        assert result['level'] == 'INFO'
        assert result['console'] is True
        assert 'format' in result
        assert 'file' in result
    
    def test_get_logging_config_with_exception(self, tmp_path):
        """Test get_logging_config when ConfigLoader raises exception using real invalid config."""
        from src.config.loader import ConfigLoader
        import yaml
        
        # Create config directory with invalid output_config.yaml that will cause exception
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        
        # Create invalid YAML file that will cause parsing error when loaded
        invalid_config_path = config_dir / "output_config.yaml"
        invalid_config_path.write_text("invalid: yaml: content: [unclosed bracket", encoding='utf-8')
        
        # Create minimal valid course and llm configs so ConfigLoader can initialize
        course_config = {"course": {"name": "Test"}}
        llm_config = {"llm": {"provider": "ollama", "model": "test"}}
        
        with open(config_dir / "course_config.yaml", "w") as f:
            yaml.dump(course_config, f)
        with open(config_dir / "llm_config.yaml", "w") as f:
            yaml.dump(llm_config, f)
        
        # Create real ConfigLoader - it will raise exception when loading output_config
        # ConfigLoader initializes successfully, but load_output_config() will fail
        failing_loader = ConfigLoader(config_dir)
        
        # Verify that load_output_config raises exception with invalid YAML
        with pytest.raises(Exception):
            failing_loader.load_output_config()
        
        # Now test get_logging_config with this loader - should catch exception and return defaults
        result = get_logging_config(failing_loader)
        
        # Should return defaults on exception
        assert result['level'] == 'INFO'
        assert result['console'] is True
        assert 'format' in result
        assert 'file' in result

