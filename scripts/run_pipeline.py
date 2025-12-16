#!/usr/bin/env python3
"""Run the complete educational course generation pipeline.

This script orchestrates all 6 stages by calling numbered scripts in sequence.
"""

import sys
from pathlib import Path

# Add project root to Python path to allow imports when run directly
# This enables running: python scripts/run_pipeline.py (from any directory)
# or: python3 run_pipeline.py (from scripts directory)
_script_dir = Path(__file__).resolve().parent
_project_root = _script_dir.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

import argparse
import logging
import os
import subprocess
from src.config.loader import ConfigLoader
from src.generate.orchestration.batch import BatchCourseProcessor
from src.utils.course_selection import select_course_template, GENERATE_ALL_COURSES
from src.utils.logging_setup import (
    setup_logging, 
    log_section_clean, 
    log_info_box,
)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run complete educational course generation pipeline (all 6 stages)"
    )
    
    # Skip flags for each stage
    parser.add_argument(
        '--skip-setup',
        action='store_true',
        help='Skip Stage 01 (environment setup)'
    )
    parser.add_argument(
        '--skip-validation',
        action='store_true',
        help='Skip Stage 02 (validation/testing)'
    )
    parser.add_argument(
        '--skip-outline',
        action='store_true',
        help='Skip Stage 03 (outline generation)'
    )
    parser.add_argument(
        '--skip-primary',
        action='store_true',
        help='Skip Stage 04 (primary materials)'
    )
    parser.add_argument(
        '--skip-secondary',
        action='store_true',
        help='Skip Stage 05 (secondary materials)'
    )
    parser.add_argument(
        '--skip-website',
        action='store_true',
        help='Skip Stage 06 (website generation)'
    )
    
    # Module selection (passed to stages 04 and 05)
    parser.add_argument(
        '--modules',
        type=int,
        nargs='+',
        metavar='ID',
        help='Only process specific module IDs (for stages 04 and 05)'
    )
    
    # Secondary material types (passed to stage 05)
    parser.add_argument(
        '--types',
        type=str,
        nargs='+',
        metavar='TYPE',
        help='Secondary material types to generate (for stage 05)'
    )
    
    # Config directory (passed to all stages)
    parser.add_argument(
        '--config-dir',
        type=Path,
        default=_project_root / "config",
        help=f'Path to config directory (default: {_project_root / "config"})'
    )
    
    # Other options
    parser.add_argument(
        '--no-interactive',
        action='store_true',
        help='Disable interactive prompts in stage 03'
    )
    parser.add_argument(
        '--run-tests',
        action='store_true',
        help='Run pytest in stage 02'
    )
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level (default: INFO)'
    )
    parser.add_argument(
        '--language',
        type=str,
        default=None,
        help='Language for course content generation (e.g., "English", "Spanish", "French"). Defaults to config value or prompts for input.'
    )
    parser.add_argument(
        '--course',
        type=str,
        default=None,
        help='Course template name to use from config/courses/ (e.g., "biology", "chemistry"). Passed to stage 03.'
    )
    
    return parser.parse_args()


def run_script(script_name: str, args: argparse.Namespace, logger: logging.Logger) -> int:
    """Run a numbered script and return exit code.
    
    Args:
        script_name: Name of script to run (e.g., '01_setup_environment.py')
        args: Parsed command-line arguments
        logger: Logger instance
        
    Returns:
        Exit code from the script
    """
    script_path = Path(__file__).parent / script_name
    cmd = [sys.executable, str(script_path)]
    
    # Always forward config-dir to all scripts (required)
    cmd.extend(['--config-dir', str(args.config_dir)])
    logger.debug(f"Config directory passed to {script_name}: {args.config_dir}")
    
    # Script-specific argument forwarding
    if script_name == '02_run_tests.py':
        # Tests run by default in 02_run_tests.py, no --run-tests argument needed
        # If --run-tests was passed, it's ignored (backward compatibility)
        pass
    
    elif script_name == '03_generate_outline.py':
        if args.no_interactive:
            cmd.append('--no-interactive')
        if args.course:
            cmd.extend(['--course', args.course])
    
    elif script_name == '04_generate_primary.py':
        if args.modules:
            cmd.append('--modules')
            cmd.extend([str(m) for m in args.modules])
        else:
            cmd.append('--all')
    
    elif script_name == '05_generate_secondary.py':
        if args.modules:
            cmd.append('--modules')
            cmd.extend([str(m) for m in args.modules])
        else:
            cmd.append('--all')
        
        if args.types:
            cmd.extend(['--types'] + args.types)
    
    elif script_name == '06_website.py':
        # No special arguments needed for website script
        pass
    
    logger.info(f"Running: {' '.join(str(c) for c in cmd)}")
    
    result = subprocess.run(cmd)
    return result.returncode


