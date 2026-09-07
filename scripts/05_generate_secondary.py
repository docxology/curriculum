#!/usr/bin/env python3
"""05 - Secondary materials generation (Stage 05) - thin orchestrator.

Secondary-material logic lives in ``src/generate/stages/secondary.py``; this
script only handles argparse, path bootstrap, logging, and the single
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

from src.generate.stages.secondary import SECONDARY_TYPES_DEFAULT, run_secondary_generation
from src.utils.logging_setup import setup_logging, log_section_clean, log_info_box


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate secondary materials (applications, visualizations, etc.) per session. "
                    "Defaults to all sessions in all modules if none specified.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate for all sessions in all modules (default if no args provided)
  %(prog)s
  %(prog)s --all

  # Generate for sessions in specific modules only
  %(prog)s --modules 1 2 3

  # Generate specific types only
  %(prog)s --all --types application visualization
        """
    )
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument(
        "--all",
        action="store_true",
        help="Generate secondary materials for all sessions in all modules (default behavior).",
    )
    group.add_argument(
        "--modules",
        type=int,
        nargs="+",
        metavar="ID",
        help="Generate for sessions in specific module IDs (e.g., --modules 1 2 3).",
    )
    parser.add_argument(
        "--types",
        type=str,
        nargs="+",
        default=SECONDARY_TYPES_DEFAULT,
        metavar="TYPE",
        help="Secondary material types to generate (default: all).",
    )
    parser.add_argument(
        "--config-dir",
        type=Path,
        default=Path(__file__).parent.parent / "config",
        help="Path to config directory (default: ../config).",
    )
    parser.add_argument(
        "--outline",
        type=Path,
        default=None,
        help="Path to specific outline file (default: most recent in output/outlines/ or scripts/output/outlines/).",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate generated content for quality issues.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be generated without calling LLM.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    # Setup logging with file output
    log_file = setup_logging(
        script_name="05_generate_secondary",
        log_level="INFO",
        console_output=True,
        file_output=True
    )

    logger = logging.getLogger("generate_secondary")

    log_section_clean(logger, "STAGE 05: SECONDARY MATERIALS (Session-Level Synthesis)", emoji="🔬")

    logger.info("Generating materials PER SESSION (with full session context)")
    logger.info("Reading all content from: [course-specific]/modules/module_XX/session_YY/")
    logger.info("Output structure: [course-specific]/modules/module_XX/session_YY/[type].md")
    logger.info("")
    logger.info("SECONDARY TYPES GENERATED PER SESSION:")
    logger.info("  1. application.md - Real-world applications and case studies")
    logger.info("  2. extension.md - Advanced topics beyond core curriculum")
    logger.info("  3. visualization.mmd - Additional diagrams and concept maps (Mermaid format)")
    logger.info("  4. integration.md - Cross-module connections and synthesis")
    logger.info("  5. investigation.md - Research questions and experiments")
    logger.info("  6. open_questions.md - Current scientific debates and frontiers")
    logger.info("")

    config_info = {
        "Content Validation": "ENABLED" if args.validate else "DISABLED",
        "Dry Run": "ENABLED (no LLM calls)" if args.dry_run else "DISABLED",
        "Log File": str(log_file) if log_file else "None"
    }
    log_info_box(logger, "CONFIGURATION", config_info, emoji="⚙️")

    return run_secondary_generation(args, logger)


if __name__ == "__main__":
    sys.exit(main())
