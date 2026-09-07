"""Tests for the validation runner module (logic moved from scripts/02_run_tests.py)."""

import json

import pytest

from src.validation.runner import (
    categorize_error,
    extract_failures,
    extract_warnings,
    get_test_file_count,
    parse_durations,
    parse_pytest_output,
    parse_test_modules,
    save_json_results,
    save_test_output,
)

pytestmark = pytest.mark.unit


SAMPLE_PYTEST_OUTPUT = (
    "============================= test session starts =============================\n"
    "collected 658 items\n"
    "\n"
    "tests/test_config_loader.py::TestConfigLoader::test_load_course_config PASSED [ 12%]\n"
    "tests/test_config_loader.py::TestConfigLoader::test_missing_file PASSED [ 12%]\n"
    "tests/test_parser.py::TestParser::test_parse_module FAILED [ 25%]\n"
    "\n"
    "=================================== FAILURES ===================================\n"
    "_________________________________ test_parse_module ____________________________\n"
    "FAILED tests/test_parser.py::TestParser::test_parse_module - assert 3 == 2\n"
    "E   assert 3 == 2\n"
    "\n"
    "=============================== warnings summary ===============================\n"
    "tests/test_parser.py: 1 warning\n"
    "\n"
    "========================= 2 passed, 1 failed, 3 skipped, 1 warning in 5.23s =========================\n"
)


class TestParsePytestOutput:
    """Test pytest output statistics parsing."""

    def test_counts_all_categories(self):
        """Test that passed/failed/skipped/warnings/duration are extracted."""
        stats = parse_pytest_output(SAMPLE_PYTEST_OUTPUT)
        assert stats["passed"] == 2
        assert stats["failed"] == 1
        assert stats["skipped"] == 3
        assert stats["warnings"] == 1
        assert stats["duration"] == 5.23
        assert stats["total"] == 2 + 1 + 3

    def test_empty_output(self):
        """Test parsing output with no summary line yields zeroed stats."""
        stats = parse_pytest_output("no summary here")
        assert stats == {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 0,
            "warnings": 0,
            "duration": 0.0,
        }

    def test_errors_category(self):
        """Test that error counts are extracted."""
        stats = parse_pytest_output("2 errors in 1.5s")
        assert stats["errors"] == 2


class TestParseTestModules:
    """Test per-module test result extraction."""

    def test_groups_results_by_module(self):
        """Test results are grouped per test file with durations."""
        output = (
            "tests/test_config_loader.py::test_a PASSED [0.10s]\n"
            "tests/test_config_loader.py::test_b PASSED [0.30s]\n"
            "tests/test_parser.py::test_c FAILED [0.50s]\n"
        )
        module_stats = parse_test_modules(output, None)
        assert set(module_stats.keys()) == {"tests/test_config_loader.py", "tests/test_parser.py"}
        assert module_stats["tests/test_config_loader.py"]["passed"] == 2
        assert module_stats["tests/test_config_loader.py"]["avg_duration"] == pytest.approx(0.20)
        assert module_stats["tests/test_parser.py"]["failed"] == 1

    def test_no_matches(self):
        """Test output without verbose test lines yields empty mapping."""
        assert parse_test_modules("nothing here", None) == {}


class TestParseDurations:
    """Test slow-test duration parsing."""

    def test_sorted_slowest_first(self):
        """Test durations are parsed and sorted descending."""
        output = (
            "========== slowest 10 tests ==========\n"
            "0.50s call    tests/test_a.py::test_slow\n"
            "1.20s call    tests/test_b.py::test_slower\n"
            "========================= 78 passed in 5.23s =========================\n"
        )
        durations = parse_durations(output)
        assert durations == [
            ("tests/test_b.py::test_slower", 1.20),
            ("tests/test_a.py::test_slow", 0.50),
        ]

    def test_empty_section(self):
        """Test missing durations section yields empty list."""
        assert parse_durations("78 passed in 5.23s") == []


class TestExtractWarnings:
    """Test warning extraction."""

    def test_collects_warning_lines(self):
        """Test lines in the warnings summary section are collected."""
        warnings = extract_warnings(SAMPLE_PYTEST_OUTPUT)
        assert "tests/test_parser.py: 1 warning" in warnings

    def test_no_warnings_section(self):
        """Test output without warnings section yields empty list."""
        assert extract_warnings("78 passed in 5.23s") == []


class TestExtractFailures:
    """Test failure detail extraction."""

    def test_extracts_assertion_and_expected_actual(self):
        """Test assertion, expected/actual, and error type are captured."""
        output = (
            "=================================== FAILURES ===================================\n"
            "FAILED tests/test_parser.py::test_parse_module\n"
            "E   assert 3 == 2\n"
            "\n"
            "========================= 1 failed, 2 passed in 0.10s =========================\n"
        )
        failures = extract_failures(output)
        assert len(failures) == 1
        failure = failures[0]
        assert "test_parse_module" in failure["test"]
        assert failure["assertion"] == "3 == 2"
        assert failure["expected"] == "2"
        assert failure["actual"] == "3"

    def test_no_failures(self):
        """Test passing output yields no failures."""
        assert extract_failures("78 passed in 5.23s") == []


class TestCategorizeError:
    """Test error categorization."""

    def test_import_error(self):
        """Test import-related context maps to import_error."""
        assert categorize_error("FAILED test", ["ModuleNotFoundError: no module"]) == "import_error"

    def test_timeout(self):
        """Test timeout context maps to timeout."""
        assert categorize_error("FAILED test", ["operation timed out"]) == "timeout"

    def test_assertion_failure(self):
        """Test assert in failure line maps to assertion_failure."""
        assert categorize_error("FAILED test - assert x == y", [""]) == "assertion_failure"

    def test_unknown_error(self):
        """Test unmapped context maps to unknown_error."""
        assert categorize_error("FAILED test", ["something odd"]) == "unknown_error"


class TestSaveReports:
    """Test report file saving."""

    def test_save_test_output(self, tmp_path):
        """Test output is saved to a timestamped .log file."""
        output_file = save_test_output("captured output", tmp_path)
        assert output_file.exists()
        assert output_file.name.startswith("test_results_")
        assert output_file.suffix == ".log"
        assert output_file.read_text(encoding="utf-8") == "captured output"

    def test_save_json_results(self, tmp_path):
        """Test structured results are saved as parseable JSON."""
        results = {"stats": {"passed": 2, "failed": 0}}
        json_file = save_json_results(results, tmp_path)
        assert json_file.exists()
        assert json_file.suffix == ".json"
        assert json.loads(json_file.read_text(encoding="utf-8")) == results


class TestGetTestFileCount:
    """Test test file counting."""

    def test_counts_test_files_only(self, tmp_path):
        """Test only test_*.py files are counted."""
        (tmp_path / "test_a.py").write_text("", encoding="utf-8")
        (tmp_path / "test_b.py").write_text("", encoding="utf-8")
        (tmp_path / "helper.py").write_text("", encoding="utf-8")
        assert get_test_file_count(tmp_path) == 2

    def test_empty_dir(self, tmp_path):
        """Test empty directory counts zero."""
        assert get_test_file_count(tmp_path) == 0
