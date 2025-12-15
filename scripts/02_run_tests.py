#!/usr/bin/env python3
"""02 - Configuration validation and pytest testing.

This script performs:
- Configuration validation (YAML files, structure, settings)
- Ollama service availability check
- Fast unit test execution (config, parser, utils tests)
- Optional integration tests with --include-ollama flag
- Per-module and overall test result logging
- Automatic test report saving with timestamps
- Real-time output streaming (optional)
- Performance metrics (slow test identification)
- Structured JSON results (optional)
- Enhanced error reporting with categorization

By default, runs validation + fast unit tests (~5 seconds).
Use --include-ollama to also run integration tests (requires Ollama, slower).
Use --skip-tests for validation only, or --skip-validation for tests only.

Exit Codes:
  0 - Success (all tests passed)
  1 - Validation failed
  2 - Tests failed
  3 - No tests found or pytest error
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to Python path to allow imports when run directly
_script_dir = Path(__file__).resolve().parent
_project_root = _script_dir.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

import argparse
import json
import logging
import re
import subprocess
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from src.config.loader import ConfigLoader
from src.utils.helpers import ensure_uv_available, ollama_is_running
from src.utils.logging_setup import setup_logging, log_section_clean, log_info_box, log_status_item


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validation and comprehensive testing with pytest.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Validate config + run unit tests (fast, ~5s)
  %(prog)s --include-ollama         # Run all tests including integration tests (slow)
  %(prog)s --skip-tests             # Validation only, skip all tests
  %(prog)s --skip-validation        # Tests only, skip validation
  %(prog)s --verbose                # Detailed test output
  %(prog)s --no-save-output         # Don't save test results to file
  %(prog)s --json-results           # Save structured JSON results
  %(prog)s --show-slow-tests 20     # Show 20 slowest tests
  %(prog)s --slow-threshold 2.0     # Warn for tests >2 seconds
        """,
    )
    parser.add_argument(
        "--config-dir",
        type=Path,
        default=Path(__file__).parent.parent / "config",
        help="Path to config directory (default: ../config)",
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip pytest tests (validation only).",
    )
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip configuration validation (tests only).",
    )
    parser.add_argument(
        "--include-ollama",
        action="store_true",
        help="Include Ollama integration tests (slow, requires Ollama running).",
    )
    parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="Disable code coverage reporting (faster, default: coverage enabled)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show verbose test output.",
    )
    parser.add_argument(
        "--tests-path",
        type=Path,
        default=Path(__file__).parent.parent / "tests",
        help="Path to tests directory (default: ../tests)",
    )
    parser.add_argument(
        "--no-save-output",
        action="store_true",
        help="Don't save test output to file (saves by default).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory to save test reports (default: scripts/test_reports)",
    )
    parser.add_argument(
        "--stream-output",
        action="store_true",
        default=True,
        help="Stream pytest output in real-time (default: True)",
    )
    parser.add_argument(
        "--no-stream-output",
        dest="stream_output",
        action="store_false",
        help="Don't stream output, capture all at once",
    )
    parser.add_argument(
        "--json-results",
        action="store_true",
        help="Save structured JSON test results file",
    )
    parser.add_argument(
        "--show-slow-tests",
        type=int,
        default=10,
        help="Show slowest N tests (default: 10)",
    )
    parser.add_argument(
        "--slow-threshold",
        type=float,
        default=1.0,
        help="Threshold in seconds for 'slow' test warning (default: 1.0)",
    )
    return parser.parse_args()


def validate_config(config_dir: Path, logger: logging.Logger) -> bool:
    try:
        loader = ConfigLoader(config_dir)
        loader.validate_all_configs()
        logger.info("✓ Configuration validated")
        return True
    except Exception as exc:  # noqa: BLE001
        logger.error(f"Configuration validation failed: {exc}", exc_info=True)
        return False


def check_ollama(logger: logging.Logger) -> bool:
    if ollama_is_running():
        logger.info("✓ Ollama reachable")
        return True
    logger.warning("Ollama not reachable at http://localhost:11434")
    return False


