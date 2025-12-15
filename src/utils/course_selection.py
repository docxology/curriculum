"""Shared utility for course template selection.

This module provides a reusable function for selecting course templates
interactively, used by multiple scripts.
"""

import logging
from typing import Optional

from src.config.loader import ConfigLoader

logger = logging.getLogger(__name__)

# Sentinel value for "generate all courses" option
GENERATE_ALL_COURSES = "__ALL__"


def select_course_template(
    config_loader: ConfigLoader, 
    logger_instance: logging.Logger
) -> Optional[str]:
    """Interactively select a course template from available options.
    
    Args:
        config_loader: ConfigLoader instance to list available courses
        logger_instance: Logger instance for logging
        
    Returns:
        Selected course template name (without .yaml extension), 
        GENERATE_ALL_COURSES sentinel for "generate all", 
        or None for default course_config.yaml
    """
    courses = config_loader.list_available_courses()
    
    if not courses:
        logger_instance.info("No course templates found in config/courses/")
        logger_instance.info("Using default course_config.yaml")
        return None
    
    logger_instance.info("")
    logger_instance.info("=" * 80)
    logger_instance.info("COURSE TEMPLATE SELECTION")
    logger_instance.info("=" * 80)
    logger_instance.info("Available course templates:")
    logger_instance.info("")
    
    for idx, course in enumerate(courses, start=1):
        course_info = course["course_info"]
        name = course_info.get("name", course["name"])
        description = course_info.get("description", "No description")
        level = course_info.get("level", "Not specified")
        subject = course_info.get("subject", "Not specified")
        
        logger_instance.info(f"  {idx}. {name}")
        logger_instance.info(f"     Subject: {subject}")
        logger_instance.info(f"     Level: {level}")
        logger_instance.info(f"     Description: {description[:80]}{'...' if len(description) > 80 else ''}")
        logger_instance.info("")
    
    logger_instance.info(f"  {len(courses) + 1}. Use default (course_config.yaml)")
    logger_instance.info(f"  {len(courses) + 2}. Generate all courses")
    logger_instance.info("")
    
    max_choice = len(courses) + 2
    
    while True:
        try:
            choice = input(f"Select course template (1-{max_choice}) [default: {len(courses) + 1}]: ").strip()
            
            if not choice:
                logger_instance.info("Using default course_config.yaml")
                return None
            
            choice_num = int(choice)
            
            if choice_num == len(courses) + 1:
                logger_instance.info("Using default course_config.yaml")
                return None
            
            if choice_num == len(courses) + 2:
                logger_instance.info("Selected: Generate all courses")
                return GENERATE_ALL_COURSES
            
            if 1 <= choice_num <= len(courses):
                selected = courses[choice_num - 1]
                logger_instance.info(f"Selected course template: {selected['name']}")
                return selected["name"]
            else:
                logger_instance.warning(f"Invalid choice. Please enter a number between 1 and {max_choice}")
        except ValueError:
            logger_instance.warning("Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            logger_instance.info("\nCancelled. Using default course_config.yaml")
            return None