def main() -> int:
    """Main entry point."""
    args = parse_args()
    
    # Setup basic logging first (before config check) to ensure we can log errors
    # This allows us to log the config directory error properly
    basic_log_file = setup_logging(
        script_name="run_pipeline",
        log_level=args.log_level,
        console_output=True,
        file_output=True
    )
    logger = logging.getLogger(__name__)
    
    # Resolve config directory to absolute path
    config_dir = Path(args.config_dir).resolve()
    if not config_dir.exists():
        logger.error(f"Config directory not found: {config_dir}")
        logger.error("Please provide a valid --config-dir path or ensure config/ directory exists")
        return 1
    
    # Log file location (already set up above)
    log_file = basic_log_file
    
    # Banner
    logger.info("")
    logger.info("🚀 EDUCATIONAL COURSE GENERATOR - Full Pipeline")
    logger.info("─" * 60)
    if log_file:
        logger.info(f"📝 Log file: {log_file}")
    logger.info("")
    
    # Log configuration information prominently
    log_info_box(
        logger,
        "Configuration",
        {
            "Config Directory": str(config_dir),
            "Project Root": str(_project_root),
            "Python Executable": sys.executable
        },
        emoji="⚙️"
    )
    
    # Update args.config_dir with resolved path
    args.config_dir = config_dir
    
    # Language selection (only if provided via command line)
    # If not provided, it will be prompted in the outline generation phase
    if args.language:
        logger.info(f"Using language from command line: {args.language}")
        # Set environment variable for subprocess scripts and ConfigLoader
        os.environ["COURSE_LANGUAGE"] = args.language
    
    stages_run = 0
    stages_failed = 0
    
    # Stage 01: Environment Setup
    if not args.skip_setup:
        log_section_clean(logger, "STAGE 01: Environment Setup", emoji="🔧")
        rc = run_script('01_setup_environment.py', args, logger)
        stages_run += 1
        if rc != 0:
            logger.error(f"❌ Stage 01 failed with exit code {rc}")
            stages_failed += 1
            return rc
        logger.info("✅ Stage 01 complete")
    else:
        logger.info("⏭️  Skipping Stage 01 (environment setup)")
    
    # Stage 02: Validation and Testing
    if not args.skip_validation:
        log_section_clean(logger, "STAGE 02: Validation & Testing", emoji="🧪")
        rc = run_script('02_run_tests.py', args, logger)
        stages_run += 1
        if rc != 0:
            logger.error(f"❌ Stage 02 failed with exit code {rc}")
            stages_failed += 1
            return rc
        logger.info("✅ Stage 02 complete")
    else:
        logger.info("⏭️  Skipping Stage 02 (validation/testing)")
    
    # Course selection (if not specified and not in non-interactive mode)
    # This happens after validation/testing to ensure system is ready
    selected_course = args.course
    if not selected_course and not args.no_interactive:
        logger.info("")
        config_loader = ConfigLoader(config_dir)
        selected_course = select_course_template(config_loader, logger)
    
    # Handle "generate all courses" option
    if selected_course == GENERATE_ALL_COURSES:
        logger.info("")
        log_section_clean(logger, "BATCH MODE: Full Pipeline for All Courses", emoji="🚀")
        batch_processor = BatchCourseProcessor(config_dir, _project_root)
        summary = batch_processor.process_all_courses_full_pipeline(args, logger)
        
        logger.info("")
        logger.info("=" * 80)
        logger.info("BATCH PROCESSING COMPLETE")
        logger.info("=" * 80)
        logger.info(summary['summary'])
        
        # Return appropriate exit code
        return 0 if len(summary['failed']) == 0 else 1
    
    # Update args.course if selected interactively
    if selected_course and selected_course != GENERATE_ALL_COURSES:
        args.course = selected_course
    
    # Stage 03: Outline Generation
    if not args.skip_outline:
        log_section_clean(logger, "STAGE 03: Outline Generation", emoji="📑")
        rc = run_script('03_generate_outline.py', args, logger)
        stages_run += 1
        if rc != 0:
            logger.error(f"❌ Stage 03 failed with exit code {rc}")
            stages_failed += 1
            return rc
        logger.info("✅ Stage 03 complete")
    else:
        logger.info("⏭️  Skipping Stage 03 (outline generation)")
    
    # Stage 04: Primary Materials
    if not args.skip_primary:
        log_section_clean(logger, "STAGE 04: Primary Materials Generation", emoji="📚")
        rc = run_script('04_generate_primary.py', args, logger)
        stages_run += 1
        if rc != 0:
            logger.error(f"❌ Stage 04 failed with exit code {rc}")
            stages_failed += 1
            # Don't return here - allow secondary to run even if primary fails
        else:
            logger.info("✅ Stage 04 complete")
    else:
        logger.info("⏭️  Skipping Stage 04 (primary materials)")
    
    # Stage 05: Secondary Materials
    if not args.skip_secondary:
        log_section_clean(logger, "STAGE 05: Secondary Materials Generation", emoji="📖")
        rc = run_script('05_generate_secondary.py', args, logger)
        stages_run += 1
        if rc != 0:
            logger.error(f"❌ Stage 05 failed with exit code {rc}")
            stages_failed += 1
        else:
            logger.info("✅ Stage 05 complete")
    else:
        logger.info("⏭️  Skipping Stage 05 (secondary materials)")
    
    # Stage 06: Website Generation
    if not args.skip_website:
        log_section_clean(logger, "STAGE 06: Website Generation", emoji="🌐")
        rc = run_script('06_website.py', args, logger)
        stages_run += 1
        if rc != 0:
            logger.error(f"❌ Stage 06 failed with exit code {rc}")
            stages_failed += 1
        else:
            logger.info("✅ Stage 06 complete")
    else:
        logger.info("⏭️  Skipping Stage 06 (website generation)")
    
    # Final summary
    logger.info("")
    logger.info("═" * 80)
    logger.info("[FINAL SUMMARY] Pipeline Execution Complete")
    logger.info("═" * 80)
    logger.info(f"  • Stages run: {stages_run}")
    logger.info(f"  • Stages failed: {stages_failed}")
    
    if stages_failed == 0:
        logger.info("  [SUCCESS] All stages completed successfully!")
        logger.info("")
        logger.info("  Next steps:")
        logger.info("    - Review generated content in output/ directory")
        logger.info("    - Check stage summaries above for any [NEEDS REVIEW] or [CRITICAL] issues")
        logger.info("    - Review log file for detailed validation information")
    else:
        logger.warning(f"  [WARNING] {stages_failed} stage(s) failed")
        logger.warning("")
        logger.warning("  Please review:")
        logger.warning("    - Error messages above for failed stages")
        logger.warning("    - Stage summaries for validation issues")
        logger.warning("    - Log file for detailed error information")
    
    logger.info("═" * 80)
    logger.info("")
    
    if log_file:
        logger.info(f"📝 Full log available at: {log_file}")
        logger.info("")
    
    return 1 if stages_failed > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
