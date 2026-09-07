#!/usr/bin/env python3
"""01 - Environment setup and validation (thin orchestrator).

This script performs comprehensive environment validation including:
- System information reporting
- Dependency checking
- Configuration validation
- Output directory structure
- Ollama service and model availability

All setup logic lives in ``src/setup/environment.py``; this script only
handles argparse, path bootstrap, logging, and the single delegated call.
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

from src.setup.environment import run_environment_setup
from src.utils.logging_setup import setup_logging


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Environment setup and validation.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Basic validation
  %(prog)s --auto-install           # Install dependencies if needed
  %(prog)s --start-ollama           # Start Ollama if not running
  %(prog)s --verbose                # Detailed logging
        """,
    )
    parser.add_argument(
        "--config-dir",
        type=Path,
        default=Path(__file__).parent.parent / "config",
        help="Path to config directory (default: ../config)",
    )
    parser.add_argument(
        "--auto-install",
        action="store_true",
        help="Install project dependencies with uv if needed.",
    )
    parser.add_argument(
        "--start-ollama",
        action="store_true",
        help="Attempt to start ollama serve if not running.",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging output.",
    )
    return parser.parse_args()


def main() -> int:
    """Main entry point for environment setup script.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    args = parse_args()

    # Setup logging with file output
    log_level = "DEBUG" if args.verbose else "INFO"
    log_file = setup_logging(
        script_name="01_setup_environment",
        log_level=log_level,
        console_output=True,
        file_output=True
    )

    logger = logging.getLogger("setup_environment")

    logger.info("")
    logger.info("🔧 EDUCATIONAL COURSE GENERATOR - ENVIRONMENT SETUP")
    logger.info("─" * 60)
    if log_file:
        logger.info(f"📝 Log file: {log_file}")
    logger.info("")

    return run_environment_setup(args, _project_root, logger)


if __name__ == "__main__":
    sys.exit(main())
