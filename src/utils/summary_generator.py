"""Summary generation utilities for content generation stages.

This module provides functions to generate formatted summaries of validation
issues, generation statistics, and error reports.
"""

import logging
from typing import Dict, List, Any, Optional

from src.utils.error_collector import ErrorCollector, ErrorEntry
from src.utils.logging_setup import log_status_with_text, log_info_box, log_summary_box, SEPARATOR_LINE


def categorize_errors_by_type(errors: List[ErrorEntry]) -> Dict[str, List[ErrorEntry]]:
    """Group errors by error type for analysis.
    
    Args:
        errors: List of error entries
        
    Returns:
        Dictionary mapping error type to list of errors
    """
    categorized: Dict[str, List[ErrorEntry]] = {}
    for error in errors:
        error_type = error.type or "unknown"
        if error_type not in categorized:
            categorized[error_type] = []
        categorized[error_type].append(error)
    return categorized


def format_error_list(
    errors: List[ErrorEntry],
    max_items: int = 10,
    show_context: bool = True
) -> List[str]:
    """Format error list for display.
    
    Args:
        errors: List of error entries
        max_items: Maximum number of errors to format
        show_context: Whether to include context information
        
    Returns:
        List of formatted error strings
    """
    formatted = []
    displayed = min(len(errors), max_items)
    
    for i, error in enumerate(errors[:max_items], 1):
        parts = [f"[{i}/{displayed}] [{error.severity}] {error.message}"]
        
        if show_context:
            if error.context:
                parts.append(f"         Context: {error.context}")
            if error.content_type:
                parts.append(f"         Content Type: {error.content_type}")
            if error.module_id is not None:
                parts.append(f"         Module: {error.module_id}")
            if error.session_num is not None:
                parts.append(f"         Session: {error.session_num}")
        
        formatted.append("\n".join(parts))
    
    if len(errors) > max_items:
        formatted.append(f"... and {len(errors) - max_items} more errors")
    
    return formatted


def generate_validation_summary(
    collector: ErrorCollector,
    logger: logging.Logger
) -> None:
    """Generate summary of all validation issues.
    
    Args:
        collector: ErrorCollector instance with collected issues
        logger: Logger instance for output
    """
    summary = collector.get_summary()
    critical_issues = collector.get_critical_issues()
    warnings = collector.get_warnings()
    
    logger.info("")
    logger.info("═" * 80)
    logger.info("[VALIDATION SUMMARY] Content Generation Validation Results")
    logger.info("═" * 80)
    
    # Overall statistics
    logger.info(f"  Total Issues: {summary['total_issues']}")
    logger.info(f"    - [CRITICAL]: {summary['total_errors']}")
    logger.info(f"    - [WARNING]: {summary['total_warnings']}")
    logger.info(f"    - [INFO]: {summary['total_info']}")
    
    # Breakdown by content type
    if summary['by_content_type']:
        logger.info("")
        logger.info("  Issues by Content Type:")
        for content_type, count in sorted(summary['by_content_type'].items()):
            logger.info(f"    - {content_type}: {count}")
    
    # Breakdown by error type
    if summary['by_error_type']:
        logger.info("")
        logger.info("  Issues by Error Type:")
        for error_type, count in sorted(summary['by_error_type'].items()):
            logger.info(f"    - {error_type}: {count}")
    
    # Critical issues
    if critical_issues:
        logger.info("")
        logger.info(f"  [CRITICAL] Top {min(5, len(critical_issues))} Critical Issues:")
        for i, error in enumerate(critical_issues[:5], 1):
            logger.warning(f"    {i}. {error.message}")
            if error.context:
                logger.warning(f"       Context: {error.context}")
    
    logger.info("═" * 80)