def parse_pytest_output(output: str) -> Dict[str, Any]:
    """Parse pytest output to extract test statistics.
    
    Improved regex patterns handle edge cases and multiple formats.
    """
    stats = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "errors": 0,
        "warnings": 0,
        "duration": 0.0,
    }
    
    # Improved patterns to handle various pytest output formats
    # Handles: "78 passed", "78 passed in 5.23s", "78 passed, 2 warnings in 5.23s"
    summary_pattern = r"(\d+)\s+passed(?:,|\s|$)"
    failed_pattern = r"(\d+)\s+failed(?:,|\s|$)"
    skipped_pattern = r"(\d+)\s+skipped(?:,|\s|$)"
    error_pattern = r"(\d+)\s+error(?:s)?(?:,|\s|$)"
    warning_pattern = r"(\d+)\s+warning(?:s)?(?:,|\s|$)"
    # Duration can appear as "in 5.23s" or "in 5.23 seconds"
    duration_pattern = r"in\s+([\d.]+)\s*(?:s|seconds?)"
    
    if match := re.search(summary_pattern, output):
        stats["passed"] = int(match.group(1))
    if match := re.search(failed_pattern, output):
        stats["failed"] = int(match.group(1))
    if match := re.search(skipped_pattern, output):
        stats["skipped"] = int(match.group(1))
    if match := re.search(error_pattern, output):
        stats["errors"] = int(match.group(1))
    if match := re.search(warning_pattern, output):
        stats["warnings"] = int(match.group(1))
    if match := re.search(duration_pattern, output):
        stats["duration"] = float(match.group(1))
    
    stats["total"] = stats["passed"] + stats["failed"] + stats["skipped"] + stats["errors"]
    
    return stats


def parse_test_modules(output: str, tests_path: Path) -> Dict[str, Dict[str, Any]]:
    """Extract per-module test results from pytest output.
    
    Handles edge cases like special characters in test names and extracts timing.
    """
    module_stats = {}
    
    # Improved pattern handles:
    # - Test names with special characters (quotes, brackets, etc.)
    # - Different path formats (relative, absolute)
    # - Timing information if available
    # Example: "tests/test_config_loader.py::test_load_course_config PASSED [0.12s]"
    # Example: "tests/test_parser.py::TestParser::test_parse_module PASSED"
    test_pattern = r"(?:tests/|.*/tests/)?(test_\w+\.py)(?:::[\w:\[\]()\s]+)?\s+(PASSED|FAILED|SKIPPED|ERROR)(?:\s+\[([\d.]+)s\])?"
    
    for match in re.finditer(test_pattern, output):
        test_file = f"tests/{match.group(1)}"  # Normalize to tests/ prefix
        result = match.group(2)
        duration_str = match.group(3) if match.group(3) else None
        
        if test_file not in module_stats:
            module_stats[test_file] = {
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "errors": 0,
                "durations": [],
            }
        
        if result == "PASSED":
            module_stats[test_file]["passed"] += 1
        elif result == "FAILED":
            module_stats[test_file]["failed"] += 1
        elif result == "SKIPPED":
            module_stats[test_file]["skipped"] += 1
        elif result == "ERROR":
            module_stats[test_file]["errors"] += 1
        
        if duration_str:
            try:
                module_stats[test_file]["durations"].append(float(duration_str))
            except ValueError:
                pass
    
    # Calculate average durations per module
    for test_file in module_stats:
        durations = module_stats[test_file].get("durations", [])
        if durations:
            module_stats[test_file]["avg_duration"] = sum(durations) / len(durations)
            module_stats[test_file]["total_duration"] = sum(durations)
        else:
            module_stats[test_file]["avg_duration"] = 0.0
            module_stats[test_file]["total_duration"] = 0.0
    
    return module_stats


def get_test_file_count(tests_path: Path) -> int:
    """Count test files in tests directory."""
    return len(list(tests_path.glob("test_*.py")))


def save_test_output(output: str, output_dir: Path) -> Path:
    """Save test output to timestamped file."""
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"test_results_{timestamp}.log"
    
    output_file.write_text(output, encoding="utf-8")
    return output_file


def save_json_results(results: Dict[str, Any], output_dir: Path) -> Path:
    """Save structured test results as JSON."""
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_file = output_dir / f"test_results_{timestamp}.json"
    
    json_file.write_text(json.dumps(results, indent=2), encoding="utf-8")
    return json_file


def parse_durations(output: str) -> List[Tuple[str, float]]:
    """Parse pytest --durations output to extract slow tests.
    
    Returns list of (test_name, duration) tuples sorted by duration (slowest first).
    """
    durations = []
    in_durations_section = False
    
    for line in output.split("\n"):
        # Detect start of durations section
        if "slowest" in line.lower() and "test" in line.lower():
            in_durations_section = True
            continue
        
        if in_durations_section:
            # Pattern: "0.12s setup    tests/test_file.py::test_name"
            # or: "0.12s call    tests/test_file.py::test_name"
            match = re.match(r"([\d.]+)s\s+(?:setup|call|teardown)\s+(.+)", line.strip())
            if match:
                duration = float(match.group(1))
                test_name = match.group(2).strip()
                durations.append((test_name, duration))
            
            # Stop at summary line
            if line.strip().startswith("="):
                break
    
    # Sort by duration (slowest first)
    durations.sort(key=lambda x: x[1], reverse=True)
    return durations


