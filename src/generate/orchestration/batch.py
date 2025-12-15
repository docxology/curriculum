"""Batch processing for multiple course templates.

This module provides functionality to process all available course templates
sequentially through the complete generation pipeline.
"""

import argparse
import logging
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

from src.config.loader import ConfigLoader
from src.utils.logging_setup import log_section_clean, log_info_box, log_operation_context

logger = logging.getLogger(__name__)


class BatchCourseProcessor:
    """Process multiple course templates sequentially.
    
    This class handles batch processing of all available course templates,
    running the complete generation pipeline for each course with proper
    error handling and logging.
    
    Attributes:
        config_dir: Path to configuration directory
        project_root: Path to project root directory
        script_dir: Path to scripts directory
    """
    
    def __init__(self, config_dir: Path, project_root: Optional[Path] = None):
        """Initialize the batch processor.
        
        Args:
            config_dir: Path to configuration directory
            project_root: Path to project root (defaults to config_dir.parent)
        """
        self.config_dir = Path(config_dir).resolve()
        
        if project_root is None:
            # Assume config is in project_root/config
            self.project_root = self.config_dir.parent
        else:
            self.project_root = Path(project_root).resolve()
        
        self.script_dir = self.project_root / "scripts"
        
        logger.debug(f"Initialized BatchCourseProcessor with config_dir: {self.config_dir}")
        logger.debug(f"Project root: {self.project_root}, Script dir: {self.script_dir}")
    
    def list_available_courses(self) -> List[Dict[str, Any]]:
        """Get list of all available course templates.
        
        Returns:
            List of course dictionaries with name, filename, and course_info
        """
        config_loader = ConfigLoader(self.config_dir)
        courses = config_loader.list_available_courses()
        logger.info(f"Found {len(courses)} course template(s) for batch processing")
        return courses
    
    def _run_script(
        self,
        script_name: str,
        course_name: str,
        args: argparse.Namespace,
        logger_instance: logging.Logger
    ) -> Tuple[int, str]:
        """Run a script with course-specific arguments.
        
        Args:
            script_name: Name of script to run (e.g., '03_generate_outline.py')
            course_name: Course template name to use (only passed to scripts that support --course flag)
            args: Parsed command-line arguments
            logger_instance: Logger instance for logging
            
        Returns:
            Tuple of (exit_code, stderr_output)
            
        Note:
            Only `03_generate_outline.py` receives `--no-interactive` and `--course` flags.
            Other scripts discover course context automatically from outline JSON metadata.
        """
        script_path = self.script_dir / script_name
        if not script_path.exists():
            logger_instance.error(f"Script not found: {script_path}")
            return 1, ""
        
        cmd = [sys.executable, str(script_path)]
        
        # Always forward config-dir
        cmd.extend(['--config-dir', str(self.config_dir)])
        
        # Only add --no-interactive and --course for scripts that support them
        # Currently only 03_generate_outline.py supports these flags
        if script_name == '03_generate_outline.py':
            cmd.append('--no-interactive')
            cmd.extend(['--course', course_name])
        
        # Forward other relevant arguments
        if script_name == '02_run_tests.py' and args.run_tests:
            cmd.append('--run-tests')
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
        
        logger_instance.debug(f"Running: {' '.join(str(c) for c in cmd)}")
        
        try:
            # Capture output for better error reporting
            result = subprocess.run(
                cmd,
                capture_output=True,  # Capture for error analysis
                text=True,
                check=False  # Don't raise exception on non-zero exit
            )
            
            # If script failed, log additional context
            if result.returncode != 0:
                logger_instance.error(f"Script {script_name} exited with code {result.returncode}")
                
                # Log stderr if available (first 500 chars to avoid spam)
                if result.stderr:
                    stderr_preview = result.stderr[:500]
                    logger_instance.error(f"Script stderr (first 500 chars): {stderr_preview}")
                    if len(result.stderr) > 500:
                        logger_instance.error(f"... ({len(result.stderr) - 500} more characters)")
                
                # Try to find and read last lines of log file for context
                try:
                    # Look for log file in scripts/output/logs/
                    log_pattern = script_name.replace('.py', '') + '_*.log'
                    log_dir = self.project_root / "scripts" / "output" / "logs"
                    if log_dir.exists():
                        log_files = sorted(log_dir.glob(log_pattern), key=lambda p: p.stat().st_mtime, reverse=True)
                        if log_files:
                            latest_log = log_files[0]
                            try:
                                # Read last 20 lines of log file
                                with open(latest_log, 'r', encoding='utf-8') as f:
                                    lines = f.readlines()
                                    if lines:
                                        logger_instance.error(f"Last 10 lines from log file ({latest_log.name}):")
                                        for line in lines[-10:]:
                                            logger_instance.error(f"  {line.rstrip()}")
                            except Exception:
                                pass  # Ignore errors reading log file
                except Exception:
                    pass  # Ignore errors finding log file
            
            return result.returncode, result.stderr or ""
        except Exception as e:
            error_msg = str(e)
            logger_instance.error(f"Error running {script_name}: {error_msg}", exc_info=True)
            # Re-raise to be caught by caller for proper error reporting
            raise
    
    def process_all_courses_for_outline(
        self,
        args: argparse.Namespace,
        logger_instance: Optional[logging.Logger] = None
    ) -> Dict[str, Any]:
        """Process all courses for outline generation only (Stage 03).
        
        Args:
            args: Parsed command-line arguments
            logger_instance: Logger instance (defaults to module logger)
            
        Returns:
            Dictionary with summary:
            - total: Total number of courses
            - successful: List of successful course names
            - failed: List of failed courses with error messages
            - summary: Human-readable summary string
        """
        if logger_instance is None:
            logger_instance = logger
        
        courses = self.list_available_courses()
        
        if not courses:
            logger_instance.warning("No course templates found for batch processing")
            return {
                'total': 0,
                'successful': [],
                'failed': [],
                'summary': 'No courses to process'
            }
        
        logger_instance.info("")
        log_section_clean(
            logger_instance,
            f"BATCH PROCESSING: Outline Generation for {len(courses)} Courses",
            emoji="📝"
        )
        
        successful = []
        failed = []
        
        for idx, course in enumerate(courses, start=1):
            course_name = course['name']
            course_display_name = course['course_info'].get('name', course_name)
            
            logger_instance.info("")
            logger_instance.info("=" * 80)
            logger_instance.info(f"Course {idx}/{len(courses)}: {course_display_name}")
            logger_instance.info(f"Template: {course_name}")
            logger_instance.info("=" * 80)
            
            try:
                rc, stderr = self._run_script('03_generate_outline.py', course_name, args, logger_instance)
                
                if rc == 0:
                    logger_instance.info(f"✅ Successfully generated outline for: {course_display_name}")
                    successful.append(course_name)
                else:
                    # Try to extract error message from stderr if available
                    error_msg = f"Exit code {rc}"
                    if stderr:
                        # Try to extract exception message from stderr
                        # Look for "Exception: ..." or "Error: ..." patterns
                        import re
                        exception_match = re.search(r'Exception:\s*(.+?)(?:\n|$)', stderr, re.MULTILINE)
                        if exception_match:
                            error_msg = exception_match.group(1).strip()
                        elif "Traceback" in stderr:
                            # Extract the last line which usually has the exception
                            lines = stderr.strip().split('\n')
                            for line in reversed(lines):
                                if line.strip() and not line.strip().startswith('File'):
                                    error_msg = line.strip()
                                    break
                    logger_instance.error(f"❌ Failed to generate outline for: {course_display_name} ({error_msg})")
                    failed.append({'name': course_name, 'error': error_msg})
            
            except Exception as e:
                error_msg = str(e)
                logger_instance.error(f"❌ Exception processing {course_display_name}: {error_msg}", exc_info=True)
                failed.append({'name': course_name, 'error': error_msg})
        
        # Summary
        summary = self._generate_summary(len(courses), successful, failed, "outline generation")
        
        logger_instance.info("")
        log_info_box(
            logger_instance,
            "BATCH PROCESSING SUMMARY",
            {
                "Total Courses": str(len(courses)),
                "Successful": str(len(successful)),
                "Failed": str(len(failed))
            },
            emoji="📊"
        )
        
        if successful:
            logger_instance.info(f"✅ Successful courses: {', '.join(successful)}")
        if failed:
            logger_instance.warning(f"❌ Failed courses:")
            for fail in failed:
                logger_instance.warning(f"  • {fail['name']}: {fail['error']}")
        
        return {
            'total': len(courses),
            'successful': successful,
            'failed': failed,
            'summary': summary
        }
    
    def process_all_courses_full_pipeline(
        self,
        args: argparse.Namespace,
        logger_instance: Optional[logging.Logger] = None
    ) -> Dict[str, Any]:
        """Process all courses through complete 6-stage pipeline.
        
        Args:
            args: Parsed command-line arguments
            logger_instance: Logger instance (defaults to module logger)
            
        Returns:
            Dictionary with summary:
            - total: Total number of courses
            - successful: List of successful course names
            - failed: List of failed courses with error messages
            - summary: Human-readable summary string
        """
        if logger_instance is None:
            logger_instance = logger
        
        courses = self.list_available_courses()
        
        if not courses:
            logger_instance.warning("No course templates found for batch processing")
            return {
                'total': 0,
                'successful': [],
                'failed': [],
                'summary': 'No courses to process'
            }
        
        logger_instance.info("")
        log_section_clean(
            logger_instance,
            f"BATCH PROCESSING: Full Pipeline for {len(courses)} Courses",
            emoji="🚀"
        )
        
        successful = []
        failed = []
        
        # Stage names for logging
        stages = [
            ('01_setup_environment.py', 'Environment Setup', '🔧'),
            ('02_run_tests.py', 'Validation & Testing', '🧪'),
            ('03_generate_outline.py', 'Outline Generation', '📑'),
            ('04_generate_primary.py', 'Primary Materials', '📚'),
            ('05_generate_secondary.py', 'Secondary Materials', '📖'),
            ('06_website.py', 'Website Generation', '🌐'),
        ]
        
        for idx, course in enumerate(courses, start=1):
            course_name = course['name']
            course_display_name = course['course_info'].get('name', course_name)
            
            logger_instance.info("")
            logger_instance.info("=" * 80)
            logger_instance.info(f"Course {idx}/{len(courses)}: {course_display_name}")
            logger_instance.info(f"Template: {course_name}")
            logger_instance.info("=" * 80)
            
            course_failed = False
            failed_stages = []
            
            for stage_script, stage_name, emoji in stages:
                # Skip stages if requested
                if stage_script == '01_setup_environment.py' and args.skip_setup:
                    logger_instance.info(f"⏭️  Skipping {stage_name}")
                    continue
                if stage_script == '02_run_tests.py' and args.skip_validation:
                    logger_instance.info(f"⏭️  Skipping {stage_name}")
                    continue
                if stage_script == '03_generate_outline.py' and args.skip_outline:
                    logger_instance.info(f"⏭️  Skipping {stage_name}")
                    continue
                if stage_script == '04_generate_primary.py' and args.skip_primary:
                    logger_instance.info(f"⏭️  Skipping {stage_name}")
                    continue
                if stage_script == '05_generate_secondary.py' and args.skip_secondary:
                    logger_instance.info(f"⏭️  Skipping {stage_name}")
                    continue
                if stage_script == '06_website.py' and args.skip_website:
                    logger_instance.info(f"⏭️  Skipping {stage_name}")
                    continue
                
                logger_instance.info("")
                log_section_clean(logger_instance, f"{stage_name} ({course_display_name})", emoji=emoji)
                
                # Add operation context for better logging
                log_operation_context(
                    logger_instance,
                    module=f"{course_name}_{stage_script.replace('.py', '')}",
                    session=f"batch_processing"
                )
                
                try:
                    rc, stderr = self._run_script(stage_script, course_name, args, logger_instance)
                    
                    if rc == 0:
                        logger_instance.info(f"✅ {stage_name} complete for {course_display_name}")
                    else:
                        error_msg = f"Exit code {rc} in {stage_name}"
                        logger_instance.error(f"❌ {error_msg}")
                        failed_stages.append(stage_name)
                        course_failed = True
                        # Continue with next stage even if one fails
                
                except Exception as e:
                    error_msg = f"Exception in {stage_name}: {str(e)}"
                    logger_instance.error(f"❌ {error_msg}", exc_info=True)
                    failed_stages.append(stage_name)
                    course_failed = True
            
            if course_failed:
                error_msg = f"Failed stages: {', '.join(failed_stages)}"
                logger_instance.error(f"❌ Course {course_display_name} completed with errors: {error_msg}")
                failed.append({'name': course_name, 'error': error_msg})
            else:
                logger_instance.info(f"✅ Successfully completed full pipeline for: {course_display_name}")
                successful.append(course_name)
        
        # Summary
        summary = self._generate_summary(len(courses), successful, failed, "full pipeline")
        
        logger_instance.info("")
        log_info_box(
            logger_instance,
            "BATCH PROCESSING SUMMARY",
            {
                "Total Courses": str(len(courses)),
                "Successful": str(len(successful)),
                "Failed": str(len(failed))
            },
            emoji="📊"
        )
        
        if successful:
            logger_instance.info(f"✅ Successful courses: {', '.join(successful)}")
        if failed:
            logger_instance.warning(f"❌ Failed courses:")
            for fail in failed:
                logger_instance.warning(f"  • {fail['name']}: {fail['error']}")
        
        return {
            'total': len(courses),
            'successful': successful,
            'failed': failed,
            'summary': summary
        }
    
    def _generate_summary(
        self,
        total: int,
        successful: List[str],
        failed: List[Dict[str, str]],
        operation: str
    ) -> str:
        """Generate human-readable summary string.
        
        Args:
            total: Total number of courses
            successful: List of successful course names
            failed: List of failed courses with error info
            operation: Description of operation (e.g., "outline generation")
            
        Returns:
            Summary string
        """
        if total == 0:
            return "No courses to process"
        
        success_count = len(successful)
        fail_count = len(failed)
        
        summary_parts = [
            f"Processed {total} course(s) for {operation}",
            f"{success_count} successful",
            f"{fail_count} failed"
        ]
        
        return ". ".join(summary_parts) + "."




