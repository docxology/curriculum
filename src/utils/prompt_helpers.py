"""Prompt helper utilities for constraint validation and summary generation.

This module provides utilities for:
- Extracting constraint values from configuration
- Generating constraint summary strings for prompts
- Validating constraint consistency across templates
"""

from typing import Dict, Any, List, Optional


def get_constraint_summary(content_type: str, requirements: Dict[str, int]) -> str:
    """Generate a concise constraint summary string for prompts.
    
    Args:
        content_type: Type of content (lecture, study_notes, questions, etc.)
        requirements: Dictionary of requirement values
        
    Returns:
        Formatted constraint summary string
    """
    if content_type == "lecture":
        return (
            f"Word Count: {requirements.get('min_word_count', 1000)}-{requirements.get('max_word_count', 1500)} words | "
            f"Examples: {requirements.get('min_examples', 5)}-{requirements.get('max_examples', 15)} | "
            f"Sections: {requirements.get('min_sections', 4)}-{requirements.get('max_sections', 8)}"
        )
    elif content_type == "study_notes":
        return (
            f"Key Concepts: {requirements.get('min_key_concepts', 3)}-{requirements.get('max_key_concepts', 10)} | "
            f"Max Words: {requirements.get('max_word_count', 1200)}"
        )
    elif content_type == "questions":
        return (
            f"Total Questions: {requirements.get('num_questions', 10)} | "
            f"MC: {requirements.get('mc_count', 5)} | "
            f"SA: {requirements.get('sa_count', 3)} | "
            f"Essay: {requirements.get('essay_count', 2)}"
        )
    else:
        # Generic format
        parts = []
        for key, value in requirements.items():
            if isinstance(value, int):
                parts.append(f"{key}: {value}")
        return " | ".join(parts)


def categorize_warnings(warnings: List[str]) -> Dict[str, List[str]]:
    """Categorize validation warnings by type for targeted feedback.
    
    Args:
        warnings: List of warning messages
        
    Returns:
        Dictionary with categorized warnings:
        - 'critical': Issues that require immediate attention
        - 'format': Format-related issues
        - 'count': Count/completeness issues
        - 'quality': Quality/content issues
    """
    categorized = {
        'critical': [],
        'format': [],
        'count': [],
        'quality': []
    }
    
    critical_keywords = ['missing', 'no', 'rejected', 'critical']
    format_keywords = ['format', 'heading', 'markdown', 'structure']
    count_keywords = ['only', 'require', 'need', 'exceeds', 'too many', 'too few', 'below minimum']
    quality_keywords = ['length', 'word count', 'explanation', 'quality']
    
    for warning in warnings:
        warning_lower = warning.lower()
        # Check quality keywords first (word count is quality-related, not count-related)
        if any(kw in warning_lower for kw in quality_keywords):
            categorized['quality'].append(warning)
        elif any(kw in warning_lower for kw in critical_keywords):
            categorized['critical'].append(warning)
        elif any(kw in warning_lower for kw in format_keywords):
            categorized['format'].append(warning)
        elif any(kw in warning_lower for kw in count_keywords):
            categorized['count'].append(warning)
        else:
            # Default to critical if unclear
            categorized['critical'].append(warning)
    
    return categorized


