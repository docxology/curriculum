"""Post-generation content cleanup and validation.

This module provides utilities to clean up LLM-generated content by removing
conversational artifacts and standardizing placeholders for professional use.
"""

import logging
import re
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

# Conversational patterns to remove
CONVERSATIONAL_PATTERNS = [
    r"^Okay,?\s+here'?s?\s+",
    r"^Alright,?\s+",
    r"^Sure,?\s+",
    r"Would you like\s+.*\?",  # Matches "Would you like..." with anything after
    r"Do you want me to\s+.*\?",
    r"Let me know if\s+.*",
    r"Let me know\s+.*",  # More general "Let me know"
    r"Feel free to\s+.*",
    r"Please let me know\s+.*",
    r"I can\s+.*if you'?d like",
    r"Should I\s+.*\?",
    r"Shall I\s+.*\?",
    r"^Okay,?\s+I\s+understand\s+.*",  # "Okay, I understand the requirements..."
    r"^I\s+have\s+carefully\s+adhered\s+.*",  # "I have carefully adhered to all formatting instructions..."
    r"^the\s+output\s+following\s+.*",  # "the output following the provided requirements..."
    r"^the\s+response\s+adhering\s+.*",  # "the response adhering to all the provided requirements..."
    r"I\s+trust\s+this\s+response\s+.*",  # "I trust this response fulfills all requirements"
    r"Do\s+you\s+have\s+any\s+further\s+.*",  # "Do you have any further instructions..."
]

# Specific name patterns to replace (support Unicode characters in names)
INSTRUCTOR_PATTERNS = [
    # Match Dr. + Unicode letters (José García, etc.)
    r"Dr\.\s+[A-ZÀ-ÖØ-Þ][a-zà-öø-ÿ]+(?:\s+[A-ZÀ-ÖØ-Þ][a-zà-öø-ÿ]+)?(?:,?\s+PhD)?(?:\s+\d+)?",
    # Match Professor + Unicode letters
    r"Professor\s+[A-ZÀ-ÖØ-Þ][a-zà-öø-ÿ]+(?:\s+[A-ZÀ-ÖØ-Þ][a-zà-öø-ÿ]+)?(?:\s+\d+)?",
]

# Date patterns to replace
DATE_PATTERNS = [
    r"(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}",
    r"\d{1,2}/\d{1,2}/\d{4}",
    r"\d{4}-\d{2}-\d{2}",
]

# Word count patterns to remove (LLM-generated word count statements)
WORD_COUNT_PATTERNS = [
    # "Word Count: X words" or "Word Count (Final): X"
    r"(?i)^\s*\*?\*?Word\s+Count\s*(?:\(Final\))?:?\s*\*?\*?\s*\d+\s*(?:words?|chars?|characters?)?\s*$",
    # "**Word Count:** X words"
    r"(?i)^\s*\*\*Word\s+Count\*\*:?\s*\d+\s*(?:words?|chars?|characters?)?\s*$",
    # "Word count: approximately X"
    r"(?i)^\s*Word\s+count:?\s*(?:approximately|approx\.?|~)?\s*\d+\s*(?:words?|chars?|characters?)?\s*$",
    # "Total words: X" or "Total: X words"
    r"(?i)^\s*\*?\*?Total\s+(?:words?|word\s+count):?\s*\*?\*?\s*\d+\s*(?:words?|chars?|characters?)?\s*$",
    # Standalone word count lines at end of file
    r"(?i)^\s*---\s*$\s*(?:Word\s+Count|Total\s+words?):?\s*\d+\s*(?:words?|chars?|characters?)?\s*$",
    # Word count in parentheses or brackets
    r"(?i)\(Word\s+Count:?\s*\d+\s*(?:words?|chars?|characters?)?\)",
    r"(?i)\[Word\s+Count:?\s*\d+\s*(?:words?|chars?|characters?)?\]",
]


def clean_conversational_artifacts(content: str) -> str:
    """Remove conversational phrases from generated content.
    
    Args:
        content: Raw content from LLM
        
    Returns:
        Cleaned content with conversational artifacts removed
    """
    cleaned = content
    changes_made = 0
    
    for pattern in CONVERSATIONAL_PATTERNS:
        matches = re.findall(pattern, cleaned, flags=re.IGNORECASE | re.MULTILINE)
        if matches:
            changes_made += len(matches)
            cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE | re.MULTILINE)
    
    if changes_made > 0:
        logger.debug(f"Removed {changes_made} conversational artifacts")
    
    return cleaned


