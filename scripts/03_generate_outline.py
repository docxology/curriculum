#!/usr/bin/env python3
"""03 - Interactive outline generation (Stage 1) - thin orchestrator.

Outline workflow logic lives in ``src/generate/stages/outline_workflow.py``;
this script only handles argparse, path bootstrap, logging, and the single
delegated call.
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

from src.generate.stages.outline_workflow import run_outline_generation
from src.utils.logging_setup import setup_logging, log_section_clean, log_info_box


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate course outline (interactive by default)."
    )
    parser.add_argument(
        "--config-dir",
        type=Path,
        default=Path(__file__).parent.parent / "config",
        help="Path to config directory (default: ../config)",
    )
    parser.add_argument(
        "--no-interactive",
        action="store_true",
        help="Disable interactive prompts and use config defaults.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional explicit output path for outline.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Override base output directory (default: from output_config.yaml).",
    )
    parser.add_argument(
        "--clear-output",
        action="store_true",
        help="Clear output directory before generation.",
    )
    parser.add_argument(
        "--course",
        type=str,
        default=None,
        help="Course template name to use from config/courses/ (e.g., 'biology', 'chemistry').",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    # Setup logging with file output
    log_file = setup_logging(
        script_name="03_generate_outline",
        log_level="INFO",
        console_output=True,
        file_output=True
    )

    logger = logging.getLogger("generate_outline")

    log_section_clean(logger, "STAGE 03: OUTLINE GENERATION", emoji="📝")

    config_info = {
        "Config Directory": str(args.config_dir),
        "Log File": str(log_file) if log_file else "None"
    }
    log_info_box(logger, "CONFIGURATION", config_info, emoji="⚙️")

    return run_outline_generation(args, _project_root, logger)


if __name__ == "__main__":
    sys.exit(main())
