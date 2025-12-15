#!/usr/bin/env python3
"""05 - Secondary materials generation (Stage 05).

Generates secondary course materials per session:
- application.md - Real-world applications and case studies
- extension.md - Advanced topics beyond core curriculum
- visualization.mmd - Additional diagrams and concept maps (Mermaid format)
- integration.md - Cross-module connections and synthesis
- investigation.md - Research questions and experiments
- open_questions.md - Current scientific debates and frontiers

All materials are generated per session and saved to:
output/modules/module_XX/session_YY/[type].md (or .mmd for visualization)
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
import re
from typing import Dict, List, Any

from src.config.loader import ConfigLoader, ConfigurationError
from src.llm.client import OllamaClient, LLMError
from src.utils.helpers import slugify
from src.utils.logging_setup import setup_logging, log_section_clean, log_info_box
from src.utils.error_collector import ErrorCollector
from src.utils.summary_generator import generate_stage_summary

SECONDARY_TYPES_DEFAULT = [
    "application",
    "extension",
    "visualization",
    "integration",
    "investigation",
    "open_questions",
]


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


def find_latest_outline(explicit_path: Path = None) -> str:
    """Find and return latest outline text, searching multiple locations.
    
    Args:
        explicit_path: Optional explicit path to outline file
        
    Returns:
        Outline text content (markdown or empty string if not found)
    """
    # If explicit path provided, use it
    if explicit_path:
        if explicit_path.exists():
            try:
                return explicit_path.read_text(encoding="utf-8")
            except Exception:
                return ""
        return ""
    
    # Search multiple locations (consistent with script 04 / pipeline behavior)
    search_paths = [
        Path("output") / "outlines",
        Path("scripts") / "output" / "outlines",
    ]
    
    # Also search in all course-specific directories (for batch processing)
    base_output_dir = Path("output")
    if base_output_dir.exists():
        for course_dir in base_output_dir.iterdir():
            if course_dir.is_dir() and not course_dir.name.startswith('.'):
                course_outlines = course_dir / "outlines"
                if course_outlines.exists() and course_outlines not in search_paths:
                    search_paths.append(course_outlines)
    
    scripts_output_dir = Path("scripts") / "output"
    if scripts_output_dir.exists():
        for course_dir in scripts_output_dir.iterdir():
            if course_dir.is_dir() and not course_dir.name.startswith('.'):
                course_outlines = course_dir / "outlines"
                if course_outlines.exists() and course_outlines not in search_paths:
                    search_paths.append(course_outlines)
    
    all_outlines = []
    for search_dir in search_paths:
        if search_dir.exists():
            markdown_files = list(search_dir.glob("course_outline_*.md"))
            all_outlines.extend(markdown_files)
    
    if not all_outlines:
        return ""
    
    # Get most recent by modification time
    latest = max(all_outlines, key=lambda p: p.stat().st_mtime)
    
    try:
        return latest.read_text(encoding="utf-8")
    except Exception:
        return ""


def build_prompt(
    module: Dict[str, Any],
    outline_text: str,
    prompt_cfg: Dict[str, str],
    material_type: str,
    subject: str = "general education",
) -> str:
    template = prompt_cfg.get("template", "")
    return template.format(
        module_name=module.get("name", ""),
        module_id=module.get("id", ""),
        subject=subject,
        outline=outline_text,
        material_type=material_type,
    )


def load_session_content(session_dir: Path) -> str:
    """Load all existing content from a session folder.
    
    Args:
        session_dir: Path to session directory
        
    Returns:
        Combined text of all session materials
    """
    if not session_dir.exists():
        return ""
    
    combined = []
    
    # Read primary materials in order
    primary_files = ["lecture.md", "lab.md", "study_notes.md", "questions.md"]
    for material_file in primary_files:
        material_path = session_dir / material_file
        if material_path.exists():
            try:
                content = material_path.read_text(encoding="utf-8")
                combined.append(f"## {material_file.replace('.md', '').replace('_', ' ').title()}\n\n")
                combined.append(content)
                combined.append("\n\n")
            except Exception:
                pass
    
    # Read all diagram files
    diagram_files = sorted(session_dir.glob("diagram_*.mmd"))
    for diagram_path in diagram_files:
        try:
            content = diagram_path.read_text(encoding="utf-8")
            combined.append(f"## {diagram_path.name}\n\n")
            combined.append("```mermaid\n")
            combined.append(content)
            combined.append("\n```\n\n")
        except Exception:
            pass
    
    return "\n".join(combined)


def generate_secondary_for_session(
    module: Dict[str, Any],
    session: Dict[str, Any],
    session_dir: Path,
    types: List[str],
    config_loader: ConfigLoader,
    llm_client: OllamaClient,
    outline_text: str,
    logger: logging.Logger,
    error_collector: ErrorCollector = None,
) -> Dict[str, Path]:
    """Generate secondary materials for a specific session.
    
    Args:
        module: Module dictionary from outline
        session: Session dictionary from outline
        session_dir: Path to session directory
        types: List of secondary material types to generate
        config_loader: ConfigLoader instance
        llm_client: OllamaClient instance
        outline_text: Outline text for context
        logger: Logger instance
        
    Returns:
        Dictionary mapping material_type -> output_path
    """
    # Import cleanup functions
    from src.generate.processors.cleanup import full_cleanup_pipeline
    
    results: Dict[str, Path] = {}
    module_id = module.get("module_id", 0)
    module_name = module.get("module_name", f"Module {module_id}")
    session_number = session.get("session_number", 0)
    session_title = session.get("session_title", f"Session {session_number}")
    
    # Load all content from this session folder
    session_content = load_session_content(session_dir)
    
    if not session_content:
        logger.warning(f"No content found in session directory: {session_dir}")
        return results
    
    prompts_cfg = config_loader.load_llm_config().get("prompts", {})

    for material_type in types:
        prompt_key = f"secondary_{material_type}"
        prompt_cfg = prompts_cfg.get(prompt_key)
        if not prompt_cfg:
            logger.warning(f"No prompt template configured for {prompt_key}; skipping.")
            continue

        # Build prompt with session-specific context
        template = prompt_cfg.get("template", "")
        # Get subject and language from config
        subject = config_loader.get_course_subject()
        language = config_loader.get_language()
        # Use session_content for session-level generation
        user_prompt = template.format(
            module_name=module_name,
            module_id=module_id,
            session_number=session_number,
            session_title=session_title,
            subject=subject,
            outline=outline_text[:50000],  # Allow up to 50K chars for outline (128K context window)
            session_content=session_content[:50000],  # Allow up to 50K chars for session content (128K context window)
            material_type=material_type,
            language=language,
        )
        system_prompt = prompt_cfg.get("system", "").format(subject=subject) if "{subject}" in prompt_cfg.get("system", "") else prompt_cfg.get("system", "")

        logger.info(f"Generating {material_type} for session {session_number}: {session_title}...")
        
        # Get operation-specific timeout for this material type
        operation_timeout = config_loader.get_operation_timeout(material_type)
        
        try:
            content = llm_client.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                operation=material_type,
                timeout_override=operation_timeout
            )
        except LLMError as e:
            # Extract request ID from error message if present
            error_msg = str(e)
            request_id = None
            if "[" in error_msg and "]" in error_msg:
                try:
                    request_id = error_msg[error_msg.find("[")+1:error_msg.find("]")]
                except (ValueError, IndexError):
                    pass
            
            # Determine if this is a timeout error
            is_timeout = "timeout" in error_msg.lower() or "timed out" in error_msg.lower()
            
            # Build detailed error context
            error_context = (
                f"Module {module_id} Session {session_number} - {material_type} generation failed"
            )
            if request_id:
                error_context += f" (Request ID: {request_id})"
            
            # Log detailed error information
            logger.error(f"  ✗ {error_context}")
            logger.error(f"     Error: {error_msg}")
            if is_timeout:
                logger.error(f"     Type: Timeout error (operation timeout: {operation_timeout}s)")
                logger.error(f"     Suggestion: Check logs for request ID {request_id} if available, or increase timeout in config")
            else:
                logger.error(f"     Type: LLM generation error")
            
            # Add to error collector if provided
            if error_collector:
                error_collector.add_error(
                    type='llm_error' if not is_timeout else 'timeout',
                    message=error_msg,
                    context=error_context,
                    content_type=material_type,
                    module_id=module_id,
                    session_num=session_number
                )
            
            # Re-raise to be caught by outer exception handler
            raise
        
        # Apply cleanup to generated content
        content, _ = full_cleanup_pipeline(content, material_type)

        # Validate and log content metrics
        from src.utils.content_analysis import (
            analyze_application,
            analyze_extension,
            analyze_visualization,
            analyze_integration,
            analyze_investigation,
            analyze_open_questions,
            log_content_metrics
        )
        
        # Get content requirements for this material type
        content_requirements = config_loader.get_content_requirements()
        requirements = content_requirements.get(material_type, {})
        
        # Analyze content based on type
        if material_type == "application":
            metrics = analyze_application(content, requirements)
        elif material_type == "extension":
            metrics = analyze_extension(content, requirements)
        elif material_type == "visualization":
            metrics = analyze_visualization(content, requirements)
        elif material_type == "integration":
            metrics = analyze_integration(content, requirements)
        elif material_type == "investigation":
            metrics = analyze_investigation(content, requirements)
        elif material_type == "open_questions":
            metrics = analyze_open_questions(content, requirements)
        else:
            # Fallback for unknown types
            metrics = {
                'word_count': len(content.split()),
                'char_count': len(content),
                'warnings': []
            }
        
        # Log metrics with validation status
        log_content_metrics(material_type, metrics, logger)
        
        # Add warnings to error collector if provided
        if error_collector and metrics.get('warnings'):
            context_str = f"Module {module_id} Session {session_number}"
            for warning in metrics['warnings']:
                # Determine severity based on warning content
                # Critical issues: missing required elements, no content, structural failures
                # Warnings: word count issues, minor format problems, recommendations
                warning_lower = warning.lower()
                
                # Critical keywords that indicate serious problems
                critical_keywords = [
                    'no questions detected',
                    'no applications found',
                    'no topics found',
                    'missing required',
                    'only 0',
                    'only 1',
                    'only 2',  # For applications requiring 3-5
                    'no diagram',
                    'invalid syntax',
                    'cannot parse',
                    'failed to generate'
                ]
                
                # Check if this is a critical issue
                is_critical = any(keyword in warning_lower for keyword in critical_keywords)
                
                # Also check for patterns like "Only N found" where N is below minimum
                only_match = re.search(r'only (\d+)', warning_lower)
                if only_match:
                    count = int(only_match.group(1))
                    # If count is 0 or very low, likely critical
                    if count == 0:
                        is_critical = True
                
                # Use appropriate method based on severity
                if is_critical:
                    error_collector.add_error(
                        type='validation',
                        message=warning,
                        context=context_str,
                        content_type=material_type,
                        module_id=module_id,
                        session_num=session_number
                    )
                else:
                    error_collector.add_warning(
                        type='validation',
                        message=warning,
                        context=context_str,
                        content_type=material_type,
                        module_id=module_id,
                        session_num=session_number
                    )

        # Save directly in session folder (flat structure)
        ext = ".mmd" if material_type == "visualization" else ".md"
        out_path = session_dir / f"{material_type}{ext}"
        out_path.write_text(content, encoding="utf-8")
        results[material_type] = out_path
        logger.info(f"  → Saved to: {out_path}")
    return results


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

    try:
        config_loader = ConfigLoader(args.config_dir)
        config_loader.validate_all_configs()

        # Load modules from JSON outline
        if args.outline:
            logger.info(f"Using specified outline: {args.outline}")
            if not args.outline.exists():
                logger.error(f"Outline file not found: {args.outline}")
                return 1
            outline_path = Path(args.outline)
            modules = config_loader.get_modules_from_outline(args.outline)
        else:
            logger.info("Using most recent outline from output/outlines/ or scripts/output/outlines/")
            outline_path = config_loader._find_latest_outline_json()
            modules = config_loader.get_modules_from_outline()
        
        # Validate that modules were loaded
        if not modules:
            logger.error("No outline found or outline contains no modules")
            logger.error("Generate an outline first:")
            logger.error("  uv run python3 scripts/03_generate_outline.py")
            return 1
        
        # Extract course_name from outline JSON metadata (for course-specific paths)
        course_name = None
        if outline_path and outline_path.exists():
            course_name = config_loader._extract_course_name_from_outline(outline_path)
        
        # Get course-specific output paths (always uses subfolder structure now)
        # If course_name is None, get_output_paths() derives it from default course config
        output_paths = config_loader.get_output_paths(course_name)
        # Get the actual course name used (may be derived from default config)
        actual_course_name = output_paths.get('course_name', 'default')
        logger.info(f"Using course-specific output directory: output/{actual_course_name}/")
        
        directories = output_paths.get('directories', {})
        # Directories always contain full paths (e.g., "output/physics/modules" or "output/introductory_biology/modules")
        modules_path_str = directories.get('modules', 'modules')
        base_modules_dir = Path(modules_path_str)
        
        # Filter modules if specific IDs requested (not --all)
        if not args.all and args.modules:
            original_count = len(modules)
            modules = [m for m in modules if m.get("module_id") in args.modules]
            logger.info(f"Filtered to modules: {args.modules} ({len(modules)}/{original_count} modules)")
            if not modules:
                logger.error(f"No modules found with IDs: {args.modules}")
                return 1
        else:
            logger.info("Processing ALL modules")

        # Count total sessions across all modules
        total_sessions = sum(len(m.get('sessions', [])) for m in modules)
        logger.info(f"Processing {len(modules)} modules ({total_sessions} total sessions)")
        logger.info(f"Secondary types: {', '.join(args.types)}")
        
        # Dry-run mode
        if args.dry_run:
            logger.info("\n" + "=" * 80)
            logger.info("DRY-RUN MODE: Showing what would be generated")
            logger.info("=" * 80)
            for module in modules:
                module_id = module.get('module_id')
                module_name = module.get('module_name')
                sessions = module.get('sessions', [])
                logger.info(f"\nModule {module_id}: {module_name} ({len(sessions)} sessions)")
                for session in sessions:
                    session_num = session.get('session_number', 0)
                    session_title = session.get('session_title', '')
                    logger.info(f"  Session {session_num}: {session_title}")
                    for sec_type in args.types:
                        ext = ".mmd" if sec_type == "visualization" else ".md"
                        logger.info(f"    Would generate: {sec_type}{ext}")
            logger.info("\n" + "=" * 80)
            logger.info(f"Would generate {len(args.types)} secondary materials for {total_sessions} sessions")
            logger.info("=" * 80)
            return 0

        llm_cfg = config_loader.get_llm_parameters()
        llm_client = OllamaClient(llm_cfg)

        outline_text = find_latest_outline(args.outline)
        
        # Initialize error collector for tracking validation issues
        error_collector = ErrorCollector()

        successful = 0
        failed = 0
        session_count = 0

        for i, module in enumerate(modules, 1):
            module_id = module.get('module_id', 0)
            module_name = module.get('module_name', f"Module {module_id}")
            module_slug = slugify(f"module_{module_id:02d}_{module_name}")
            module_dir = base_modules_dir / module_slug
            
            sessions = module.get('sessions', [])
            
            logger.info(f"\n{'='*60}")
            logger.info(f"[{i}/{len(modules)}] Module {module_id}: {module_name} ({len(sessions)} sessions)")
            logger.info(f"{'='*60}")
            
            for session in sessions:
                session_number = session.get('session_number', 0)
                session_title = session.get('session_title', f"Session {session_number}")
                session_dir = module_dir / f"session_{session_number:02d}"
                session_count += 1
                
                logger.info(f"\n  Session {session_number}/{total_sessions}: {session_title}")
                
                if not session_dir.exists():
                    logger.warning(f"  ⚠ Session directory not found: {session_dir}")
                    failed += 1
                    continue
                
                try:
                    results = generate_secondary_for_session(
                        module,
                        session,
                        session_dir,
                        args.types,
                        config_loader,
                        llm_client,
                        outline_text,
                        logger,
                        error_collector=error_collector,
                    )
                    if results:
                        successful += 1
                        logger.info(f"  ✓ Generated {len(results)} secondary materials")
                    else:
                        failed += 1
                        logger.warning(f"  ⚠ No materials generated for session {session_number}")
                except LLMError as e:
                    failed += 1
                    # Extract request ID and error details
                    error_msg = str(e)
                    request_id = None
                    if "[" in error_msg and "]" in error_msg:
                        try:
                            request_id = error_msg[error_msg.find("[")+1:error_msg.find("]")]
                        except (ValueError, IndexError):
                            pass
                    
                    is_timeout = "timeout" in error_msg.lower()
                    error_type = "Timeout" if is_timeout else "LLM Error"
                    
                    logger.error(f"  ✗ {error_type} for session {session_number}: {session_title}")
                    logger.error(f"     Module: {module_name} (ID: {module_id})")
                    if request_id:
                        logger.error(f"     Request ID: {request_id} (filter logs: grep '[{request_id}]' output/logs/*.log)")
                    logger.error(f"     Error: {error_msg}")
                    if is_timeout:
                        logger.error(f"     Troubleshooting: See docs/TROUBLESHOOTING.md for timeout resolution steps")
                except Exception as e:
                    failed += 1
                    error_type = type(e).__name__
                    logger.error(f"  ✗ {error_type} for session {session_number}: {session_title}")
                    logger.error(f"     Module: {module_name} (ID: {module_id})")
                    logger.error(f"     Error: {str(e)}")
                    logger.error(f"     Full traceback:", exc_info=True)

        # Generate stage summary with error collector
        generate_stage_summary(
            error_collector,
            "Secondary Materials Generation",
            logger,
            total_items=session_count,
            successful_items=successful,
            failed_items=failed
        )
        
        # Check for critical issues
        critical_issues = error_collector.get_critical_issues()
        warnings = error_collector.get_warnings()
        
        # Determine exit code and log reason
        exit_code = 0 if failed == 0 and len(critical_issues) == 0 else 1
        
        if exit_code != 0:
            logger.error("\n" + "=" * 80)
            logger.error("EXIT CODE: 1 (FAILURE)")
            logger.error("=" * 80)
            if failed > 0:
                logger.error(f"Reason: {failed} session(s) failed during generation")
                logger.error("")
                logger.error("Failed sessions details:")
                # Log details from error collector if available
                all_errors = error_collector.get_all_errors() if error_collector else []
                if all_errors:
                    for i, error in enumerate(all_errors[:5], 1):  # Show top 5 errors
                        logger.error(f"  {i}. {error.context or 'Unknown context'}")
                        logger.error(f"     Type: {error.type}, Content: {error.content_type or 'N/A'}")
                        logger.error(f"     Message: {error.message[:200]}")  # Truncate long messages
                    if len(all_errors) > 5:
                        logger.error(f"  ... and {len(all_errors) - 5} more errors (check log file for details)")
                else:
                    logger.error("  (Error details not captured - check log file for full traceback)")
            if critical_issues:
                logger.error("")
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
            if warnings:
                logger.info(f"Note: {len(warnings)} warning(s) found (content may need review)")
                logger.info("Warnings do not cause exit code 1 - only critical issues do")
            else:
                logger.info("All sessions processed successfully with no issues")
            logger.info("=" * 80)
        
        return exit_code
    except ConfigurationError as exc:
        logger.error(f"Configuration error: {exc}", exc_info=True)
        return 1
    except Exception as exc:  # noqa: BLE001
        logger.error(f"ERROR: {exc}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())


