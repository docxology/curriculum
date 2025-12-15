"""Utility functions for educational course generator.

This package provides common utilities for file operations, text processing,
logging setup, and other helper functions.
"""

from src.utils.helpers import (
    ensure_directory,
    slugify,
    save_markdown,
    load_markdown,
    format_timestamp,
    sanitize_filename,
    format_module_filename
)
from src.utils.logging_setup import (
    setup_logging,
    log_section_header,
    log_parameters,
    log_validation_results,
    log_summary_box,
    log_status_with_text,
    log_error_summary,
    get_logging_config,
)
from src.utils.error_collector import ErrorCollector
from src.utils.summary_generator import (
    generate_stage_summary,
    generate_validation_summary,
    generate_generation_summary,
    categorize_errors_by_type,
    format_error_list,
)
from src.utils.content_analysis import (
    count_words,
    count_sections,
    count_subsections,
    count_examples,
    count_definitions,
    count_cross_references,
    analyze_lecture,
    analyze_lab,
    analyze_questions,
    analyze_study_notes,
    analyze_application,
    analyze_extension,
    analyze_visualization,
    analyze_integration,
    analyze_investigation,
    analyze_open_questions,
    validate_mermaid_syntax,
    log_content_metrics
)

__all__ = [
    'ensure_directory',
    'slugify',
    'save_markdown',
    'load_markdown',
    'format_timestamp',
    'sanitize_filename',
    'format_module_filename',
    'setup_logging',
    'log_section_header',
    'log_parameters',
    'log_validation_results',
    'log_summary_box',
    'log_status_with_text',
    'log_error_summary',
    'get_logging_config',
    'ErrorCollector',
    'generate_stage_summary',
    'generate_validation_summary',
    'generate_generation_summary',
    'categorize_errors_by_type',
    'format_error_list',
    'count_words',
    'count_sections',
    'count_subsections',
    'count_examples',
    'count_definitions',
    'count_cross_references',
    'analyze_lecture',
    'analyze_lab',
    'analyze_questions',
    'analyze_study_notes',
    'analyze_application',
    'analyze_extension',
    'analyze_visualization',
    'analyze_integration',
    'analyze_investigation',
    'analyze_open_questions',
    'validate_mermaid_syntax',
    'log_content_metrics',
]