def discover_tests(cmd_base: List[str], project_root: Path, logger: logging.Logger, explicit_test_files: Optional[List[str]] = None) -> Dict[str, Any]:
    """Discover tests using pytest --collect-only.
    
    Uses multiple strategies to extract test files:
    1. Parse pytest's tree output format (<Module test_*.py>)
    2. Extract from command arguments when explicitly specified
    3. Parse file paths from output
    
    Args:
        cmd_base: Base pytest command (without --collect-only)
        project_root: Project root directory
        logger: Logger instance
        explicit_test_files: Optional list of test files explicitly specified in command
    
    Returns dictionary with test count and list of test files.
    """
    # Remove -q flag to get more detailed output for parsing
    collect_cmd = [c for c in cmd_base if c != "-q"] + ["--collect-only"]
    
    logger.debug(f"Discovering tests with: {' '.join(collect_cmd)}")
    
    # Strategy 1: Extract test files from command arguments if explicitly specified
    test_files_from_cmd = set()
    if explicit_test_files:
        for test_file in explicit_test_files:
            # Normalize paths: remove 'tests/' prefix if present, then add it back
            normalized = test_file
            if not normalized.startswith("tests/"):
                if normalized.startswith("test_"):
                    normalized = f"tests/{normalized}"
            test_files_from_cmd.add(normalized)
        logger.debug(f"Extracted {len(test_files_from_cmd)} test files from command: {sorted(test_files_from_cmd)}")
    
    try:
        proc = subprocess.run(
            collect_cmd,
            capture_output=True,
            text=True,
            check=False,
            cwd=project_root,
            timeout=30,
        )
        
        output = proc.stdout + proc.stderr
        
        # Count test files and tests using multiple parsing strategies
        test_files = set()
        test_count = 0
        skipped_count = 0
        
        for line in output.split("\n"):
            # Strategy 2: Parse pytest's tree output format: "<Module test_file.py>"
            # Matches: <Module test_config_loader.py> or <Module tests/test_file.py>
            module_match = re.search(r"<Module\s+(?:tests/)?(test_\w+\.py)", line)
            if module_match:
                test_file_name = module_match.group(1)
                # Normalize to include tests/ prefix
                normalized_file = f"tests/{test_file_name}" if not test_file_name.startswith("tests/") else test_file_name
                test_files.add(normalized_file)
            
            # Strategy 3: Parse file paths in output: "tests/test_file.py"
            # Matches lines containing test file paths
            path_match = re.search(r"(?:^|\s)(tests/test_\w+\.py)", line)
            if path_match:
                test_files.add(path_match.group(1))
            
            # Count tests: "<Function test_name>" or "<Test test_name>"
            if "<Function" in line or "<Test" in line:
                test_count += 1
            
            # Count skipped tests
            if "SKIPPED" in line:
                skipped_count += 1
        
        # Strategy 4: Use explicit test files from command as fallback/primary source
        if test_files_from_cmd:
            # Merge with discovered files, but prioritize command files
            test_files.update(test_files_from_cmd)
            logger.debug(f"Combined test files: {len(test_files)} total (from cmd: {len(test_files_from_cmd)}, from parsing: {len(test_files - test_files_from_cmd)})")
        
        # If we still have no files but have test count, try to extract from command arguments as last resort
        if not test_files and test_count > 0:
            # Try to extract from command arguments as last resort
            # Only look for actual test file paths, not pytest options
            for arg in cmd_base:
                # Skip pytest options/flags
                if arg.startswith("-") or arg.startswith("--"):
                    continue
                # Look for test file paths
                if arg.startswith("tests/test_") and arg.endswith(".py"):
                    test_files.add(arg)
                elif arg.startswith("test_") and arg.endswith(".py") and "/" not in arg:
                    # Only add if it's a simple filename (not a path with slashes)
                    test_files.add(f"tests/{arg}")
            if test_files:
                logger.debug(f"Fallback: extracted {len(test_files)} files from command arguments")
        
        # Determine discovery method
        if test_files_from_cmd:
            # If all files came from command (no additional files from parsing)
            if test_files == test_files_from_cmd:
                discovery_method = "command"
            else:
                # Mix of command and parsed files
                discovery_method = "mixed"
        else:
            # No explicit files, all from parsing
            discovery_method = "parsed"
        
        return {
            "test_files": sorted(test_files),
            "test_file_count": len(test_files),
            "test_count": test_count,
            "skipped_count": skipped_count,
            "discovery_output": output,
            "discovery_method": discovery_method,
        }
    except subprocess.TimeoutExpired:
        logger.warning("Test discovery timed out")
        # Return command files as fallback
        return {
            "test_files": sorted(test_files_from_cmd) if test_files_from_cmd else [],
            "test_file_count": len(test_files_from_cmd) if test_files_from_cmd else 0,
            "test_count": 0,
            "skipped_count": 0,
            "discovery_output": "",
            "discovery_method": "timeout_fallback",
        }
    except Exception as exc:
        logger.warning(f"Test discovery failed: {exc}")
        # Return command files as fallback
        return {
            "test_files": sorted(test_files_from_cmd) if test_files_from_cmd else [],
            "test_file_count": len(test_files_from_cmd) if test_files_from_cmd else 0,
            "test_count": 0,
            "skipped_count": 0,
            "discovery_output": "",
            "discovery_method": "error_fallback",
        }