def generate_retry_feedback(
    warnings: List[str],
    content_type: str,
    requirements: Optional[Dict[str, int]] = None
) -> str:
    """Generate targeted retry feedback based on validation warnings.
    
    Args:
        warnings: List of validation warning messages
        content_type: Type of content being generated
        requirements: Optional requirements dictionary for specific guidance
        
    Returns:
        Formatted feedback string for retry prompt
    """
    if not warnings:
        return ""
    
    categorized = categorize_warnings(warnings)
    
    feedback_parts = []
    
    # Add categorized issues
    if categorized['format']:
        feedback_parts.append("FORMAT ISSUES:\n" + "\n".join(f"  - {w}" for w in categorized['format'][:3]))
    if categorized['count']:
        feedback_parts.append("COUNT/COMPLETENESS ISSUES:\n" + "\n".join(f"  - {w}" for w in categorized['count'][:3]))
    if categorized['quality']:
        feedback_parts.append("QUALITY ISSUES:\n" + "\n".join(f"  - {w}" for w in categorized['quality'][:2]))
    if categorized['critical']:
        feedback_parts.append("CRITICAL ISSUES:\n" + "\n".join(f"  - {w}" for w in categorized['critical'][:3]))
    
    if not feedback_parts:
        return ""
    
    feedback = "\n\n".join(feedback_parts)
    
    # Add specific guidance based on content type
    guidance = []
    if content_type == "questions":
        if any('question marks' in w.lower() or 'format' in w.lower() for w in warnings):
            guidance.append("- Ensure ALL questions use **Question N:** format and end with '?'")
        if any('4 options' in w.lower() or 'mc' in w.lower() for w in warnings):
            guidance.append("- Ensure ALL MC questions have exactly 4 options (A, B, C, D) and include **Explanation:** sections")
        if any('only' in w.lower() or 'require' in w.lower() for w in warnings):
            guidance.append("- Ensure you generate exactly the required number of questions with all required components")
    
    elif content_type == "study_notes":
        if any('key concepts' in w.lower() for w in warnings):
            guidance.append("- Include the required number of key concepts using **Concept Name**: format (colon after bold name)")
            guidance.append("- Format example: - **ATP**: definition (not 'ATP is...' or 'ATP - definition')")
        if any('word count' in w.lower() for w in warnings):
            guidance.append("- Keep total word count within the specified limit")
    
    elif content_type == "lecture":
        if any('word count' in w.lower() for w in warnings):
            guidance.append("- Ensure word count is within the specified range")
        if any('examples' in w.lower() for w in warnings):
            guidance.append("- Include the required number of examples using phrases: 'for example', 'for instance', 'such as'")
            guidance.append("- Make examples specific and concrete")
        if any('sections' in w.lower() for w in warnings):
            guidance.append("- Create the required number of major sections using ## headings (### subsections don't count)")
    
    guidance_text = "\n".join(guidance) if guidance else ""
    
    separator = "═" * 63
    return f"\n\n{separator}\nVALIDATION FEEDBACK FROM PREVIOUS ATTEMPT:\n{separator}\n\nThe previous attempt had these issues:\n{feedback}\n\nCRITICAL FIXES REQUIRED:\n{guidance_text}"


def validate_constraint_consistency(
    requirements: Dict[str, Dict[str, int]],
    content_types: Optional[List[str]] = None
) -> List[str]:
    """Validate that constraints are consistent across content types.
    
    Args:
        requirements: Dictionary of content type requirements
        content_types: Optional list of content types to validate
        
    Returns:
        List of validation issues found (empty if all valid)
    """
    issues = []
    
    if content_types is None:
        content_types = list(requirements.keys())
    
    # Check for reasonable ranges
    for content_type in content_types:
        if content_type not in requirements:
            continue
        
        reqs = requirements[content_type]
        
        # Check min <= max for range constraints
        if 'min_word_count' in reqs and 'max_word_count' in reqs:
            if reqs['min_word_count'] > reqs['max_word_count']:
                issues.append(f"{content_type}: min_word_count ({reqs['min_word_count']}) > max_word_count ({reqs['max_word_count']})")
        
        if 'min_examples' in reqs and 'max_examples' in reqs:
            if reqs['min_examples'] > reqs['max_examples']:
                issues.append(f"{content_type}: min_examples ({reqs['min_examples']}) > max_examples ({reqs['max_examples']})")
        
        if 'min_sections' in reqs and 'max_sections' in reqs:
            if reqs['min_sections'] > reqs['max_sections']:
                issues.append(f"{content_type}: min_sections ({reqs['min_sections']}) > max_sections ({reqs['max_sections']})")
        
        if 'min_key_concepts' in reqs and 'max_key_concepts' in reqs:
            if reqs['min_key_concepts'] > reqs['max_key_concepts']:
                issues.append(f"{content_type}: min_key_concepts ({reqs['min_key_concepts']}) > max_key_concepts ({reqs['max_key_concepts']})")
    
    return issues




