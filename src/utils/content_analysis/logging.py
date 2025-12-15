"""Logging utilities for content analysis metrics."""

import logging
from typing import Dict, Any

from src.utils.logging_setup import log_status_with_text


logger = logging.getLogger(__name__)


def log_content_metrics(
    content_type: str,
    metrics: Dict[str, Any],
    logger_obj: logging.Logger = None
) -> None:
    """Log content analysis metrics with appropriate formatting.
    
    Args:
        content_type: Type of content (lecture, lab, questions, etc.)
        metrics: Metrics dictionary from analyze_* functions
        logger_obj: Logger to use (defaults to module logger)
    """
    log = logger_obj or logger
    
    # Determine overall compliance status
    has_warnings = bool(metrics.get('warnings'))
    status_text = "NEEDS REVIEW" if has_warnings else "COMPLIANT"
    status_emoji = "⚠️" if has_warnings else "✓"
    
    # Log basic metrics with compliance status (using text labels for accessibility)
    if content_type == "lecture":
        log_status_with_text(log, status_text, f"Lecture generated", emoji=status_emoji, level="INFO")
        log.info(f"    - Length: {metrics['char_count']} chars, {metrics['word_count']} words")
        
        # Show requirements if available
        if 'requirements' in metrics:
            reqs = metrics['requirements']
            log.info(f"    - Requirements: {reqs.get('word_count_range', 'N/A')} words, {reqs.get('examples_range', 'N/A')} examples, {reqs.get('sections_range', 'N/A')} sections")
        
        log.info(f"    - Structure: {metrics['sections']} sections, {metrics['subsections']} subsections")
        log.info(f"    - Content: {metrics['examples']} examples, {metrics['terms']} terms defined")
        if metrics.get('cross_refs', 0) > 0:
            log.info(f"    - Cross-references: {metrics['cross_refs']}")
    
    elif content_type == "lab":
        log_status_with_text(log, status_text, f"Lab generated", emoji=status_emoji, level="INFO")
        log.info(f"    - Length: {metrics['char_count']} chars, {metrics['word_count']} words")
        log.info(f"    - Procedure: {metrics['procedure_steps']} steps")
        log.info(f"    - Safety: {metrics['safety_warnings']} warnings")
        if metrics.get('tables', 0) > 0:
            log.info(f"    - Data tables: {metrics['tables']}")
    
    elif content_type == "questions":
        # Determine severity of issues
        critical_issues = []
        warnings_list = metrics.get('warnings', [])
        for warning in warnings_list:
            if any(keyword in warning.lower() for keyword in ['missing question marks', 'missing explanations', 'missing answers', 'no questions detected']):
                critical_issues.append(warning)
        
        # Determine severity indicator with text labels
        if critical_issues:
            severity_text = "CRITICAL"
            severity_emoji = "🔴"
        elif warnings_list:
            severity_text = "WARNING"
            severity_emoji = "⚠️"
        else:
            severity_text = "OK"
            severity_emoji = "✓"
        
        log_status_with_text(log, status_text, f"Questions generated", emoji=status_emoji, level="INFO")
        log.info(f"    - Total: {metrics['total_questions']} questions")
        log.info(f"    - Multiple choice: {metrics['mc_questions']} (valid structure: {metrics.get('mc_questions_valid', 0)}, with 4 options: {metrics.get('mc_questions_with_4_options', 0)})")
        log.info(f"    - Answers: {metrics['answers_provided']}, Explanations: {metrics['explanations_provided']}")
        log_status_with_text(log, severity_text, f"Question marks: {metrics.get('question_marks', 0)} total, {metrics.get('questions_with_marks', 0)} questions with '?'", emoji=severity_emoji, level="INFO")
        if metrics.get('question_lengths'):
            log.info(f"    - Question length: avg {metrics.get('avg_question_length', 0)} words (range: {metrics.get('min_question_length', 0)}-{metrics.get('max_question_length', 0)})")
        if metrics.get('mc_questions_with_proper_explanations', 0) > 0:
            log.info(f"    - MC explanations: {metrics.get('mc_questions_with_proper_explanations', 0)}/{metrics.get('explanations_provided', 0)} have proper length (20-50 words)")
        if critical_issues:
            log.warning(f"    - Critical issues: {len(critical_issues)} issues requiring attention")
    
    elif content_type == "study_notes":
        log_status_with_text(log, status_text, f"Study notes generated", emoji=status_emoji, level="INFO")
        log.info(f"    - Length: {metrics['char_count']} chars, {metrics['word_count']} words")
        
        # Show requirements if available
        if 'requirements' in metrics:
            reqs = metrics['requirements']
            log.info(f"    - Requirements: {reqs.get('key_concepts_range', 'N/A')} key concepts, max {reqs.get('max_word_count', 'N/A')} words")
        
        log.info(f"    - Key concepts: {metrics['key_concepts']}")
        log.info(f"    - Structure: {metrics['sections']} sections, {metrics['bullet_points']} bullets")
    
    elif content_type == "application":
        log_status_with_text(log, status_text, f"Application generated", emoji=status_emoji, level="INFO")
        log.info(f"    - Length: {metrics['char_count']} chars, {metrics['word_count']} words")
        
        # Show requirements if available
        if 'requirements' in metrics:
            reqs = metrics['requirements']
            log.info(f"    - Requirements: {reqs.get('applications_range', 'N/A')} applications, {reqs.get('words_per_application_range', 'N/A')} words each, max {reqs.get('max_total_words', 'N/A')} total words")
        
        log.info(f"    - Applications: {metrics['applications']}")
        if metrics.get('words_per_application'):
            avg_words = sum(metrics['words_per_application']) / len(metrics['words_per_application'])
            log.info(f"    - Avg words per application: {avg_words:.0f}")
    
    elif content_type == "extension":
        log_status_with_text(log, status_text, f"Extension generated", emoji=status_emoji, level="INFO")
        log.info(f"    - Length: {metrics['char_count']} chars, {metrics['word_count']} words")
        
        # Show requirements if available
        if 'requirements' in metrics:
            reqs = metrics['requirements']
            log.info(f"    - Requirements: {reqs.get('topics_range', 'N/A')} topics, {reqs.get('words_per_topic_range', 'N/A')} words each, max {reqs.get('max_total_words', 'N/A')} total words")
        
        log.info(f"    - Topics: {metrics['topics']}")
        if metrics.get('words_per_topic'):
            avg_words = sum(metrics['words_per_topic']) / len(metrics['words_per_topic'])
            log.info(f"    - Avg words per topic: {avg_words:.0f}")
    
    elif content_type == "diagram" or content_type == "visualization":
        # Determine severity of issues
        critical_issues = []
        warnings_list = metrics.get('warnings', [])
        mermaid_warnings = metrics.get('mermaid_warnings', [])
        all_warnings = warnings_list + mermaid_warnings
        
        for warning in all_warnings:
            if any(keyword in warning.lower() for keyword in ['missing diagram type', 'no connections found', 'no nodes found', 'only', 'require at least']):
                critical_issues.append(warning)
        
        # Determine severity indicator with text labels
        if critical_issues:
            severity_text = "CRITICAL"
            severity_emoji = "🔴"
        elif all_warnings:
            severity_text = "WARNING"
            severity_emoji = "⚠️"
        else:
            severity_text = "OK"
            severity_emoji = "✓"
        
        log_status_with_text(log, status_text, f"Diagram generated", emoji=status_emoji, level="INFO")
        log.info(f"    - Length: {metrics['char_count']} chars (cleaned: {metrics.get('cleaned_char_count', metrics['char_count'])} chars)")
        
        # Show requirements if available
        if 'requirements' in metrics:
            reqs = metrics['requirements']
            log.info(f"    - Requirements: min {reqs.get('min_diagram_elements', 'N/A')} diagram elements")
        
        log_status_with_text(log, severity_text, f"Elements: {metrics['total_elements']} total (nodes: {metrics['nodes']}, connections: {metrics['connections']})", emoji=severity_emoji, level="INFO")
        if metrics.get('mermaid_warnings'):
            log.warning(f"    - Mermaid syntax warnings: {len(metrics['mermaid_warnings'])} issues fixed (code fences, style commands)")
        if critical_issues:
            log.warning(f"    - Critical issues: {len(critical_issues)} structural problems requiring attention")
    
    elif content_type == "integration":
        log_status_with_text(log, status_text, f"Integration generated", emoji=status_emoji, level="INFO")
        log.info(f"    - Length: {metrics['char_count']} chars, {metrics['word_count']} words")
        
        # Show requirements if available
        if 'requirements' in metrics:
            reqs = metrics['requirements']
            log.info(f"    - Requirements: min {reqs.get('min_connections', 'N/A')} connections, max {reqs.get('max_total_words', 'N/A')} words")
        
        log.info(f"    - Connections: {metrics['connections']}")
        log.info(f"    - Structure: {metrics['sections']} sections")
    
    elif content_type == "investigation":
        log_status_with_text(log, status_text, f"Investigation generated", emoji=status_emoji, level="INFO")
        log.info(f"    - Length: {metrics['char_count']} chars, {metrics['word_count']} words")
        
        # Show requirements if available
        if 'requirements' in metrics:
            reqs = metrics['requirements']
            log.info(f"    - Requirements: min {reqs.get('min_questions', 'N/A')} questions, max {reqs.get('max_total_words', 'N/A')} words")
        
        log.info(f"    - Research questions: {metrics['questions']}")
        log.info(f"    - Structure: {metrics['sections']} sections")
    
    elif content_type == "open_questions":
        log_status_with_text(log, status_text, f"Open questions generated", emoji=status_emoji, level="INFO")
        log.info(f"    - Length: {metrics['char_count']} chars, {metrics['word_count']} words")
        
        # Show requirements if available
        if 'requirements' in metrics:
            reqs = metrics['requirements']
            log.info(f"    - Requirements: min {reqs.get('min_questions', 'N/A')} questions, max {reqs.get('max_total_words', 'N/A')} words")
        
        log.info(f"    - Open questions: {metrics['questions']}")
        log.info(f"    - Structure: {metrics['sections']} sections")
    
    # Log warnings if any (with text labels for accessibility)
    if metrics.get('warnings'):
        for warning in metrics['warnings']:
            log_status_with_text(log, "WARNING", warning, emoji="⚠️", level="WARNING")
        
        # Add helpful documentation reference for significant issues
        if content_type in ["lecture", "study_notes", "questions", "application", "extension", "visualization", "integration", "investigation", "open_questions"]:
            if any("below minimum" in w or "exceeds maximum" in w or "Missing" in w or "Only" in w or "Too many" in w for w in metrics.get('warnings', [])):
                log.info(f"    💡 Tip: See docs/FORMATS.md → Validation and Quality Checks for guidance")
                log.info(f"    💡 Tip: Consider regenerating if issues are significant (validation is conservative)")