def stream_pytest_output(
    cmd: List[str],
    project_root: Path,
    logger: logging.Logger,
    stream: bool = True,
) -> Tuple[str, int]:
    """Run pytest and optionally stream output in real-time.
    
    Returns (output, exit_code) tuple.
    """
    if stream:
        logger.debug("Streaming pytest output in real-time...")
        output_lines = []
        
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            cwd=project_root,
        )
        
        # Stream output line by line
        test_count = 0
        for line in proc.stdout:
            line = line.rstrip()
            output_lines.append(line)
            
            # Log test progress at DEBUG level
            if "PASSED" in line or "FAILED" in line or "SKIPPED" in line:
                test_count += 1
                logger.debug(f"Test {test_count}: {line[:80]}...")
            elif "ERROR" in line and "::" in line:
                logger.debug(f"Error: {line[:80]}...")
            else:
                # Log other output at DEBUG level
                logger.debug(line)
        
        proc.wait()
        output = "\n".join(output_lines)
        return output, proc.returncode
    else:
        # Capture all output at once (original behavior)
        logger.debug("Capturing all pytest output...")
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            cwd=project_root,
        )
        return proc.stdout + proc.stderr, proc.returncode


def extract_warnings(output: str) -> List[str]:
    """Extract warning messages from pytest output."""
    warnings = []
    in_warnings_section = False
    
    for line in output.split("\n"):
        if "warnings summary" in line.lower():
            in_warnings_section = True
            continue
        if in_warnings_section:
            if line.strip() and not line.startswith("="):
                warnings.append(line)
            if line.startswith("=") and "passed" in line.lower():
                break
    
    return warnings


def extract_failures(output: str) -> List[Dict[str, Any]]:
    """Extract failure details from pytest output with full error context.
    
    Captures assertion details, expected vs actual values, and traceback.
    """
    failures = []
    current_failure = None
    in_traceback = False
    assertion_details = {}
    
    lines = output.split("\n")
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Detect test failure line
        if "FAILED" in line and "::" in line:
            if current_failure:
                failures.append(current_failure)
            
            # Extract test name and categorize error
            test_name = line.strip()
            error_type = categorize_error(line, lines[i+1:i+10] if i+10 < len(lines) else lines[i+1:])
            
            current_failure = {
                "test": test_name,
                "error_type": error_type,
                "details": [],
                "assertion": None,
                "expected": None,
                "actual": None,
                "traceback": [],
            }
            in_traceback = False
            assertion_details = {}
        elif current_failure:
            # Look for assertion details
            if "assert" in line.lower() and ("==" in line or "!=" in line or "in" in line.lower()):
                assertion_details["line"] = line.strip()
                # Try to extract expected/actual from common patterns
                if "==" in line:
                    parts = line.split("==")
                    if len(parts) == 2:
                        assertion_details["left"] = parts[0].strip()
                        assertion_details["right"] = parts[1].strip()
            
            # Look for "E   AssertionError:" or similar
            if re.match(r"E\s+(AssertionError|ValueError|TypeError|KeyError|AttributeError)", line):
                current_failure["error_type"] = line.split(":")[0].strip().replace("E   ", "")
                in_traceback = True
            
            # Capture expected/actual from common pytest output
            if "E   assert" in line:
                current_failure["assertion"] = line.replace("E   assert", "").strip()
            elif line.strip().startswith("E   ") and in_traceback:
                current_failure["traceback"].append(line.replace("E   ", "").strip())
            
            # Capture details
            if line.strip() and not line.startswith("="):
                current_failure["details"].append(line)
            
            # Detect end of failure block
            if line.strip().startswith("=") and current_failure["details"]:
                failures.append(current_failure)
                current_failure = None
                in_traceback = False
        
        i += 1
    
    if current_failure:
        failures.append(current_failure)
    
    # Post-process to extract expected/actual from assertion
    for failure in failures:
        if failure.get("assertion"):
            # Try to extract expected/actual from assertion text
            assertion = failure["assertion"]
            if " == " in assertion:
                parts = assertion.split(" == ")
                if len(parts) == 2:
                    failure["expected"] = parts[1].strip()
                    failure["actual"] = parts[0].strip()
            elif " != " in assertion:
                parts = assertion.split(" != ")
                if len(parts) == 2:
                    failure["actual"] = parts[0].strip()
                    failure["expected"] = f"not {parts[1].strip()}"
    
    return failures


