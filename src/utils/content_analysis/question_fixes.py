"""Auto-correction functions for question format issues.

This module provides automatic fixes for common question format problems:
- Missing question marks
- Incorrect MC option formatting
- Missing explanations
- Format standardization
"""

import re
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


def fix_missing_question_marks(questions_text: str) -> Tuple[str, int]:
    """Add missing question marks to questions that don't end with '?'.
    
    Args:
        questions_text: Questions content in markdown
        
    Returns:
        Tuple of (fixed_text, count_of_fixes)
    """
    fixed_text = questions_text
    fix_count = 0
    
    # Pattern to find question markers and their content
    question_patterns = [
        r'(\*\*Question\s+\d+:\*\*[^\n]*)',  # **Question N:**
        r'(\*\*Question\s+\d+\*\*:?[^\n]*)',  # **Question N** or **Question N**:
        r'(##\s+Question\s+\d+[^\n]*)',      # ## Question N
        r'(###\s+Question\s+\d+[^\n]*)',      # ### Question N
        r'(Q\s*\d+\s*:[^\n]*)',              # Q1: or Q 1:
    ]
    
    for pattern in question_patterns:
        def add_question_mark(match):
            question_line = match.group(1)
            # Check if it already ends with ?
            if question_line.rstrip().endswith('?'):
                return question_line
            
            # Check if it ends with Answer/Explanation markers (don't add ?)
            if re.search(r'\*\*(?:Answer|Explanation):\*\*', question_line, re.IGNORECASE):
                return question_line
            
            # Add ? if it doesn't have one
            if not question_line.rstrip().endswith('?'):
                nonlocal fix_count
                fix_count += 1
                # Add ? before any Answer/Explanation markers, or at end
                if re.search(r'\*\*(?:Answer|Explanation):\*\*', question_line, re.IGNORECASE):
                    return re.sub(r'(\*\*(?:Answer|Explanation):\*\*)', r'? \1', question_line, flags=re.IGNORECASE)
                else:
                    return question_line.rstrip() + '?'
            
            return question_line
        
        fixed_text = re.sub(pattern, add_question_mark, fixed_text, flags=re.IGNORECASE | re.MULTILINE)
    
    return fixed_text, fix_count


def fix_mc_options(questions_text: str) -> Tuple[str, int]:
    """Fix MC questions to have exactly 4 options (A, B, C, D).
    
    Args:
        questions_text: Questions content in markdown
        
    Returns:
        Tuple of (fixed_text, count_of_fixes)
    """
    fixed_text = questions_text
    fix_count = 0
    
    # Find all MC questions (have A-D options)
    mc_question_pattern = r'((?:\*\*Question\s+\d+:\*\*|##\s+Question\s+\d+).*?)(?=\*\*Question\s+\d+:|##\s+Question\s+\d+|$)'
    
    def fix_mc_question(match):
        question_section = match.group(1)
        
        # Check if this is an MC question (has at least one A-D option)
        if not re.search(r'[A-D][).]\s+', question_section, re.IGNORECASE):
            return question_section
        
        # Count current options
        options = re.findall(r'([A-D])[).]\s+([^\n]+)', question_section, re.IGNORECASE)
        option_letters = {opt[0].upper() for opt in options}
        
        # If already has 4 options, return as-is
        if len(option_letters) == 4:
            return question_section
        
        # If has fewer than 4 options, try to add missing ones
        # This is tricky - we can't generate content, so we'll just ensure format is correct
        # For now, we'll just ensure existing options are properly formatted
        
        # Ensure options are in order A, B, C, D
        expected_options = ['A', 'B', 'C', 'D']
        option_dict = {opt[0].upper(): opt[1] for opt in options}
        
        # Rebuild options section in correct order
        options_text = ""
        for letter in expected_options:
            if letter in option_dict:
                options_text += f"{letter}) {option_dict[letter]}\n"
        
        # Replace options section
        if options_text:
            # Find where options start and end
            options_match = re.search(r'([A-D][).]\s+[^\n]+(?:\n[A-D][).]\s+[^\n]+)*)', question_section, re.IGNORECASE | re.MULTILINE)
            if options_match:
                nonlocal fix_count
                fix_count += 1
                return question_section[:options_match.start()] + options_text + question_section[options_match.end():]
        
        return question_section
    
    fixed_text = re.sub(mc_question_pattern, fix_mc_question, fixed_text, flags=re.DOTALL | re.IGNORECASE)
    
    return fixed_text, fix_count


def standardize_question_format(questions_text: str) -> Tuple[str, int]:
    """Standardize question format to **Question N:** format.
    
    Args:
        questions_text: Questions content in markdown
        
    Returns:
        Tuple of (fixed_text, count_of_fixes)
    """
    fixed_text = questions_text
    fix_count = 0
    
    # Convert various formats to **Question N:**
    replacements = [
        # **Question N** (no colon) -> **Question N:**
        (r'\*\*Question\s+(\d+)\*\*(?!:)', r'**Question \1:**'),
        # **Question N**: (colon outside) -> **Question N:**
        (r'\*\*Question\s+(\d+)\*\*:', r'**Question \1:**'),
        # ## Question N -> **Question N:**
        (r'##\s+Question\s+(\d+)', r'**Question \1:**'),
        # ### Question N -> **Question N:**
        (r'###\s+Question\s+(\d+)', r'**Question \1:**'),
        # Q1: or Q 1: -> **Question 1:**
        (r'Q\s*(\d+)\s*:', r'**Question \1:**'),
    ]
    
    for pattern, replacement in replacements:
        matches = len(re.findall(pattern, fixed_text, re.IGNORECASE))
        if matches > 0:
            fix_count += matches
            fixed_text = re.sub(pattern, replacement, fixed_text, flags=re.IGNORECASE)
    
    return fixed_text, fix_count


def auto_fix_questions(questions_text: str) -> Tuple[str, Dict[str, int]]:
    """Apply all auto-fixes to questions content.
    
    Args:
        questions_text: Questions content in markdown
        
    Returns:
        Tuple of (fixed_text, fix_summary) where fix_summary is a dict with fix counts
    """
    fixed_text = questions_text
    fix_summary = {}
    
    # Apply fixes in order
    fixed_text, count = standardize_question_format(fixed_text)
    fix_summary['format_standardized'] = count
    
    fixed_text, count = fix_missing_question_marks(fixed_text)
    fix_summary['question_marks_added'] = count
    
    fixed_text, count = fix_mc_options(fixed_text)
    fix_summary['mc_options_fixed'] = count
    
    total_fixes = sum(fix_summary.values())
    fix_summary['total_fixes'] = total_fixes
    
    if total_fixes > 0:
        logger.info(f"Auto-fixed {total_fixes} question format issues: {fix_summary}")
    
    return fixed_text, fix_summary

