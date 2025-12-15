"""Counting functions for content analysis.

This module provides functions to count various elements in text content,
such as words, sections, examples, definitions, and cross-references.
"""

import re
from typing import Dict, Any


def count_words(text: str) -> int:
    """Count words in text.
    
    Args:
        text: Input text
        
    Returns:
        Number of words
    """
    return len(text.split())


def count_sections(text: str) -> int:
    """Count major sections (## headings).
    
    Args:
        text: Markdown text
        
    Returns:
        Number of major sections
    """
    return len(re.findall(r'^##\s+[^#]', text, re.MULTILINE))


def count_subsections(text: str) -> int:
    """Count subsections (### headings).
    
    Args:
        text: Markdown text
        
    Returns:
        Number of subsections
    """
    return len(re.findall(r'^###\s+[^#]', text, re.MULTILINE))


def count_examples(text: str) -> int:
    """Count concrete examples in text.
    
    Args:
        text: Input text
        
    Returns:
        Number of examples found
    """
    patterns = [
        r'\bfor example\b',
        r'\bfor instance\b',
        r'\bsuch as\b',
        r'\be\.g\.\b',
        r'\be\.g\b',
        r'\bconsider\s+',
        r'\bimagine\s+',
        r'\btake\s+(?:the\s+)?(?:case\s+of|example\s+of)',
        r'\bexample:\s*',
        r'\bexamples?\s+include',
    ]
    count = sum(len(re.findall(p, text, re.IGNORECASE)) for p in patterns)
    return count


def count_definitions(text: str) -> int:
    """Count term definitions (bold terms followed by explanation).
    
    Args:
        text: Markdown text
        
    Returns:
        Number of definitions
    """
    # Look for **term**: definition pattern
    return len(re.findall(r'\*\*[^*]+\*\*:\s+', text))


def count_cross_references(text: str) -> int:
    """Count cross-references to other materials.
    
    Args:
        text: Input text
        
    Returns:
        Number of cross-references
    """
    patterns = [
        r'see\s+(lab|lecture|diagram|section)',
        r'refer\s+to',
        r'→\s*(lab|lecture|diagram)',
        r'\[see\s+',
    ]
    count = sum(len(re.findall(p, text, re.IGNORECASE)) for p in patterns)
    return count






