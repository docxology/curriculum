#!/usr/bin/env python3
"""03 - Interactive outline generation (Stage 1)."""

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
from typing import Dict, Any

from src.config.loader import ConfigLoader
from src.generate.orchestration.pipeline import ContentGenerator
from src.generate.orchestration.batch import BatchCourseProcessor
from src.utils.course_selection import select_course_template, GENERATE_ALL_COURSES
from src.utils.logging_setup import setup_logging, log_section_clean, log_info_box, log_status_item
from typing import Optional


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




def maybe_override_course_info(
    course: Dict[str, Any], 
    logger: logging.Logger, 
    config_loader: Any = None
) -> tuple[Dict[str, Any], str, Dict[str, Any]]:
    """Interactively allow user to override course metadata and output settings.
    
    Args:
        course: Course information dictionary
        logger: Logger instance for detailed logging
        config_loader: ConfigLoader instance to get output paths and defaults
        
    Returns:
        Tuple of (updated course info, output_base_dir, structure_config)
    """
    def prompt(msg: str, default: str) -> str:
        resp = input(f"{msg} [{default}]: ").strip()
        return resp or default

    logger.info("Starting interactive course configuration...")
    logger.info("Current defaults loaded from config/course_config.yaml")
    logger.info("Press Enter to accept defaults, or type new values")
    logger.info("-" * 80)
    
    # Get defaults from config
    defaults = config_loader.get_course_defaults() if config_loader else {}
    
    # Improved defaults with more context and quality
    default_name = course.get("name", "Introductory Course")
    default_subject = course.get("subject", "general education")
    default_level = course.get("level", "Undergraduate Introductory (100-200 level)")
    default_description = course.get(
        "description",
        "Comprehensive introduction covering fundamental concepts and principles"
    )
    default_constraints = course.get("additional_constraints", "")
    
    # Interactive prompts with logging
    new_name = prompt("Course name", default_name)
    if new_name != default_name:
        logger.info(f"Course name changed: '{default_name}' → '{new_name}'")
    course["name"] = new_name
    
    new_subject = prompt("Subject/Expertise area", default_subject)
    if new_subject != default_subject:
        logger.info(f"Subject changed: '{default_subject}' → '{new_subject}'")
    course["subject"] = new_subject
    
    new_level = prompt("Course level", default_level)
    if new_level != default_level:
        logger.info(f"Course level changed: '{default_level}' → '{new_level}'")
    course["level"] = new_level
    
    # Language selection
    import os
    default_language = config_loader.get_language() if config_loader else "English"
    new_language = prompt("Language for course content generation", default_language)
    if new_language != default_language:
        logger.info(f"Language changed: '{default_language}' → '{new_language}'")
    # Update environment variable and in-memory config
    os.environ["COURSE_LANGUAGE"] = new_language
    if config_loader:
        llm_config = config_loader.load_llm_config()
        llm_config.setdefault("llm", {})["language"] = new_language
        config_loader._llm_config = llm_config
    
    # NEW: Module and Session Structure Configuration
    logger.info("-" * 80)
    logger.info("MODULE AND SESSION STRUCTURE")
    logger.info("-" * 80)
    
    default_num_modules = defaults.get("num_modules", 5)
    num_modules_str = prompt("Number of modules", str(default_num_modules))
    try:
        num_modules = int(num_modules_str)
        if num_modules <= 0:
            logger.warning(f"Invalid module count, using default: {default_num_modules}")
            num_modules = default_num_modules
        else:
            if num_modules != default_num_modules:
                logger.info(f"Number of modules: {default_num_modules} → {num_modules}")
    except ValueError:
        logger.warning(f"Invalid format, using default: {default_num_modules}")
        num_modules = default_num_modules
    
    default_total_sessions = defaults.get("total_sessions", num_modules * 2)
    total_sessions_str = prompt("Total sessions", str(default_total_sessions))
    try:
        total_sessions = int(total_sessions_str)
        if total_sessions <= 0:
            logger.warning(f"Invalid session count, using default: {default_total_sessions}")
            total_sessions = default_total_sessions
        else:
            if total_sessions != default_total_sessions:
                logger.info(f"Total sessions: {default_total_sessions} → {total_sessions}")
    except ValueError:
        logger.warning(f"Invalid format, using default: {default_total_sessions}")
        total_sessions = default_total_sessions
    
    avg_sessions = total_sessions / num_modules
    logger.info(f"Configuration: {num_modules} modules, {total_sessions} sessions")
    logger.info(f"Average: {avg_sessions:.1f} sessions per module")
    
    # Validation
    if total_sessions < num_modules:
        logger.warning("⚠️  Sessions < modules: Some modules may be combined or abbreviated")
    
    # NEW: Content Item Bounds Configuration
    logger.info("-" * 80)
    logger.info("CONTENT ITEM BOUNDS")
    logger.info("-" * 80)
    
    # Get defaults from llm_config
    default_bounds = {
        'subtopics_min': 3, 'subtopics_max': 7,
        'objectives_min': 3, 'objectives_max': 7,
        'concepts_min': 3, 'concepts_max': 7
    }
    if config_loader:
        try:
            llm_config = config_loader.load_llm_config()
            bounds_config = llm_config.get('outline_generation', {}).get('items_per_field', {})
            default_bounds['subtopics_min'] = bounds_config.get('subtopics', {}).get('min', 3)
            default_bounds['subtopics_max'] = bounds_config.get('subtopics', {}).get('max', 7)
            default_bounds['objectives_min'] = bounds_config.get('learning_objectives', {}).get('min', 3)
            default_bounds['objectives_max'] = bounds_config.get('learning_objectives', {}).get('max', 7)
            default_bounds['concepts_min'] = bounds_config.get('key_concepts', {}).get('min', 3)
            default_bounds['concepts_max'] = bounds_config.get('key_concepts', {}).get('max', 7)
        except Exception:
            pass
    
    # Subtopics bounds
    try:
        min_subtopics_str = prompt("Minimum subtopics per session", str(default_bounds['subtopics_min']))
        max_subtopics_str = prompt("Maximum subtopics per session", str(default_bounds['subtopics_max']))
        min_subtopics = int(min_subtopics_str)
        max_subtopics = int(max_subtopics_str)
        if min_subtopics > max_subtopics or min_subtopics <= 0:
            logger.warning(f"Invalid subtopics bounds, using defaults: {default_bounds['subtopics_min']}-{default_bounds['subtopics_max']}")
            min_subtopics = default_bounds['subtopics_min']
            max_subtopics = default_bounds['subtopics_max']
        elif min_subtopics != default_bounds['subtopics_min'] or max_subtopics != default_bounds['subtopics_max']:
            logger.info(f"Subtopics bounds: {default_bounds['subtopics_min']}-{default_bounds['subtopics_max']} → {min_subtopics}-{max_subtopics}")
    except ValueError:
        logger.warning(f"Invalid format, using defaults: {default_bounds['subtopics_min']}-{default_bounds['subtopics_max']}")
        min_subtopics = default_bounds['subtopics_min']
        max_subtopics = default_bounds['subtopics_max']
    
    # Learning objectives bounds
    try:
        min_objectives_str = prompt("Minimum learning objectives per session", str(default_bounds['objectives_min']))
        max_objectives_str = prompt("Maximum learning objectives per session", str(default_bounds['objectives_max']))
        min_objectives = int(min_objectives_str)
        max_objectives = int(max_objectives_str)
        if min_objectives > max_objectives or min_objectives <= 0:
            logger.warning(f"Invalid objectives bounds, using defaults: {default_bounds['objectives_min']}-{default_bounds['objectives_max']}")
            min_objectives = default_bounds['objectives_min']
            max_objectives = default_bounds['objectives_max']
        elif min_objectives != default_bounds['objectives_min'] or max_objectives != default_bounds['objectives_max']:
            logger.info(f"Learning objectives bounds: {default_bounds['objectives_min']}-{default_bounds['objectives_max']} → {min_objectives}-{max_objectives}")
    except ValueError:
        logger.warning(f"Invalid format, using defaults: {default_bounds['objectives_min']}-{default_bounds['objectives_max']}")
        min_objectives = default_bounds['objectives_min']
        max_objectives = default_bounds['objectives_max']
    
    # Key concepts bounds
    try:
        min_concepts_str = prompt("Minimum key concepts per session", str(default_bounds['concepts_min']))
        max_concepts_str = prompt("Maximum key concepts per session", str(default_bounds['concepts_max']))
        min_concepts = int(min_concepts_str)
        max_concepts = int(max_concepts_str)
        if min_concepts > max_concepts or min_concepts <= 0:
            logger.warning(f"Invalid concepts bounds, using defaults: {default_bounds['concepts_min']}-{default_bounds['concepts_max']}")
            min_concepts = default_bounds['concepts_min']
            max_concepts = default_bounds['concepts_max']
        elif min_concepts != default_bounds['concepts_min'] or max_concepts != default_bounds['concepts_max']:
            logger.info(f"Key concepts bounds: {default_bounds['concepts_min']}-{default_bounds['concepts_max']} → {min_concepts}-{max_concepts}")
    except ValueError:
        logger.warning(f"Invalid format, using defaults: {default_bounds['concepts_min']}-{default_bounds['concepts_max']}")
        min_concepts = default_bounds['concepts_min']
        max_concepts = default_bounds['concepts_max']
    
    new_description = prompt("Course description", default_description)
    if new_description != default_description:
        logger.info(f"Description changed (length: {len(default_description)} → {len(new_description)} chars)")
    course["description"] = new_description
    
    # New field: additional constraints (optional)
    new_constraints = prompt("Additional constraints (optional, press Enter to skip)", default_constraints)
    if new_constraints != default_constraints:
        if new_constraints:
            logger.info(f"Additional constraints added (length: {len(new_constraints)} chars)")
        else:
            logger.info("Additional constraints cleared")
    course["additional_constraints"] = new_constraints
    
    # Output directory configuration
    default_output_dir = "output"
    if config_loader:
        try:
            output_paths = config_loader.get_output_paths()
            default_output_dir = output_paths.get('base_directory', 'output')
        except Exception:
            pass
    
    new_output_dir = prompt("Output base directory", default_output_dir)
    if new_output_dir != default_output_dir:
        logger.info(f"Output directory changed: '{default_output_dir}' → '{new_output_dir}'")
    
    # Prompt for clearing output directory
    clear_choice = prompt("Clear output directory? (y/n)", "n").lower()
    should_clear = clear_choice in ['y', 'yes']
    logger.info(f"Clear output: {'Yes' if should_clear else 'No'}")
    
    logger.info("-" * 80)
    logger.info("Interactive configuration complete")
    
    # Prepare structure configuration
    structure_config = {
        "num_modules": num_modules,
        "total_sessions": total_sessions,
        "avg_sessions_per_module": avg_sessions,
        "should_clear_output": should_clear,
        "min_subtopics": min_subtopics,
        "max_subtopics": max_subtopics,
        "min_objectives": min_objectives,
        "max_objectives": max_objectives,
        "min_concepts": min_concepts,
        "max_concepts": max_concepts
    }
    
    return course, new_output_dir, structure_config


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

    try:
        config_loader = ConfigLoader(args.config_dir)
        config_loader.validate_all_configs()
        
        # Determine which course template to use
        selected_course = args.course
        
        # If no course specified and in interactive mode, show selection menu
        if not selected_course and not args.no_interactive:
            selected_course = select_course_template(config_loader, logger)
        
        # Handle "generate all courses" option
        if selected_course == GENERATE_ALL_COURSES:
            logger.info("")
            log_section_clean(logger, "BATCH MODE: Generating Outlines for All Courses", emoji="📝")
            batch_processor = BatchCourseProcessor(args.config_dir, _project_root)
            summary = batch_processor.process_all_courses_for_outline(args, logger)
            
            logger.info("")
            logger.info("=" * 80)
            logger.info("BATCH PROCESSING COMPLETE")
            logger.info("=" * 80)
            logger.info(summary['summary'])
            return 0 if len(summary['failed']) == 0 else 1
        
        # Load course info from template or default
        if selected_course:
            logger.info(f"Loading course template: {selected_course}")
            try:
                course_info = config_loader.get_course_info(course_template=selected_course)
                # Update the cached config to use the template
                config_loader._course_config = config_loader.load_course_config(course_template=selected_course)
            except Exception as e:
                logger.warning(f"Failed to load course template '{selected_course}': {e}")
                logger.info("Falling back to default course_config.yaml")
                course_info = config_loader.get_course_info()
                selected_course = None  # Clear selected course on error
        else:
            course_info = config_loader.get_course_info()
            selected_course = None  # Explicitly set to None for default

        output_base_dir = args.output_dir
        
        if not args.no_interactive:
            logger.info("")
            log_section_clean(logger, "INTERACTIVE MODE: Customize Course Metadata", emoji="✏️")
            course_info, interactive_output_dir, structure_config = maybe_override_course_info(
                course_info.copy(), logger, config_loader
            )
            # Use interactive output dir if no command-line override
            if output_base_dir is None:
                output_base_dir = interactive_output_dir
            
            # Apply overrides back into loader cache so downstream uses updated values
            config_loader._course_config = config_loader.load_course_config()
            config_loader._course_config["course"] = course_info
            
            # Also update output config if changed
            if output_base_dir != config_loader.get_output_paths().get('base_directory', 'output'):
                if not hasattr(config_loader, '_output_config'):
                    config_loader._output_config = config_loader.load_output_config()
                config_loader._output_config['output']['base_directory'] = output_base_dir
            
            # Store structure config in loader for pipeline to use
            config_loader._structure_config = structure_config
            
            # Log final configuration being used
            logger.info("")
            
            final_config = {
                "Course Name": course_info['name'],
                "Course Level": course_info['level'],
                "Description": course_info['description'][:100] + "..." if len(course_info['description']) > 100 else course_info['description'],
                "Additional Constraints": course_info.get('additional_constraints', 'None')[:100] + "..." if course_info.get('additional_constraints') else 'None',
                "Number of Modules": structure_config['num_modules'],
                "Total Sessions": structure_config['total_sessions'],
                "Avg Sessions per Module": f"{structure_config['avg_sessions_per_module']:.1f}",
                "Subtopics per Session": f"{structure_config['min_subtopics']}-{structure_config['max_subtopics']}",
                "Learning Objectives per Session": f"{structure_config['min_objectives']}-{structure_config['max_objectives']}",
                "Key Concepts per Session": f"{structure_config['min_concepts']}-{structure_config['max_concepts']}",
                "Output Directory": str(output_base_dir),
                "Clear Output": 'Yes' if structure_config['should_clear_output'] else 'No'
            }
            log_info_box(logger, "FINAL COURSE CONFIGURATION", final_config, emoji="📋")
        else:
            # Non-interactive mode: use defaults from config
            structure_config = None

        generator = ContentGenerator(config_loader)
        
        # Handle clear output (from --clear-output flag or interactive prompt)
        struct_config = getattr(config_loader, '_structure_config', None)
        should_clear = args.clear_output or (struct_config and struct_config.get('should_clear_output', False))
        
        if should_clear:
            logger.info("")
            log_section_clean(logger, "CLEARING OUTPUT DIRECTORY", emoji="🗑️")
            generator.clear_output_directories(confirm=False, course_name=selected_course)
        
        # Pass structure config to generator
        if struct_config:
            num_modules = struct_config['num_modules']
            total_sessions = struct_config['total_sessions']
            min_subtopics = struct_config.get('min_subtopics')
            max_subtopics = struct_config.get('max_subtopics')
            min_objectives = struct_config.get('min_objectives')
            max_objectives = struct_config.get('max_objectives')
            min_concepts = struct_config.get('min_concepts')
            max_concepts = struct_config.get('max_concepts')
        else:
            # Use defaults from config
            defaults = config_loader.get_course_defaults()
            num_modules = defaults.get('num_modules', 5)
            total_sessions = defaults.get('total_sessions', 15)
            min_subtopics = None
            max_subtopics = None
            min_objectives = None
            max_objectives = None
            min_concepts = None
            max_concepts = None
        
        outline_path = generator.stage1_generate_outline(
            num_modules=num_modules,
            total_sessions=total_sessions,
            min_subtopics=min_subtopics,
            max_subtopics=max_subtopics,
            min_objectives=min_objectives,
            max_objectives=max_objectives,
            min_concepts=min_concepts,
            max_concepts=max_concepts,
            course_name=selected_course
        )

        logger.info("")
        log_status_item(logger, "Outline Generated Successfully", str(outline_path), "success")
        return 0
    except Exception as exc:  # noqa: BLE001
        logger.error(f"ERROR: {exc}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