def categorize_error(failure_line: str, context_lines: List[str]) -> str:
    """Categorize error type from failure line and context."""
    context = " ".join(context_lines).lower()
    
    if "import" in context or "importerror" in context or "module" in context:
        return "import_error"
    elif "timeout" in context or "timed out" in context:
        return "timeout"
    elif "assertion" in context or "assert" in failure_line.lower():
        return "assertion_failure"
    elif "attributeerror" in context:
        return "attribute_error"
    elif "keyerror" in context:
        return "key_error"
    elif "typeerror" in context:
        return "type_error"
    elif "valueerror" in context:
        return "value_error"
    else:
        return "unknown_error"


def run_tests_with_reporting(
    logger: logging.Logger,
    verbose: bool = False,
    tests_path: Path = Path("tests"),
    save_output: bool = True,
    output_dir: Optional[Path] = None,
    include_ollama: bool = False,
    include_coverage: bool = True,
    stream_output: bool = True,
    json_results: bool = False,
    show_slow_tests: int = 10,
    slow_threshold: float = 1.0,
) -> int:
    """Run pytest with comprehensive reporting and output saving.
    
    Args:
        logger: Logger instance
        verbose: Show verbose test output
        tests_path: Path to tests directory
        save_output: Whether to save test output to file
        output_dir: Directory to save output (default: scripts/test_reports)
        include_ollama: Include Ollama integration tests
        include_coverage: Include coverage reporting
        stream_output: Stream output in real-time
        json_results: Save structured JSON results
        show_slow_tests: Number of slowest tests to show
        slow_threshold: Threshold in seconds for slow test warning
    
    Returns:
        Exit code: 0=success, 2=tests failed, 3=no tests found
    """
    logger.info("=" * 70)
    logger.info("Running modular test suite with pytest...")
    logger.info("=" * 70)
    
    # Count test files
    test_file_count = get_test_file_count(tests_path)
    logger.debug(f"Found {test_file_count} test modules in {tests_path}")
    
    # Build pytest command with verbose output
    cmd = ["uv", "run", "pytest", "-v", "--tb=short"]
    
    # Add durations to identify slow tests
    cmd.extend(["--durations", str(show_slow_tests)])
    logger.debug(f"Will show {show_slow_tests} slowest tests")
    
    # Add coverage if requested
    if include_coverage:
        cmd.extend(["--cov=src", "--cov-report=term-missing:skip-covered", "--cov-report=html"])
        logger.debug("Coverage reporting enabled")
    
    # By default, run only fast unit tests (skip integration tests that need Ollama)
    explicit_test_files = None
    if not include_ollama:
        # Run all unit tests that don't require Ollama (17 files according to tests/AGENTS.md)
        unit_test_files = [
            "tests/test_config_loader.py",
            "tests/test_parser.py",
            "tests/test_parser_edge_cases.py",
            "tests/test_utils.py",
            "tests/test_helpers_extended.py",
            "tests/test_cleanup.py",
            "tests/test_outline_generator_noninteractive.py",
            "tests/test_content_analysis.py",
            "tests/test_error_collector.py",
            "tests/test_summary_generator.py",
            "tests/test_website_generator.py",
            "tests/test_website_content_loader.py",
            "tests/test_website_templates.py",
            "tests/test_website_scripts.py",
            "tests/test_website_scripts_interaction.py",
            "tests/test_website_styles.py",
            "tests/test_logging_setup.py",
        ]
        cmd.extend(unit_test_files)
        explicit_test_files = unit_test_files
        logger.info(f"Running fast unit tests only ({len(unit_test_files)} files, use --include-ollama for integration tests)")
        logger.debug(f"Unit test files: {', '.join(unit_test_files)}")
    else:
        logger.info("Running all tests including Ollama integration tests")
    
    if verbose:
        cmd.append("-vv")
        logger.debug("Verbose mode enabled")
    
    # Run pytest from project root
    project_root = Path(__file__).parent.parent
    
    # Test discovery
    logger.debug("Discovering tests with pytest --collect-only...")
    discovery_info = discover_tests(cmd, project_root, logger, explicit_test_files=explicit_test_files)
    
    # Handle discovery results with improved logging
    if discovery_info["test_count"] > 0:
        method = discovery_info.get("discovery_method", "unknown")
        logger.info(f"Discovered {discovery_info['test_count']} tests in {discovery_info['test_file_count']} files (method: {method})")
        if discovery_info["skipped_count"] > 0:
            logger.debug(f"  ({discovery_info['skipped_count']} tests will be skipped)")
        
        # Show test files discovered
        if discovery_info["test_files"]:
            files_to_show = discovery_info["test_files"][:10]
            files_display = ", ".join(files_to_show)
            if len(discovery_info["test_files"]) > 10:
                files_display += f" ... and {len(discovery_info['test_files']) - 10} more"
            logger.debug(f"Test files: {files_display}")
        else:
            logger.warning("No test files identified in discovery output")
    elif discovery_info["test_file_count"] > 0:
        # We have files but no test count - this is unusual but not necessarily wrong
        method = discovery_info.get("discovery_method", "unknown")
        logger.info(f"Discovered {discovery_info['test_file_count']} test files (method: {method}, test count unavailable)")
        if discovery_info["test_files"]:
            files_to_show = discovery_info["test_files"][:10]
            files_display = ", ".join(files_to_show)
            if len(discovery_info["test_files"]) > 10:
                files_display += f" ... and {len(discovery_info['test_files']) - 10} more"
            logger.debug(f"Test files: {files_display}")
    else:
        logger.warning("No tests discovered - this may indicate a problem")
        if explicit_test_files:
            logger.warning(f"  Expected {len(explicit_test_files)} test files from command: {', '.join(explicit_test_files)}")
        logger.debug(f"Discovery output (first 500 chars): {discovery_info['discovery_output'][:500]}...")
    
    logger.info(f"Running: {' '.join(cmd)}")
    logger.debug(f"Working directory: {project_root}")
    logger.debug(f"Stream output: {stream_output}")
    logger.debug("-" * 70)
    
    # Run pytest with streaming or capture
    logger.debug("Starting pytest execution...")
    start_time = datetime.now()
    output, exit_code = stream_pytest_output(cmd, project_root, logger, stream_output)
    end_time = datetime.now()
    execution_time = (end_time - start_time).total_seconds()
    
    logger.debug(f"Test execution completed in {execution_time:.2f}s (exit code: {exit_code})")
    
    # Save output to file if requested
    output_file = None
    if save_output:
        if output_dir is None:
            output_dir = Path(__file__).parent / "test_reports"
        output_file = save_test_output(output, output_dir)
        logger.debug(f"Test output saved to: {output_file}")
    
    logger.debug(f"Captured {len(output)} characters of pytest output")
    
    # Parse results
    logger.debug("Parsing test results...")
    stats = parse_pytest_output(output)
    module_stats = parse_test_modules(output, tests_path)
    warnings = extract_warnings(output)
    failures = extract_failures(output)
    slow_tests = parse_durations(output)
    
    logger.debug(f"Parsed: {stats['total']} tests, {len(module_stats)} modules, {len(failures)} failures, {len(warnings)} warnings, {len(slow_tests)} slow tests")
    
    # Build structured results for JSON output
    structured_results = {
        "timestamp": datetime.now().isoformat(),
        "python_version": sys.version,
        "execution_time": execution_time,
        "stats": stats,
        "module_stats": {
            k: {
                "passed": v["passed"],
                "failed": v["failed"],
                "skipped": v["skipped"],
                "errors": v["errors"],
                "avg_duration": v.get("avg_duration", 0.0),
                "total_duration": v.get("total_duration", 0.0),
            }
            for k, v in module_stats.items()
        },
        "slow_tests": [{"test": t[0], "duration": t[1]} for t in slow_tests[:show_slow_tests]],
        "failures": failures,
        "warnings": warnings,
        "discovery": discovery_info,
    }
    
    # Display detailed results
    logger.info("=" * 70)
    logger.info("TEST RESULTS BY MODULE")
    logger.info("=" * 70)
    
    if module_stats:
        for test_file in sorted(module_stats.keys()):
            module_name = Path(test_file).stem
            counts = module_stats[test_file]
            total = counts["passed"] + counts["failed"] + counts["skipped"] + counts["errors"]
            avg_duration = counts.get("avg_duration", 0.0)
            
            status_icon = "✓" if counts["failed"] == 0 and counts["errors"] == 0 else "✗"
            duration_str = f" [{avg_duration:.2f}s avg]" if avg_duration > 0 else ""
            
            logger.info(
                f"{status_icon} {module_name:30s} | "
                f"Total: {total:3d} | "
                f"Passed: {counts['passed']:3d} | "
                f"Failed: {counts['failed']:3d} | "
                f"Skipped: {counts['skipped']:3d}{duration_str}"
            )
    else:
        # If we can't parse module stats, check if pytest had an internal error
        logger.warning("(Detailed module breakdown not available)")
        
        if "INTERNALERROR" in output:
            logger.error("Pytest encountered an internal error!")
            logger.info("\nShowing first 30 lines of error output:")
            error_lines = output.split("\n")[:30]
            for line in error_lines:
                if line.strip():
                    logger.error(f"  {line}")
            logger.info(f"\n💡 Full error details in: {output_file if save_output else 'pytest output'}")
        elif verbose:
            logger.info("\nRaw pytest output:")
            for line in output.split("\n")[:50]:
                if line.strip():
                    logger.info(f"  {line}")
    
    # Display overall summary
    logger.info("=" * 70)
    logger.info("OVERALL TEST SUMMARY")
    logger.info("=" * 70)
    logger.info(f"Total Tests:        {stats['total']:3d}")
    logger.info(f"Passed:             {stats['passed']:3d}")
    logger.info(f"Failed:             {stats['failed']:3d}")
    logger.info(f"Skipped:            {stats['skipped']:3d}")
    logger.info(f"Errors:             {stats['errors']:3d}")
    logger.info(f"Warnings:           {stats['warnings']:3d}")
    logger.info(f"Duration:           {stats['duration']:.2f}s")
    
    if stats['total'] > 0:
        pass_rate = (stats['passed'] / stats['total']) * 100
        logger.info(f"Pass Rate:          {pass_rate:.1f}%")
    
    logger.info("=" * 70)
    
    # Report coverage if available
    if "--cov" in cmd or include_coverage:
        logger.info("")
        logger.info("=" * 70)
        logger.info("CODE COVERAGE SUMMARY")
        logger.info("=" * 70)
        
        # Extract coverage from output
        coverage_lines = []
        in_coverage = False
        
        for line in output.split("\n"):
            if "coverage:" in line.lower() or (in_coverage and "---" in line):
                in_coverage = True
                continue
            if in_coverage and ("TOTAL" in line or line.strip().startswith("src/")):
                coverage_lines.append(line)
            if "Coverage HTML" in line:
                logger.info(line.strip())
                break
        
        if coverage_lines:
            # Show module coverage with color coding
            for line in coverage_lines:
                if "TOTAL" in line:
                    logger.info(line)
                elif line.strip():
                    # Extract coverage percentage
                    parts = line.split()
                    if len(parts) >= 5:
                        try:
                            coverage_pct = int(parts[4].rstrip("%"))
                            if coverage_pct >= 80:
                                status = "✓"
                            elif coverage_pct >= 50:
                                status = "!"
                            else:
                                status = "✗"
                            logger.info(f"{status} {line}")
                        except (ValueError, IndexError):
                            logger.info(f"  {line}")
        else:
            logger.info("(Coverage data not available)")
        
        logger.info("=" * 70)
    
    # Report warnings
    if warnings:
        logger.info("WARNINGS DETAILS")
        logger.info("=" * 70)
        for i, warning in enumerate(warnings[:10], 1):  # Show first 10 warnings
            logger.warning(f"{i}. {warning}")
        if len(warnings) > 10:
            logger.warning(f"... and {len(warnings) - 10} more warnings")
        logger.info("=" * 70)
    
    # Performance metrics - slow tests
    if slow_tests:
        logger.info("")
        logger.info("=" * 70)
        logger.info("PERFORMANCE METRICS - SLOWEST TESTS")
        logger.info("=" * 70)
        
        slow_count = 0
        for test_name, duration in slow_tests[:show_slow_tests]:
            if duration >= slow_threshold:
                slow_count += 1
                status = "⚠" if duration >= slow_threshold * 5 else "!"
                logger.warning(f"{status} {duration:6.2f}s - {test_name}")
        
        if slow_count == 0:
            logger.info(f"All tests completed in under {slow_threshold}s")
        else:
            logger.warning(f"{slow_count} test(s) exceeded {slow_threshold}s threshold")
        
        logger.info("=" * 70)
    
    # Report failures with improved details
    if failures:
        logger.info("")
        logger.info("=" * 70)
        logger.info("FAILURE DETAILS")
        logger.info("=" * 70)
        for i, failure in enumerate(failures, 1):
            error_type = failure.get("error_type", "unknown")
            logger.error(f"\nFailure {i}: {failure['test']}")
            logger.error(f"  Error Type: {error_type}")
            
            if failure.get("assertion"):
                logger.error(f"  Assertion: {failure['assertion']}")
            if failure.get("expected"):
                logger.error(f"  Expected: {failure['expected']}")
            if failure.get("actual"):
                logger.error(f"  Actual: {failure['actual']}")
            
            if failure.get("traceback"):
                logger.error("  Traceback:")
                for tb_line in failure["traceback"][:3]:
                    logger.error(f"    {tb_line}")
                if len(failure["traceback"]) > 3:
                    logger.error(f"    ... ({len(failure['traceback']) - 3} more lines)")
            
            if failure['details']:
                logger.error("  Details:")
                for detail_line in failure['details'][:5]:
                    logger.error(f"    {detail_line}")
                if len(failure['details']) > 5:
                    logger.error(f"    ... ({len(failure['details']) - 5} more lines)")
            
            # Provide actionable guidance based on error type
            if error_type == "import_error":
                logger.info("  💡 Tip: Check that all dependencies are installed (uv pip install -e .)")
            elif error_type == "timeout":
                logger.info("  💡 Tip: This test may need a longer timeout or faster model")
            elif error_type == "assertion_failure":
                logger.info("  💡 Tip: Review the expected vs actual values above")
        
        logger.info("=" * 70)
    
    # Save JSON results if requested
    json_file = None
    if json_results:
        if output_dir is None:
            output_dir = Path(__file__).parent / "test_reports"
        json_file = save_json_results(structured_results, output_dir)
        logger.info(f"✓ JSON results saved to: {json_file}")
        logger.debug(f"JSON contains: {len(structured_results)} top-level keys")
    
    # Final status with improved exit code handling
    exit_code = exit_code
    if exit_code == 0:
        logger.info("✓ ALL TESTS PASSED")
        if warnings:
            logger.warning(f"  (but {len(warnings)} warnings detected)")
        exit_code = 0  # Success
    elif exit_code == 3 or stats['total'] == 0:
        logger.error("✗ PYTEST ERROR: No tests collected or internal error")
        logger.info("💡 This may indicate:")
        logger.info("  - No test files found")
        logger.info("  - Pytest internal error (check saved output)")
        logger.info("  - Import errors in test files")
        if save_output and output_file:
            logger.info(f"💡 Full error details saved to: {output_file}")
        exit_code = 3  # No tests found
    else:
        logger.error(f"✗ TESTS FAILED (exit code {exit_code})")
        if stats['total'] == 0:
            logger.warning("No tests were run - check pytest output for errors")
            exit_code = 3  # No tests found
        else:
            exit_code = 2  # Tests failed
        if not verbose and stats['failed'] > 0:
            logger.info("\n💡 Tip: Rerun with --verbose to see detailed failure output")
        if save_output and output_file:
            logger.info(f"💡 Full output saved to: {output_file}")
    
    logger.info("=" * 70)
    
    # Log exit code meaning
    exit_code_meanings = {
        0: "Success - all tests passed",
        1: "Validation failed",
        2: "Tests failed",
        3: "No tests found or pytest error",
    }
    logger.debug(f"Exit code {exit_code}: {exit_code_meanings.get(exit_code, 'Unknown')}")
    
    return exit_code