def generate_stage_summary(
    collector: ErrorCollector,
    stage_name: str,
    logger: logging.Logger,
    total_items: Optional[int] = None,
    successful_items: Optional[int] = None,
    failed_items: Optional[int] = None
) -> None:
    """Generate stage-level summary with compliance statistics.
    
    Args:
        collector: ErrorCollector instance with collected issues
        stage_name: Name of the stage (e.g., "Primary Materials Generation")
        logger: Logger instance for output
        total_items: Total number of items processed (optional)
        successful_items: Number of successful items (optional)
        failed_items: Number of failed items (optional)
    """
    summary = collector.get_summary()
    critical_issues = collector.get_critical_issues()
    warnings = collector.get_warnings()
    
    # Determine overall status
    if critical_issues:
        status = "error"
        status_emoji = "❌"
        status_text = "CRITICAL ISSUES FOUND"
    elif warnings:
        status = "warning"
        status_emoji = "⚠️"
        status_text = "WARNINGS FOUND"
    else:
        status = "success"
        status_emoji = "✅"
        status_text = "ALL COMPLIANT"
    
    logger.info("")
    logger.info("═" * 80)
    log_status_with_text(logger, status_text, f"{stage_name} - Summary", emoji=status_emoji, level="INFO")
    logger.info("═" * 80)
    
    # Processing statistics
    if total_items is not None:
        logger.info(f"  Items Processed: {total_items}")
        if successful_items is not None:
            logger.info(f"    - [COMPLIANT] Successful: {successful_items}")
        if failed_items is not None:
            logger.info(f"    - [ERROR] Failed: {failed_items}")
    
    # Compliance breakdown
    # Note: One item can have multiple warnings, so we can't simply subtract
    # Instead, we estimate: items with issues <= min(len(critical_issues) + unique_warning_items, total_items)
    # For now, we use a conservative estimate: assume each critical issue and each warning
    # might be from a different item, but cap at total_items
    logger.info("")
    logger.info("  Compliance Breakdown:")
    if total_items:
        # Estimate items with issues (conservative: assume each issue is from different item)
        items_with_issues = min(len(critical_issues) + len(warnings), total_items)
        compliant_count = max(0, total_items - items_with_issues)
        # More accurate: count unique items with issues from error collector
        # Get unique (module_id, session_num) pairs for critical issues
        critical_items = set()
        for issue in critical_issues:
            if issue.module_id is not None and issue.session_num is not None:
                critical_items.add((issue.module_id, issue.session_num))
        # Get unique (module_id, session_num) pairs for warnings
        warning_items = set()
        for warning in warnings:
            if warning.module_id is not None and warning.session_num is not None:
                warning_items.add((warning.module_id, warning.session_num))
        # Combine unique items
        unique_items_with_issues = len(critical_items | warning_items)
        # Use more accurate count if available, otherwise use conservative estimate
        if unique_items_with_issues > 0:
            compliant_count = max(0, total_items - unique_items_with_issues)
            needs_review_count = len(warning_items)
            critical_count = len(critical_items)
        else:
            # Fallback: use conservative estimate
            needs_review_count = len(warnings)
            critical_count = len(critical_issues)
    else:
        compliant_count = 'N/A'
        needs_review_count = len(warnings)
        critical_count = len(critical_issues)
    
    logger.info(f"    - [COMPLIANT]: {compliant_count}")
    logger.info(f"    - [NEEDS REVIEW]: {needs_review_count}")
    logger.info(f"    - [CRITICAL]: {critical_count}")
    
    # Issue statistics
    logger.info("")
    logger.info("  Issue Statistics:")
    logger.info(f"    - Total Issues: {summary['total_issues']}")
    logger.info(f"    - Critical Errors: {summary['total_errors']}")
    logger.info(f"    - Warnings: {summary['total_warnings']}")
    
    # Top critical issues
    if critical_issues:
        logger.info("")
        logger.info(f"  [CRITICAL] Top Issues Requiring Attention:")
        top_issues = critical_issues[:5]
        for i, error in enumerate(top_issues, 1):
            logger.warning(f"    {i}. {error.message}")
            if error.context:
                logger.warning(f"       Context: {error.context}")
            if error.content_type:
                logger.warning(f"       Content Type: {error.content_type}")
    
    # Recommendations
    logger.info("")
    logger.info("  Recommendations:")
    if critical_issues:
        logger.warning("    - Review and fix critical issues before proceeding")
        logger.warning("    - Consider regenerating content with issues")
    elif warnings:
        logger.info("    - Review warnings for potential improvements")
        logger.info("    - Content is usable but may need refinement")
    else:
        logger.info("    - All content generated successfully")
        logger.info("    - No issues detected")
    
    logger.info("═" * 80)


def generate_generation_summary(
    results: Dict[str, Any],
    collector: ErrorCollector,
    logger: logging.Logger
) -> None:
    """Generate overall generation statistics summary.
    
    Args:
        results: Dictionary with generation results
        collector: ErrorCollector instance with collected issues
        logger: Logger instance for output
    """
    summary = collector.get_summary()
    critical_issues = collector.get_critical_issues()
    
    # Determine overall status
    if critical_issues:
        status = "error"
        status_emoji = "❌"
    elif summary['total_warnings'] > 0:
        status = "warning"
        status_emoji = "⚠️"
    else:
        status = "success"
        status_emoji = "✅"
    
    # Build summary items
    summary_items: Dict[str, Any] = {}
    
    # Add results statistics
    if 'sessions_generated' in results:
        summary_items['Sessions Generated'] = results['sessions_generated']
    if 'modules_processed' in results:
        summary_items['Modules Processed'] = results['modules_processed']
    
    # Add issue statistics
    summary_items['Total Issues'] = summary['total_issues']
    summary_items['Critical Errors'] = summary['total_errors']
    summary_items['Warnings'] = summary['total_warnings']
    
    # Add breakdown by content type
    if summary['by_content_type']:
        for content_type, count in sorted(summary['by_content_type'].items()):
            summary_items[f'Issues in {content_type}'] = count
    
    log_summary_box(
        logger,
        "Generation Complete - Final Summary",
        summary_items,
        status=status
    )
    
    # Show critical issues if any
    if critical_issues:
        logger.info("")
        logger.info("  [CRITICAL] Issues Requiring Immediate Attention:")
        for i, error in enumerate(critical_issues[:10], 1):
            logger.warning(f"    {i}. {error.message}")
            if error.context:
                logger.warning(f"       {error.context}")