def standardize_placeholders(content: str) -> str:
    """Replace specific names/dates with generic placeholders.
    
    Args:
        content: Content with specific names/dates
        
    Returns:
        Content with standardized placeholders
    """
    cleaned = content
    changes_made = 0
    
    # Replace instructor names
    for pattern in INSTRUCTOR_PATTERNS:
        matches = re.findall(pattern, cleaned)
        if matches:
            changes_made += len(matches)
            cleaned = re.sub(pattern, "[INSTRUCTOR]", cleaned)
    
    # Replace specific dates
    for pattern in DATE_PATTERNS:
        matches = re.findall(pattern, cleaned)
        if matches:
            changes_made += len(matches)
            cleaned = re.sub(pattern, "[DATE]", cleaned)
    
    if changes_made > 0:
        logger.debug(f"Standardized {changes_made} placeholders")
    
    return cleaned


def remove_duplicate_headings(content: str) -> str:
    """Remove duplicate markdown headings at the same level.
    
    Detects duplicate headings (e.g., "## Key Concepts" appearing twice)
    and removes duplicates, keeping the first occurrence and its content.
    
    Args:
        content: Content that may contain duplicate headings
        
    Returns:
        Content with duplicate headings removed
    """
    if not content:
        return content
    
    lines = content.split('\n')
    seen_headings = {}  # Map of (level, text) -> first occurrence line number
    filtered_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # Check if this is a markdown heading
        heading_match = re.match(r'^(#{1,6})\s+(.+)$', stripped)
        
        if heading_match:
            level = len(heading_match.group(1))
            heading_text = heading_match.group(2).strip()
            heading_key = (level, heading_text.lower())
            
            # Check if we've seen this heading before
            if heading_key in seen_headings:
                # This is a duplicate - skip it and its content until next heading of same or higher level
                logger.debug(f"Removed duplicate heading: {stripped}")
                i += 1
                # Skip content until we hit a heading of same or higher level, or end of file
                while i < len(lines):
                    next_line = lines[i]
                    next_stripped = next_line.strip()
                    next_heading_match = re.match(r'^(#{1,6})\s+', next_stripped)
                    
                    if next_heading_match:
                        next_level = len(next_heading_match.group(1))
                        # If it's same or higher level, stop skipping
                        if next_level <= level:
                            break
                    i += 1
                # Don't increment i here, we want to process the next heading
                continue
            else:
                # First occurrence - record it and include it
                seen_headings[heading_key] = i
                filtered_lines.append(line)
        else:
            # Not a heading - include it
            filtered_lines.append(line)
        
        i += 1
    
    cleaned = '\n'.join(filtered_lines)
    
    # Clean up multiple consecutive blank lines that may result
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    
    return cleaned


def remove_word_count_statements(content: str) -> str:
    """Remove LLM-generated word count statements from content.
    
    Removes patterns like:
    - "Word Count: 198 words"
    - "Word Count (Final): 1021"
    - "**Word Count:** X words"
    - "Total words: X"
    - Word count sections at end of files
    
    Args:
        content: Content that may contain word count statements
        
    Returns:
        Content with word count statements removed
    """
    cleaned = content
    changes_made = 0
    
    # Remove word count patterns line by line
    lines = cleaned.split('\n')
    filtered_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        line_stripped = line.strip()
        
        # Check if this line matches a word count pattern
        is_word_count = False
        for pattern in WORD_COUNT_PATTERNS:
            if re.match(pattern, line_stripped, re.IGNORECASE):
                is_word_count = True
                changes_made += 1
                break
        
        # Also check for common word count formats
        if not is_word_count:
            # Pattern: "Word Count: X" or "Word Count (Final): X"
            if re.match(r'(?i)^\s*\*?\*?Word\s+Count\s*(?:\(Final\))?:?\s*\*?\*?\s*\d+', line_stripped):
                is_word_count = True
                changes_made += 1
            # Pattern: "Application N: X words" or "Topic N: X words" at end
            elif re.match(r'(?i)^\s*(?:Application|Topic)\s+\d+:?\s*\d+\s*(?:words?|chars?|characters?)?\s*$', line_stripped):
                # Check if we're near the end of the file (last 10 lines)
                if i >= len(lines) - 10:
                    is_word_count = True
                    changes_made += 1
            # Pattern: standalone number with "words" on next line
            elif re.match(r'(?i)^\s*\d+\s*(?:words?|chars?|characters?)?\s*$', line_stripped):
                # Check if previous line was a word count header
                if i > 0 and re.match(r'(?i)^\s*(?:Word\s+Count|Total|Application|Topic)', lines[i-1].strip()):
                    is_word_count = True
                    changes_made += 1
        
        if not is_word_count:
            filtered_lines.append(line)
        
        i += 1
    
    cleaned = '\n'.join(filtered_lines)
    
    # Remove word count sections that span multiple lines (e.g., "---\nWord Count: X")
    cleaned = re.sub(r'(?i)^---\s*$\s*(?:Word\s+Count|Total\s+words?):?\s*\d+\s*(?:words?|chars?|characters?)?\s*$', '', cleaned, flags=re.MULTILINE)
    
    # Clean up multiple consecutive blank lines that may result
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    
    # Remove trailing whitespace
    cleaned = cleaned.rstrip()
    
    if changes_made > 0:
        logger.debug(f"Removed {changes_made} word count statement(s)")
    
    return cleaned