def main() -> int:
    args = parse_args()
    
    # Setup logging with file output
    log_file = setup_logging(
        script_name="02_run_tests",
        log_level="INFO",
        console_output=True,
        file_output=True
    )
    
    logger = logging.getLogger("run_tests")
    
    config_dir = args.config_dir
    tests_path = args.tests_path

    log_section_clean(logger, "STAGE 02: VALIDATION & COMPREHENSIVE TESTING", emoji="🧪")
    if log_file:
        logger.info(f"📄 Log file: {log_file}")
    logger.info("")

    # Validation phase
    validation_ok = True
    if not args.skip_validation:
        logger.info("=== Configuration Validation ===")
        validation_ok = validate_config(config_dir, logger) and check_ollama(logger)
        logger.info("")
        
        if not validation_ok:
            logger.error("✗ Validation failed - cannot proceed")
            return 1
    else:
        logger.info("Skipping validation (--skip-validation)")
        logger.info("")

    # Testing phase (runs by default)
    test_rc = 0
    if not args.skip_tests:
        test_rc = run_tests_with_reporting(
            logger,
            args.verbose,
            tests_path,
            save_output=not args.no_save_output,
            output_dir=args.output_dir,
            include_ollama=args.include_ollama,
            include_coverage=not args.no_coverage,
            stream_output=args.stream_output,
            json_results=args.json_results,
            show_slow_tests=args.show_slow_tests,
            slow_threshold=args.slow_threshold,
        )
        logger.info("")
    else:
        logger.info("Skipping tests (--skip-tests)")
        logger.info("")

    # Final summary
    logger.info("=" * 70)
    logger.info("=== STAGE 02 COMPLETE ===")
    logger.info("=" * 70)
    
    # Exit code meanings:
    # 0 = Success
    # 1 = Validation failed
    # 2 = Tests failed
    # 3 = No tests found
    if validation_ok and test_rc == 0:
        logger.info("✓ Validation and testing completed successfully")
        logger.info("  Next step: uv run python3 scripts/03_generate_outline.py")
        return 0
    elif not validation_ok:
        logger.error("✗ Validation failed")
        return 1
    elif test_rc == 3:
        logger.error("✗ No tests found or pytest error")
        logger.info("  Check test discovery and pytest configuration")
        return 3
    else:
        logger.error("✗ Some tests failed")
        logger.info("  Fix failing tests before proceeding to content generation")
        return 2
    
    logger.info("=" * 70)
    logger.info("")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())


