#!/usr/bin/env python3
"""02 - Configuration validation and pytest testing (thin orchestrator).

All validation/testing/reporting logic lives in ``src/validation/runner.py``;
this script only handles argparse, path bootstrap, logging, and the single
delegated call.

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
import logging

from src.validation.runner import run_validation_and_tests
from src.utils.logging_setup import setup_logging, log_section_clean


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
        help="Directory to save test reports (default: output/test_reports)",
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

    log_section_clean(logger, "STAGE 02: VALIDATION & COMPREHENSIVE TESTING", emoji="🧪")
    if log_file:
        logger.info(f"📄 Log file: {log_file}")
    logger.info("")

    return run_validation_and_tests(args, _project_root, logger)


if __name__ == "__main__":
    sys.exit(main())