def validate_content(content: str, content_type: str = "generic") -> Dict[str, any]:
    """Validate generated content for quality issues.
    
    Args:
        content: Content to validate
        content_type: Type of content (lecture, lab, questions, etc.)
        
    Returns:
        Dictionary with validation results and issues found
    """
    issues = []
    
    # Check for conversational artifacts
    for pattern in CONVERSATIONAL_PATTERNS:
        matches = re.findall(pattern, content, flags=re.IGNORECASE | re.MULTILINE)
        if matches:
            issues.append({
                "type": "conversational_artifact",
                "pattern": pattern,
                "count": len(matches),
                "examples": matches[:3]  # Show first 3 examples
            })
    
    # Check for specific names/dates
    for pattern in INSTRUCTOR_PATTERNS:
        matches = re.findall(pattern, content)
        if matches:
            issues.append({
                "type": "specific_name",
                "count": len(matches),
                "examples": matches[:3]
            })
    
    for pattern in DATE_PATTERNS:
        matches = re.findall(pattern, content)
        if matches:
            issues.append({
                "type": "specific_date",
                "count": len(matches),
                "examples": matches[:3]
            })
    
    # Content-type specific validation
    if content_type == "questions":
        # Check for missing answer keys
        question_count = len(re.findall(r"(?:Question|^\d+\.)\s+", content, re.MULTILINE))
        answer_count = len(re.findall(r"\*\*Answer:\*\*", content))
        if question_count > answer_count:
            issues.append({
                "type": "missing_answer_keys",
                "expected": question_count,
                "found": answer_count,
                "missing": question_count - answer_count
            })
    
    return {
        "is_valid": len(issues) == 0,
        "issues_found": len(issues),
        "issues": issues
    }


def full_cleanup_pipeline(content: str, content_type: str = "generic") -> Tuple[str, Dict]:
    """Apply full cleanup pipeline to content.
    
    Args:
        content: Raw content from LLM
        content_type: Type of content for specific validation (e.g., "visualization", "lecture", etc.)
        
    Returns:
        Tuple of (cleaned content, validation results)
    """
    # First validate the raw content
    validation_before = validate_content(content, content_type)
    
    # Apply Mermaid-specific cleanup for visualization/diagram content
    if content_type in ("visualization", "diagram"):
        from src.utils.content_analysis.mermaid import clean_mermaid_diagram
        cleaned = clean_mermaid_diagram(content)
        # Also apply conversational artifact removal (may have artifacts before diagram)
        cleaned = clean_conversational_artifacts(cleaned)
    else:
        # Apply standard cleanup for markdown content
        cleaned = clean_conversational_artifacts(content)
        cleaned = standardize_placeholders(cleaned)
        cleaned = remove_word_count_statements(cleaned)
        
        # Remove duplicate headings for markdown content (not for Mermaid)
        if content_type not in ("visualization", "diagram"):
            cleaned = remove_duplicate_headings(cleaned)
    
    # Validate after cleanup
    validation_after = validate_content(cleaned, content_type)
    
    logger.info(
        f"Cleanup complete: {validation_before['issues_found']} issues before, "
        f"{validation_after['issues_found']} issues after"
    )
    
    return cleaned, validation_after


def batch_validate_materials(materials: Dict[str, str]) -> Dict[str, Dict]:
    """Validate multiple materials at once.
    
    Args:
        materials: Dictionary of {material_type: content}
        
    Returns:
        Dictionary of {material_type: validation_results}
    """
    results = {}
    total_issues = 0
    
    for material_type, content in materials.items():
        validation = validate_content(content, material_type)
        results[material_type] = validation
        total_issues += validation["issues_found"]
    
    logger.info(f"Batch validation: {total_issues} total issues across {len(materials)} materials")
    
    return results


