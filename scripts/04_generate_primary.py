#!/usr/bin/env python3
"""04 - Primary materials generation (Stage 04).

Generates primary course materials per session:
- lecture.md - Comprehensive instructional content
- lab.md - Laboratory exercise with procedures
- study_notes.md - Concise session summary
- diagram_1.mmd, diagram_2.mmd, ... - Mermaid diagrams (number from config)
- questions.md - Comprehension assessment questions

All materials are generated per session and saved to:
output/modules/module_XX/session_YY/[material].md
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

from src.config.loader import ConfigLoader
from src.generate.orchestration.pipeline import ContentGenerator
from src.utils.logging_setup import setup_logging, log_section_clean, log_info_box, log_status_item


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate primary course materials (lectures, labs, notes, diagrams, questions)."
    )
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument(
        "--all",
        action="store_true",
        help="Generate content for all modules (default if no options specified).",
    )
    group.add_argument(
        "--modules",
        type=int,
        nargs="+",
        metavar="ID",
        help="Generate content for specific module IDs (e.g., --modules 1 2 3).",
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
        help="Path to specific outline JSON (default: most recent in output/outlines/ or scripts/output/outlines/).",
    )
    parser.add_argument(
        "--sessions",
        type=int,
        default=None,
        help="Override number of sessions per module (optional).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    
    # Setup logging with file output
    log_file = setup_logging(
        script_name="04_generate_primary",
        log_level="INFO",
        console_output=True,
        file_output=True
    )
    
    logger = logging.getLogger("generate_primary")

    log_section_clean(logger, "STAGE 04: PRIMARY MATERIALS (Session-Based)", emoji="📚")
    
    logger.info("Generating materials PER SESSION (not per module)")
    logger.info("Output structure: output/modules/module_XX/session_YY/[material].md")
    logger.info("")
    
    try:
        config_loader = ConfigLoader(args.config_dir)
        config_loader.validate_all_configs()
        
        # Get diagram count from config for logging
        diagrams_per_session = config_loader.get_diagrams_per_session()
        
        logger.info("PRIMARY ARTIFACTS GENERATED PER SESSION:")
        logger.info("  1. lecture.md - Comprehensive instructional content")
        logger.info("  2. lab.md - Laboratory exercise with procedures")
        logger.info("  3. study_notes.md - Concise session summary")
        logger.info(f"  4. diagram_1.mmd, diagram_2.mmd, ... (up to {diagrams_per_session} diagrams)")
        logger.info("  5. questions.md - Comprehension assessment questions")
        logger.info("")
        
        config_info = {
            "Diagrams per Session": str(diagrams_per_session),
            "Log File": str(log_file) if log_file else "None"
        }
        log_info_box(logger, "CONFIGURATION", config_info, emoji="⚙️")

        # Validate that outline exists before proceeding
        if args.outline:
            logger.info(f"Using specified outline: {args.outline}")
            if not args.outline.exists():
                logger.error(f"Outline file not found: {args.outline}")
                logger.error("Please provide a valid outline path or omit --outline to use the latest.")
                return 1
            outline_path = args.outline
        else:
            # Find latest outline
            outline_path = config_loader._find_latest_outline_json()
            if not outline_path:
                logger.error("")
                log_status_item(logger, "ERROR", "No outline JSON found", "error")
                logger.error("Searched in:")
                logger.error("  - output/outlines/")
                logger.error("  - scripts/output/outlines/")
                logger.error("  - output/{course_name}/outlines/ (all course-specific directories)")
                logger.error("")
                logger.error("Generate an outline first:")
                logger.error("  uv run python3 scripts/03_generate_outline.py")
                logger.error("")
                return 1
            logger.info(f"Using most recent outline: {outline_path}")
        
        logger.info("")

        # Default to --all if neither --all nor --modules specified
        if args.all or (not args.all and not args.modules):
            module_ids = None
            logger.info("Processing ALL modules from outline")
        else:
            module_ids = args.modules
            logger.info(f"Processing specific modules: {module_ids}")

        generator = ContentGenerator(config_loader)

        # Use new session-based generation
        results = generator.stage2_generate_content_by_session(module_ids)

        successful = sum(1 for r in results if r.get("status") == "success")
        failed = len(results) - successful

        logger.info("\n" + "=" * 80)
        logger.info("PRIMARY MATERIALS COMPLETE")
        logger.info("=" * 80)
        logger.info(f"Total sessions processed: {len(results)}")
        logger.info(f"Successful: {successful}")
        logger.info(f"Failed: {failed}")

        if failed > 0:
            logger.warning("\nFailed sessions:")
            for result in results:
                if result.get("status") == "error":
                    error_msg = result.get('error', 'Unknown error')
                    request_id = result.get('request_id')
                    error_type = result.get('error_type', 'Error')
                    material_types = result.get('material_types_generated', [])
                    
                    logger.warning(
                        f"  - Module {result.get('module_id')} Session {result.get('session_number')}: {error_type}"
                    )
                    if material_types:
                        logger.warning(f"    Generated materials: {', '.join(material_types)}")
                    if request_id:
                        logger.warning(f"    Request ID: {request_id} (filter logs: grep '[{request_id}]' output/logs/*.log)")
                    logger.warning(f"    Error: {error_msg[:200]}")  # Truncate long messages
        
        # Check for critical issues from error collector
        critical_issues = generator.error_collector.get_critical_issues()
        if critical_issues:
            logger.warning("\n" + "=" * 80)
            logger.warning(f"[CRITICAL] {len(critical_issues)} critical issues found requiring attention")
            logger.warning("=" * 80)
            for i, issue in enumerate(critical_issues[:5], 1):
                logger.warning(f"  {i}. {issue.message}")
                if issue.context:
                    logger.warning(f"     Context: {issue.context}")
            if len(critical_issues) > 5:
                logger.warning(f"  ... and {len(critical_issues) - 5} more critical issues")
            logger.warning("=" * 80)

        # Determine exit code and log reason
        exit_code = 0 if failed == 0 and len(critical_issues) == 0 else 1
        
        if exit_code != 0:
            logger.error("\n" + "=" * 80)
            logger.error("EXIT CODE: 1 (FAILURE)")
            logger.error("=" * 80)
            if failed > 0:
                logger.error(f"Reason: {failed} session(s) failed during generation")
                logger.error("Failed sessions:")
                for result in results:
                    if result.get("status") == "error":
                        error_msg = result.get('error', 'Unknown error')
                        request_id = result.get('request_id')
                        error_type = result.get('error_type', 'Error')
                        material_types = result.get('material_types_generated', [])
                        recovery_suggestions = result.get('recovery_suggestions', [])
                        
                        logger.error(
                            f"  - Module {result.get('module_id')} Session {result.get('session_number')}: {error_type}"
                        )
                        if material_types:
                            logger.error(f"    Generated materials: {', '.join(material_types)}")
                        if request_id:
                            logger.error(f"    Request ID: {request_id} (filter logs: grep '[{request_id}]' output/logs/*.log)")
                        logger.error(f"    Error: {error_msg[:200]}")  # Truncate long messages
                        if recovery_suggestions:
                            logger.error("    Recovery suggestions:")
                            for suggestion in recovery_suggestions[:3]:  # Show top 3
                                logger.error(f"      {suggestion}")
            if critical_issues:
                logger.error(f"Reason: {len(critical_issues)} critical issue(s) found requiring attention")
                logger.error("Top critical issues:")
                for i, issue in enumerate(critical_issues[:3], 1):
                    logger.error(f"  {i}. {issue.message}")
                    if issue.context:
                        logger.error(f"     Context: {issue.context}")
            logger.error("")
            logger.error("Troubleshooting:")
            logger.error("  1. Check log file for detailed error messages and request IDs")
            logger.error("  2. Review docs/TROUBLESHOOTING.md for common issues")
            logger.error("  3. For timeout errors, see timeout troubleshooting section")
            logger.error("  4. Use request IDs to filter logs: grep '[REQUEST_ID]' output/logs/*.log")
            logger.error("=" * 80)
        else:
            logger.info("\n" + "=" * 80)
            logger.info("EXIT CODE: 0 (SUCCESS)")
            logger.info("=" * 80)
            logger.info("All sessions processed successfully with no critical issues")
            logger.info("=" * 80)

        return exit_code
    except Exception as exc:  # noqa: BLE001
        logger.error(f"\nERROR: {exc}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

