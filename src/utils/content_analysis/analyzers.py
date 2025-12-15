"""Content analysis functions for different content types.

This module provides comprehensive analysis functions for lectures, labs,
questions, study notes, and other content types.
"""

import re
import logging
from typing import Dict, Any, List, Optional

from src.utils.content_analysis.counters import (
    count_words,
    count_sections,
    count_subsections,
    count_examples,
    count_definitions,
    count_cross_references,
)
from src.utils.content_analysis.mermaid import validate_mermaid_syntax

logger = logging.getLogger(__name__)


def analyze_lecture(lecture_text: str, requirements: Dict[str, int] = None) -> Dict[str, Any]:
    """Comprehensive lecture content analysis.
    
    Args:
        lecture_text: Lecture content in markdown
        requirements: Optional dict with min_word_count, max_word_count, min_examples, max_examples, min_sections, max_sections
        
    Returns:
        Dictionary with analysis metrics
    """
    # Use provided requirements or defaults
    if requirements is None:
        requirements = {}
    min_word_count = requirements.get('min_word_count', 1000)
    max_word_count = requirements.get('max_word_count', 1500)
    min_examples = requirements.get('min_examples', 5)
    max_examples = requirements.get('max_examples', 15)
    min_sections = requirements.get('min_sections', 4)
    max_sections = requirements.get('max_sections', 8)
    
    metrics = {
        'word_count': count_words(lecture_text),
        'char_count': len(lecture_text),
        'sections': count_sections(lecture_text),
        'subsections': count_subsections(lecture_text),
        'examples': count_examples(lecture_text),
        'terms': count_definitions(lecture_text),
        'cross_refs': count_cross_references(lecture_text),
    }
    
    # Quality warnings (check both min and max constraints)
    warnings = []
    if metrics['word_count'] < min_word_count:
        shortfall = min_word_count - metrics['word_count']
        warnings.append(f"Word count ({metrics['word_count']}) below minimum {min_word_count} (need {shortfall} more words - consider regenerating or expanding content)")
    elif metrics['word_count'] > max_word_count:
        excess = metrics['word_count'] - max_word_count
        warnings.append(f"Word count ({metrics['word_count']}) exceeds maximum {max_word_count} (exceeds by {excess} words - consider condensing or splitting)")
    
    if metrics['examples'] < min_examples:
        needed = min_examples - metrics['examples']
        warnings.append(f"Only {metrics['examples']} examples found (require {min_examples}-{max_examples}, need {needed} more - add concrete examples)")
    elif metrics['examples'] > max_examples:
        excess = metrics['examples'] - max_examples
        warnings.append(f"Too many examples ({metrics['examples']}, maximum {max_examples}, {excess} excess - consider consolidating or removing less critical examples)")
    
    if metrics['sections'] < min_sections:
        needed = min_sections - metrics['sections']
        warnings.append(f"Only {metrics['sections']} major sections (require {min_sections}-{max_sections}, need {needed} more - add section breaks with ## headings)")
    elif metrics['sections'] > max_sections:
        excess = metrics['sections'] - max_sections
        warnings.append(f"Too many sections ({metrics['sections']}, maximum {max_sections}, {excess} excess - consider merging related sections)")
    
    metrics['warnings'] = warnings
    metrics['requirements'] = {
        'word_count_range': f"{min_word_count}-{max_word_count}",
        'examples_range': f"{min_examples}-{max_examples}",
        'sections_range': f"{min_sections}-{max_sections}"
    }
    return metrics


def analyze_lab(lab_text: str) -> Dict[str, Any]:
    """Comprehensive lab content analysis.
    
    Analyzes lab content for procedure steps, safety warnings, materials, and tables.
    
    Expected format:
        # Lab Title
        ## Materials
        - Item 1
        - Item 2
        
        ## Procedure
        1. First step
        2. Second step
        ⚠️ Safety warning
        
        ## Data Collection
        | Measurement | Value |
        |-------------|-------|
    
    Args:
        lab_text: Lab content in markdown
        
    Returns:
        Dictionary with analysis metrics including:
        - word_count: Total word count
        - procedure_steps: Number of numbered procedure steps
        - safety_warnings: Number of safety warnings found
        - materials_count: Number of material list items
        - tables: Number of markdown tables
        - warnings: List of validation warnings
    """
    metrics = {
        'word_count': count_words(lab_text),
        'char_count': len(lab_text),
        'procedure_steps': len(re.findall(r'^\s*\d+\.\s+', lab_text, re.MULTILINE)),
        'safety_warnings': len(re.findall(r'⚠️|WARNING|CAUTION|Safety', lab_text, re.IGNORECASE)),
        'materials_count': len(re.findall(r'^\s*[-*]\s+', lab_text, re.MULTILINE)),
        'tables': len(re.findall(r'^\|[^|]+\|', lab_text, re.MULTILINE)),
    }
    
    # Quality warnings
    warnings = []
    if metrics['procedure_steps'] < 5:
        needed = 5 - metrics['procedure_steps']
        warnings.append(f"Only {metrics['procedure_steps']} procedure steps (recommend 8+, need {needed} more - break down complex steps)")
    if metrics['safety_warnings'] == 0:
        warnings.append("No safety warnings found (add ⚠️ or WARNING sections for hazardous materials/procedures)")
    if metrics['tables'] == 0:
        warnings.append("No data collection tables found (add markdown tables for observations/measurements)")
    
    metrics['warnings'] = warnings
    return metrics


def analyze_questions(questions_text: str) -> Dict[str, Any]:
    """Comprehensive questions content analysis.
    
    Supports multiple question formats:
    - **Question 1:** (colon inside bold markers) - PREFERRED/ACTUAL FORMAT
    - **Question 1** (without colon)
    - **Question 1**: (colon after bold markers)
    - ## Question 1 (markdown heading)
    - Q1: or Q 1: (abbreviated format)
    - 1. (numbered list)
    - 1) (numbered list with parenthesis)
    
    Examples:
        **Question 1:** What is DNA?
        **Question 2:** Explain the process.
        ## Question 3: Multiple choice question
    
    Args:
        questions_text: Questions content in markdown
        
    Returns:
        Dictionary with analysis metrics including:
        - total_questions: Number of unique questions detected
        - mc_questions: Number of multiple choice questions
        - answers_provided: Number of answer sections found
        - explanations_provided: Number of explanation sections found
        - question_marks: Total count of "?" characters
        - questions_with_marks: Number of questions ending with "?"
        - mc_questions_valid: Number of MC questions with proper A-D options
        - question_lengths: List of word counts per question
        - warnings: List of validation warnings
    """
    # Pattern 1a: **Question N:** (colon inside bold markers) - ACTUAL FORMAT
    pattern1a = r'\*\*Question\s+\d+:\*\*'
    
    # Pattern 1b: **Question N** (without colon)
    pattern1b = r'\*\*Question\s+\d+\*\*'
    
    # Pattern 1c: **Question N**: (colon after bold markers)
    pattern1c = r'\*\*Question\s+\d+\*\*:'
    
    # Pattern 2: ## Question N (markdown heading)
    pattern2 = r'##\s+Question\s+\d+'
    
    # Pattern 3: Q1: or Q 1: (abbreviated format)
    pattern3 = r'Q\s*\d+\s*:'
    
    # Pattern 4: Numbered list (1. or 1) followed by question-like text ending with ?)
    pattern4 = r'^\s*\d+[.)]\s+.*\?'
    
    # Pattern 5: ### Question N (subsection heading)
    pattern5 = r'###\s+Question\s+\d+'
    
    # Combine all patterns and deduplicate by extracting question numbers
    all_matches = (
        re.findall(pattern1a, questions_text, re.IGNORECASE) +
        re.findall(pattern1b, questions_text, re.IGNORECASE) +
        re.findall(pattern1c, questions_text, re.IGNORECASE) +
        re.findall(pattern2, questions_text, re.IGNORECASE) +
        re.findall(pattern3, questions_text, re.IGNORECASE) +
        re.findall(pattern4, questions_text, re.MULTILINE) +
        re.findall(pattern5, questions_text, re.IGNORECASE)
    )
    
    # Extract question numbers to deduplicate
    question_numbers = set()
    for match in all_matches:
        # Extract number from various formats
        num_match = re.search(r'\d+', str(match))
        if num_match:
            question_numbers.add(int(num_match.group()))
    
    # Use unique question count (more accurate)
    total_questions = len(question_numbers) if question_numbers else len(all_matches)
    
    # Question mark counting - comprehensive validation
    total_question_marks = questions_text.count('?')
    
    # Extract individual questions and analyze them
    # Find all question markers and extract their content
    # Use regex to find question markers and their following content
    question_marker_pattern = r'(?:\*\*Question\s+\d+:\*\*|\*\*Question\s+\d+\*\*:?|##\s+Question\s+\d+|###\s+Question\s+\d+|Q\s*\d+\s*:)'
    
    questions_with_marks = 0
    question_lengths = []
    mc_questions_valid = 0
    mc_questions_with_4_options = 0
    mc_questions_with_proper_explanations = 0
    mc_option_counts = []  # Track option counts per MC question
    explanation_lengths = []  # Track explanation word counts
    
    # Find all question markers and extract content after each
    question_matches = list(re.finditer(question_marker_pattern, questions_text, flags=re.IGNORECASE))
    
    for i, match in enumerate(question_matches):
        # Get content from this question marker to next marker (or end)
        start_pos = match.end()
        if i + 1 < len(question_matches):
            end_pos = question_matches[i + 1].start()
        else:
            end_pos = len(questions_text)
        
        question_section = questions_text[start_pos:end_pos]
        
        # Extract just the question text (before Answer/Explanation)
        question_text = re.split(r'\*\*(?:Answer|Explanation):\*\*', question_section, flags=re.IGNORECASE)[0]
        
        # Remove MC options if present (A), B), C), D))
        question_text_clean = re.sub(r'[A-D][).]\s+[^\n]+\n?', '', question_text, flags=re.IGNORECASE | re.MULTILINE)
        question_text_clean = question_text_clean.strip()
        
        # Check if question ends with "?"
        if question_text_clean.endswith('?'):
            questions_with_marks += 1
        
        # Count words in question
        question_words = count_words(question_text_clean)
        if question_words > 0:
            question_lengths.append(question_words)
        
        # Check for MC question structure: should have A), B), C), D) options
        if re.search(r'[A-D][).]\s+', question_section, re.IGNORECASE):
            # Validate it has exactly 4 options (A, B, C, D)
            option_count = len(re.findall(r'[A-D][).]\s+', question_section, re.IGNORECASE))
            # Check for all 4 options (A, B, C, D)
            options_found = set(re.findall(r'([A-D])[).]\s+', question_section, re.IGNORECASE))
            mc_option_counts.append(option_count)
            
            if option_count >= 2:
                mc_questions_valid += 1
            
            # Check for exactly 4 options
            if option_count == 4 and len(options_found) == 4:
                mc_questions_with_4_options += 1
            
            # Check explanation length for MC questions
            explanation_match = re.search(r'\*\*Explanation:\*\*\s*(.+?)(?=\*\*|$)', question_section, re.IGNORECASE | re.DOTALL)
            if explanation_match:
                explanation_text = explanation_match.group(1).strip()
                explanation_words = count_words(explanation_text)
                explanation_lengths.append(explanation_words)
                # MC explanations should be 2-3 sentences (roughly 20-50 words)
                if 20 <= explanation_words <= 50:
                    mc_questions_with_proper_explanations += 1
    
    # Multiple choice detection: Questions with A-D options
    # Look for question markers followed by A), B), C), D) options
    # Updated to include all question format patterns
    mc_pattern = r'(?:\*\*Question\s+\d+:\*\*|\*\*Question\s+\d+\*\*:?|##\s+Question\s+\d+).*?[A-D][).]\s+'
    mc_questions = len(re.findall(mc_pattern, questions_text, re.DOTALL | re.IGNORECASE))
    
    # Answer detection: **Answer:** or **Answer:** (case insensitive)
    answers = len(re.findall(r'\*\*Answer:\*\*', questions_text, re.IGNORECASE))
    
    # Explanation detection: **Explanation:** (case insensitive)
    explanations = len(re.findall(r'\*\*Explanation:\*\*', questions_text, re.IGNORECASE))
    
    # Calculate average question length
    avg_question_length = sum(question_lengths) / len(question_lengths) if question_lengths else 0
    min_question_length = min(question_lengths) if question_lengths else 0
    max_question_length = max(question_lengths) if question_lengths else 0
    
    metrics = {
        'word_count': count_words(questions_text),
        'char_count': len(questions_text),
        'total_questions': total_questions,
        'mc_questions': mc_questions,
        'mc_questions_valid': mc_questions_valid,
        'mc_questions_with_4_options': mc_questions_with_4_options,
        'mc_questions_with_proper_explanations': mc_questions_with_proper_explanations,
        'answers_provided': answers,
        'explanations_provided': explanations,
        'question_marks': total_question_marks,
        'questions_with_marks': questions_with_marks,
        'question_lengths': question_lengths,
        'avg_question_length': round(avg_question_length, 1),
        'min_question_length': min_question_length,
        'max_question_length': max_question_length,
        'mc_option_counts': mc_option_counts,
        'explanation_lengths': explanation_lengths,
    }
    
    # Quality warnings - comprehensive validation
    warnings = []
    
    # Check if questions were detected
    if total_questions == 0:
        warnings.append("No questions detected - check question format (expected: **Question N:** or ## Question N) - regenerate with format specification in prompt")
    else:
        # Question mark validation
        if total_question_marks == 0:
            warnings.append("No question marks (?) found - questions should typically end with '?' - check question format")
        elif questions_with_marks < total_questions:
            missing_marks = total_questions - questions_with_marks
            warnings.append(f"Only {questions_with_marks}/{total_questions} questions end with '?' ({missing_marks} missing question marks - ensure questions are properly formatted)")
        
        # Answer validation
        if answers < total_questions:
            missing = total_questions - answers
            warnings.append(f"Missing answers: {missing} questions lack answers (add **Answer:** sections for all questions)")
        
        # Explanation validation for MC questions
        if mc_questions > 0:
            if explanations < mc_questions:
                missing = mc_questions - explanations
                warnings.append(f"Missing explanations: {missing} MC questions lack explanations (add **Explanation:** sections for multiple choice questions)")
            
            # MC question structure validation - check for exactly 4 options
            if mc_questions_with_4_options < mc_questions:
                invalid = mc_questions - mc_questions_with_4_options
                warnings.append(f"MC option count: {invalid} multiple choice questions do not have exactly 4 options (require A, B, C, D - ensure each MC question has exactly 4 options)")
            
            # MC question structure validation - minimum 2 options
            if mc_questions_valid < mc_questions:
                invalid = mc_questions - mc_questions_valid
                warnings.append(f"MC question structure: {invalid} multiple choice questions may lack proper A-D options (ensure each MC question has at least 2 options labeled A), B), C), D))")
            
            # Explanation length validation
            if explanation_lengths:
                short_explanations = [e for e in explanation_lengths if e < 20]
                long_explanations = [e for e in explanation_lengths if e > 50]
                if short_explanations:
                    warnings.append(f"Explanation length: {len(short_explanations)} MC explanations are too short (<20 words - explanations should be 2-3 sentences, roughly 20-50 words)")
                if long_explanations:
                    warnings.append(f"Explanation length: {len(long_explanations)} MC explanations are too long (>50 words - keep explanations concise, 2-3 sentences)")
            
            if mc_questions_with_proper_explanations < explanations:
                improper = explanations - mc_questions_with_proper_explanations
                if improper > 0:
                    warnings.append(f"Explanation quality: {improper} MC explanations may be too short or too long (target: 2-3 sentences, 20-50 words)")
        
        # Question length validation
        if question_lengths:
            # Questions should be at least 3 words (too short = likely incomplete)
            short_questions = [q for q in question_lengths if q < 3]
            if short_questions:
                warnings.append(f"Question length: {len(short_questions)} questions are very short (<3 words) - may be incomplete or improperly formatted")
            
            # Questions longer than 50 words may be too complex
            long_questions = [q for q in question_lengths if q > 50]
            if long_questions:
                warnings.append(f"Question length: {len(long_questions)} questions are very long (>50 words) - consider breaking into simpler questions")
        
        # Question mark to question ratio validation
        if total_question_marks > 0 and total_questions > 0:
            marks_per_question = total_question_marks / total_questions
            if marks_per_question < 0.8:  # Less than 80% of questions have marks
                warnings.append(f"Question mark ratio: Only {marks_per_question:.1%} of questions have question marks (expected ~100% - ensure questions end with '?')")
            elif marks_per_question > 1.5:  # More than 1.5 marks per question (likely multiple ? in one question)
                warnings.append(f"Question mark ratio: {marks_per_question:.1f} question marks per question (may indicate multiple questions combined or excessive punctuation)")
    
    metrics['warnings'] = warnings
    return metrics


def analyze_study_notes(notes_text: str, requirements: Dict[str, int] = None) -> Dict[str, Any]:
    """Comprehensive study notes content analysis.
    
    Analyzes study notes for key concepts, summaries, and structure.
    
    Expected format:
        # Module Name - Study Notes
        ## Key Concepts
        - **Term 1**: Definition
        - **Term 2**: Definition
        
        ## Summary
        Main points...
    
    Args:
        notes_text: Study notes content in markdown
        requirements: Optional dict with min_key_concepts, max_key_concepts, max_word_count
        
    Returns:
        Dictionary with analysis metrics including:
        - word_count: Total word count
        - key_concepts: Number of key concepts (bold terms with definitions)
        - sections: Number of major sections
        - warnings: List of validation warnings
    """
    # Use provided requirements or defaults
    if requirements is None:
        requirements = {}
    min_key_concepts = requirements.get('min_key_concepts', 3)
    max_key_concepts = requirements.get('max_key_concepts', 10)
    max_word_count = requirements.get('max_word_count', 1200)
    
    # Detect key concepts in multiple formats:
    # 1. Bullet points: - **Concept**: or * **Concept**:
    # 2. Numbered lists: 1. **Concept**: or 1) **Concept**:
    # 3. Paragraphs: **Concept**: (standalone, not in lists)
    # 4. Section headers: ## **Concept**: (less common but possible)
    key_concept_patterns = [
        r'^\s*[-*]\s+\*\*[^*]+\*\*:',  # Bullet points: - **Concept**:
        r'^\s*\d+[.)]\s+\*\*[^*]+\*\*:',  # Numbered lists: 1. **Concept**: or 1) **Concept**:
        r'(?<![-*]\s)(?<!\d[.)]\s)\*\*[^*]+\*\*:\s+',  # Standalone paragraphs: **Concept**: (not preceded by bullet/number)
        r'^##\s+\*\*[^*]+\*\*:',  # Section headers: ## **Concept**:
    ]
    
    # Find all matches and deduplicate by extracting concept names
    all_matches = []
    for pattern in key_concept_patterns:
        matches = re.findall(pattern, notes_text, re.MULTILINE)
        all_matches.extend(matches)
    
    # Extract concept names to deduplicate (same concept might appear in different formats)
    concept_names = set()
    for match in all_matches:
        # Extract the concept name from **Concept**: format
        concept_match = re.search(r'\*\*([^*]+)\*\*:', match)
        if concept_match:
            concept_names.add(concept_match.group(1).strip())
    
    # Use unique concept count (more accurate than raw match count)
    key_concepts_count = len(concept_names) if concept_names else len(all_matches)
    
    metrics = {
        'word_count': count_words(notes_text),
        'char_count': len(notes_text),
        'sections': count_sections(notes_text),
        'key_concepts': key_concepts_count,
        'bullet_points': len(re.findall(r'^\s*[-*]\s+', notes_text, re.MULTILINE)),
        'tables': len(re.findall(r'^\|[^|]+\|', notes_text, re.MULTILINE)),
    }
    
    # Quality warnings (check both min and max constraints)
    warnings = []
    if metrics['word_count'] > max_word_count:
        excess = metrics['word_count'] - max_word_count
        warnings.append(f"Word count ({metrics['word_count']}) exceeds maximum {max_word_count} (exceeds by {excess} words - condense content or remove less critical details)")
    
    if metrics['key_concepts'] < min_key_concepts:
        needed = min_key_concepts - metrics['key_concepts']
        warnings.append(f"Only {metrics['key_concepts']} key concepts highlighted (require {min_key_concepts}-{max_key_concepts}, need {needed} more - format concepts as **Concept Name:** in bullet points)")
    elif metrics['key_concepts'] > max_key_concepts:
        excess = metrics['key_concepts'] - max_key_concepts
        warnings.append(f"Too many key concepts ({metrics['key_concepts']}, maximum {max_key_concepts}, {excess} excess - consolidate related concepts or remove less critical ones)")
    
    metrics['warnings'] = warnings
    metrics['requirements'] = {
        'key_concepts_range': f"{min_key_concepts}-{max_key_concepts}",
        'max_word_count': max_word_count
    }
    return metrics


def analyze_application(content_text: str, requirements: Dict[str, int] = None) -> Dict[str, Any]:
    """Comprehensive application content analysis.
    
    Analyzes real-world application content for structure and completeness.
    
    Expected format:
        # Real-World Applications
        ## Application 1: Title
        Description of application...
        
        ## Application 2: Title
        Description of application...
    
    Args:
        content_text: Application content in markdown
        requirements: Optional dict with min_applications, max_applications, 
            min_words_per_application, max_words_per_application, max_total_words
        
    Returns:
        Dictionary with analysis metrics including:
        - word_count: Total word count
        - applications: Number of application sections found
        - words_per_application: List of word counts per application
        - sections: Number of major sections
        - warnings: List of validation warnings
    """
    # Use provided requirements or defaults
    if requirements is None:
        requirements = {}
    min_applications = requirements.get('min_applications', 3)
    max_applications = requirements.get('max_applications', 5)
    min_words_per_app = requirements.get('min_words_per_application', 150)
    max_words_per_app = requirements.get('max_words_per_application', 200)
    max_total_words = requirements.get('max_total_words', 1000)
    
    # Count applications (## Application N or ## Application 1, etc.)
    application_patterns = [
        r'##\s+Application\s+\d+',
        r'##\s+Real[- ]?World\s+Application\s+\d+',
        r'###\s+Application\s+\d+',
    ]
    applications = len(re.findall('|'.join(application_patterns), content_text, re.IGNORECASE))
    
    # Extract individual application sections and count words per application
    app_sections = re.split(r'##\s+Application\s+\d+', content_text, flags=re.IGNORECASE)
    if len(app_sections) <= 1:
        app_sections = re.split(r'##\s+Real[- ]?World\s+Application\s+\d+', content_text, flags=re.IGNORECASE)
    
    words_per_application = []
    for section in app_sections[1:]:  # Skip header
        words = count_words(section)
        if words > 0:
            words_per_application.append(words)
    
    total_words = count_words(content_text)
    
    metrics = {
        'word_count': total_words,
        'char_count': len(content_text),
        'applications': applications,
        'words_per_application': words_per_application,
        'sections': count_sections(content_text),
    }
    
    # Quality warnings
    warnings = []
    if applications < min_applications:
        needed = min_applications - applications
        warnings.append(f"Only {applications} applications found (require {min_applications}-{max_applications}, need {needed} more - add ## Application N sections)")
    elif applications > max_applications:
        excess = applications - max_applications
        warnings.append(f"Too many applications ({applications}, maximum {max_applications}, {excess} excess - consider consolidating or removing less critical applications)")
    
    if words_per_application:
        for i, word_count in enumerate(words_per_application, 1):
            if word_count < min_words_per_app:
                shortfall = min_words_per_app - word_count
                warnings.append(f"Application {i} has {word_count} words (require {min_words_per_app}-{max_words_per_app}, need {shortfall} more words)")
            elif word_count > max_words_per_app:
                excess = word_count - max_words_per_app
                warnings.append(f"Application {i} has {word_count} words (exceeds {max_words_per_app} by {excess} words - consider condensing)")
    
    if total_words > max_total_words:
        excess = total_words - max_total_words
        warnings.append(f"Total word count ({total_words}) exceeds maximum {max_total_words} (exceeds by {excess} words - condense content)")
    
    metrics['warnings'] = warnings
    metrics['requirements'] = {
        'applications_range': f"{min_applications}-{max_applications}",
        'words_per_application_range': f"{min_words_per_app}-{max_words_per_app}",
        'max_total_words': max_total_words
    }
    return metrics


def analyze_extension(content_text: str, requirements: Dict[str, int] = None) -> Dict[str, Any]:
    """Comprehensive extension content analysis.
    
    Analyzes advanced extension topics for structure and completeness.
    
    Expected format:
        # Advanced Topics
        ## Topic 1: Title
        Advanced content...
        
        ## Topic 2: Title
        Advanced content...
    
    Args:
        content_text: Extension content in markdown
        requirements: Optional dict with min_topics, max_topics, 
            min_words_per_topic, max_words_per_topic, max_total_words
        
    Returns:
        Dictionary with analysis metrics including:
        - word_count: Total word count
        - topics: Number of topic sections found
        - words_per_topic: List of word counts per topic
        - sections: Number of major sections
        - warnings: List of validation warnings
    """
    # Use provided requirements or defaults
    if requirements is None:
        requirements = {}
    min_topics = requirements.get('min_topics', 3)
    max_topics = requirements.get('max_topics', 4)
    min_words_per_topic = requirements.get('min_words_per_topic', 100)
    max_words_per_topic = requirements.get('max_words_per_topic', 150)
    max_total_words = requirements.get('max_total_words', 600)
    
    # Count topics (## Topic N or ## Advanced Topic N, etc.)
    topic_patterns = [
        r'##\s+(?:Advanced\s+)?Topic\s+\d+',
        r'##\s+Extension\s+\d+',
        r'###\s+(?:Advanced\s+)?Topic\s+\d+',
    ]
    topics = len(re.findall('|'.join(topic_patterns), content_text, re.IGNORECASE))
    
    # Extract individual topic sections
    topic_sections = re.split(r'##\s+(?:Advanced\s+)?Topic\s+\d+', content_text, flags=re.IGNORECASE)
    if len(topic_sections) <= 1:
        topic_sections = re.split(r'##\s+Extension\s+\d+', content_text, flags=re.IGNORECASE)
    
    words_per_topic = []
    for section in topic_sections[1:]:  # Skip header
        words = count_words(section)
        if words > 0:
            words_per_topic.append(words)
    
    total_words = count_words(content_text)
    
    metrics = {
        'word_count': total_words,
        'char_count': len(content_text),
        'topics': topics,
        'words_per_topic': words_per_topic,
        'sections': count_sections(content_text),
    }
    
    # Quality warnings
    warnings = []
    if topics < min_topics:
        needed = min_topics - topics
        warnings.append(f"Only {topics} topics found (require {min_topics}-{max_topics}, need {needed} more - add ## Topic N sections)")
    elif topics > max_topics:
        excess = topics - max_topics
        warnings.append(f"Too many topics ({topics}, maximum {max_topics}, {excess} excess - consider consolidating or removing less critical topics)")
    
    if words_per_topic:
        for i, word_count in enumerate(words_per_topic, 1):
            if word_count < min_words_per_topic:
                shortfall = min_words_per_topic - word_count
                warnings.append(f"Topic {i} has {word_count} words (require {min_words_per_topic}-{max_words_per_topic}, need {shortfall} more words)")
            elif word_count > max_words_per_topic:
                excess = word_count - max_words_per_topic
                warnings.append(f"Topic {i} has {word_count} words (exceeds {max_words_per_topic} by {excess} words - consider condensing)")
    
    if total_words > max_total_words:
        excess = total_words - max_total_words
        warnings.append(f"Total word count ({total_words}) exceeds maximum {max_total_words} (exceeds by {excess} words - condense content)")
    
    metrics['warnings'] = warnings
    metrics['requirements'] = {
        'topics_range': f"{min_topics}-{max_topics}",
        'words_per_topic_range': f"{min_words_per_topic}-{max_words_per_topic}",
        'max_total_words': max_total_words
    }
    return metrics


def analyze_visualization(content_text: str, requirements: Dict[str, int] = None) -> Dict[str, Any]:
    """Comprehensive visualization content analysis.
    
    Analyzes Mermaid diagram syntax and structure.
    
    Expected format (Mermaid):
        graph TD
            A[Node1] --> B[Node2]
            B --> C[Node3]
    
    Args:
        content_text: Visualization content (Mermaid diagram code)
        requirements: Optional dict with min_diagram_elements, min_nodes, min_connections
        
    Returns:
        Dictionary with analysis metrics including:
        - nodes: Number of diagram nodes
        - connections: Number of connections/edges
        - total_elements: Total diagram elements
        - mermaid_warnings: List of Mermaid syntax warnings
        - warnings: List of validation warnings
    """
    # Use provided requirements or defaults
    if requirements is None:
        requirements = {}
    min_elements = requirements.get('min_diagram_elements', 3)
    min_nodes = requirements.get('min_nodes', 3)
    min_connections = requirements.get('min_connections', 2)
    
    # Validate Mermaid syntax and get warnings
    cleaned_diagram, mermaid_warnings = validate_mermaid_syntax(content_text, min_nodes=min_nodes, min_connections=min_connections)
    
    # Count diagram elements (nodes, connections)
    # Count nodes: [NodeName], (NodeName), NodeName{...}, etc.
    nodes = len(re.findall(r'\[[^\]]+\]|\([^\)]+\)|\w+\s*\{', cleaned_diagram))
    
    # Count connections: -->, ---, ==>, etc.
    connections = len(re.findall(r'-->|---|==>|--|==', cleaned_diagram))
    
    # Count total elements
    total_elements = nodes + connections
    
    # Initialize warnings list with Mermaid validation warnings
    warnings = list(mermaid_warnings)  # Start with Mermaid validation warnings
    
    # Add quality warnings based on element count
    if total_elements < min_elements:
        needed = min_elements - total_elements
        warnings.append(f"Only {total_elements} diagram elements found (require at least {min_elements}, need {needed} more - add nodes and connections)")
    
    # Build metrics dictionary with all warnings
    metrics = {
        'char_count': len(content_text),
        'cleaned_char_count': len(cleaned_diagram),
        'nodes': nodes,
        'connections': connections,
        'total_elements': total_elements,
        'mermaid_warnings': mermaid_warnings,
        'warnings': warnings,  # Include validation warnings
    }
    
    metrics['requirements'] = {
        'min_diagram_elements': min_elements
    }
    return metrics


def analyze_integration(content_text: str, requirements: Dict[str, int] = None) -> Dict[str, Any]:
    """Comprehensive integration content analysis.
    
    Analyzes cross-module integration content for connections and references.
    
    Expected format:
        # Integration with Other Modules
        This module connects to Module 2...
        See also Module 3...
    
    Args:
        content_text: Integration content in markdown
        requirements: Optional dict with min_connections, max_total_words
        
    Returns:
        Dictionary with analysis metrics including:
        - word_count: Total word count
        - connections: Number of cross-module connections found
        - cross_refs: Number of cross-references
        - sections: Number of major sections
        - warnings: List of validation warnings
    """
    # Use provided requirements or defaults
    if requirements is None:
        requirements = {}
    min_connections = requirements.get('min_connections', 3)
    max_total_words = requirements.get('max_total_words', 1000)
    
    # Count cross-module connections (references to other modules, topics, concepts)
    connection_patterns = [
        r'Module\s+\d+',
        r'module\s+\d+',
        r'see\s+(?:module|lecture|lab)',
        r'connects?\s+to',
        r'relates?\s+to',
        r'builds?\s+on',
        r'extends?\s+',
    ]
    connections = sum(len(re.findall(p, content_text, re.IGNORECASE)) for p in connection_patterns)
    
    total_words = count_words(content_text)
    
    metrics = {
        'word_count': total_words,
        'char_count': len(content_text),
        'connections': connections,
        'sections': count_sections(content_text),
        'cross_refs': count_cross_references(content_text),
    }
    
    # Quality warnings
    warnings = []
    if connections < min_connections:
        needed = min_connections - connections
        warnings.append(f"Only {connections} connections found (require at least {min_connections}, need {needed} more - add references to other modules/topics)")
    
    if total_words > max_total_words:
        excess = total_words - max_total_words
        warnings.append(f"Total word count ({total_words}) exceeds maximum {max_total_words} (exceeds by {excess} words - condense content)")
    
    metrics['warnings'] = warnings
    metrics['requirements'] = {
        'min_connections': min_connections,
        'max_total_words': max_total_words
    }
    return metrics


def analyze_investigation(content_text: str, requirements: Dict[str, int] = None) -> Dict[str, Any]:
    """Comprehensive investigation content analysis.
    
    Analyzes research investigation content for questions and structure.
    
    Expected format:
        # Research Investigations
        ## Research Question 1: Title
        Investigation details...
        
        ## Research Question 2: Title
        Investigation details...
    
    Args:
        content_text: Investigation content in markdown
        requirements: Optional dict with min_questions, max_total_words
        
    Returns:
        Dictionary with analysis metrics including:
        - word_count: Total word count
        - questions: Number of research questions found
        - sections: Number of major sections
        - warnings: List of validation warnings
    """
    # Use provided requirements or defaults
    if requirements is None:
        requirements = {}
    min_questions = requirements.get('min_questions', 3)
    max_total_words = requirements.get('max_total_words', 1000)
    
    # Count research questions (## Research Question N, **Question N:**, etc.)
    # Updated to match actual format: **Question N:** (colon inside bold)
    question_patterns = [
        r'##\s+Research\s+Question\s+\d+',
        r'##\s+Investigation\s+\d+',
        r'\*\*Question\s+\d+:\*\*',  # Colon inside bold - ACTUAL FORMAT
        r'\*\*Question\s+\d+\*\*:?',  # Fallback for other formats
        r'^\s*\d+[.)]\s+.*\?',  # Numbered list with question mark
    ]
    questions = len(re.findall('|'.join(question_patterns), content_text, re.IGNORECASE | re.MULTILINE))
    
    total_words = count_words(content_text)
    
    metrics = {
        'word_count': total_words,
        'char_count': len(content_text),
        'questions': questions,
        'sections': count_sections(content_text),
    }
    
    # Quality warnings
    warnings = []
    if questions < min_questions:
        needed = min_questions - questions
        warnings.append(f"Only {questions} research questions found (require at least {min_questions}, need {needed} more - add ## Research Question N sections)")
    
    if total_words > max_total_words:
        excess = total_words - max_total_words
        warnings.append(f"Total word count ({total_words}) exceeds maximum {max_total_words} (exceeds by {excess} words - condense content)")
    
    metrics['warnings'] = warnings
    metrics['requirements'] = {
        'min_questions': min_questions,
        'max_total_words': max_total_words
    }
    return metrics


def analyze_open_questions(content_text: str, requirements: Dict[str, int] = None) -> Dict[str, Any]:
    """Comprehensive open questions content analysis.
    
    Analyzes open-ended research questions content for structure and completeness.
    
    Expected format:
        # Open Questions
        ## Open Question 1: Title
        Question details...
        
        ## Open Question 2: Title
        Question details...
    
    Args:
        content_text: Open questions content in markdown
        requirements: Optional dict with min_questions, max_total_words
        
    Returns:
        Dictionary with analysis metrics including:
        - word_count: Total word count
        - questions: Number of open questions found
        - sections: Number of major sections
        - warnings: List of validation warnings
    """
    # Use provided requirements or defaults
    if requirements is None:
        requirements = {}
    min_questions = requirements.get('min_questions', 3)
    max_total_words = requirements.get('max_total_words', 1000)
    
    # Count open questions (## Open Question N, **Question N:**, etc.)
    # Updated to match actual format: **Question N:** (colon inside bold)
    question_patterns = [
        r'##\s+Open\s+Question\s+\d+',
        r'##\s+Question\s+\d+',
        r'\*\*Question\s+\d+:\*\*',  # Colon inside bold - ACTUAL FORMAT
        r'\*\*Question\s+\d+\*\*:?',  # Fallback for other formats
        r'^\s*\d+[.)]\s+.*\?',  # Numbered list with question mark
    ]
    questions = len(re.findall('|'.join(question_patterns), content_text, re.IGNORECASE | re.MULTILINE))
    
    total_words = count_words(content_text)
    
    metrics = {
        'word_count': total_words,
        'char_count': len(content_text),
        'questions': questions,
        'sections': count_sections(content_text),
    }
    
    # Quality warnings
    warnings = []
    if questions < min_questions:
        needed = min_questions - questions
        warnings.append(f"Only {questions} open questions found (require at least {min_questions}, need {needed} more - add ## Open Question N sections)")
    
    if total_words > max_total_words:
        excess = total_words - max_total_words
        warnings.append(f"Total word count ({total_words}) exceeds maximum {max_total_words} (exceeds by {excess} words - condense content)")
    
    metrics['warnings'] = warnings
    metrics['requirements'] = {
        'min_questions': min_questions,
        'max_total_words': max_total_words
    }
    return metrics







def validate_prompt_quality(
    prompt_template: str,
    variables: Dict[str, Any],
    content_type: str,
    requirements: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Validate prompt quality before generation (proactive validation).
    
    Checks if prompt contains necessary information and requirements.
    
    Args:
        prompt_template: Prompt template string
        variables: Template variables dictionary
        content_type: Type of content being generated
        requirements: Optional content requirements dictionary
        
    Returns:
        Dictionary with validation results including:
        - is_valid: Boolean indicating if prompt passes checks
        - issues: List of issues found
        - suggestions: List of improvement suggestions
        - quality_score: Prompt quality score (0-100)
    """
    issues = []
    suggestions = []
    score = 100.0
    
    # Check for required variables
    required_vars_pattern = r'\{(\w+)\}'
    required_vars = set(re.findall(required_vars_pattern, prompt_template))
    provided_vars = set(variables.keys())
    
    missing_vars = required_vars - provided_vars
    if missing_vars:
        issues.append({
            'type': 'missing_variables',
            'message': f"Missing template variables: {', '.join(missing_vars)}",
            'severity': 'high'
        })
        score -= len(missing_vars) * 10
        suggestions.append(f"Provide values for: {', '.join(missing_vars)}")
    
    # Check for content-specific requirements in prompt
    if content_type == "questions":
        if "num_questions" not in variables:
            issues.append({
                'type': 'missing_requirement',
                'message': "Number of questions not specified",
                'severity': 'high'
            })
            score -= 15
        if "**Question" not in prompt_template and "Question" not in prompt_template:
            issues.append({
                'type': 'format_guidance',
                'message': "Prompt doesn't specify question format",
                'severity': 'medium'
            })
            score -= 5
            suggestions.append("Add format specification: Use **Question N:** format")
    
    elif content_type == "lecture":
        if requirements:
            min_words = requirements.get('min_word_count', 0)
            max_words = requirements.get('max_word_count', 0)
            if min_words and max_words:
                if f"{min_words}" not in prompt_template and f"{max_words}" not in prompt_template:
                    issues.append({
                        'type': 'missing_requirement',
                        'message': f"Word count requirement ({min_words}-{max_words}) not in prompt",
                        'severity': 'medium'
                    })
                    score -= 5
                    suggestions.append(f"Specify word count requirement: {min_words}-{max_words} words")
    
    # Check prompt length (too short may lack guidance)
    if len(prompt_template) < 100:
        issues.append({
            'type': 'prompt_too_short',
            'message': "Prompt is very short, may lack sufficient guidance",
            'severity': 'low'
        })
        score -= 5
        suggestions.append("Add more specific guidance to prompt")
    
    # Check for examples in prompt (examples help LLM understand format)
    if "example" not in prompt_template.lower() and "format" not in prompt_template.lower():
        issues.append({
            'type': 'missing_examples',
            'message': "Prompt doesn't include format examples",
            'severity': 'low'
        })
        score -= 3
        suggestions.append("Add format examples to help LLM understand expected output")
    
    score = max(0.0, score)
    
    return {
        'is_valid': score >= 70,
        'quality_score': round(score, 1),
        'issues': issues,
        'suggestions': suggestions,
        'missing_variables': list(missing_vars) if missing_vars else [],
        'provided_variables': list(provided_vars)
    }


def calculate_quality_score(
    metrics: Dict[str, Any],
    requirements: Optional[Dict[str, Any]] = None,
    content_type: str = "generic"
) -> Dict[str, Any]:
    """Calculate quality score (0-100) for generated content.
    
    Args:
        metrics: Analysis metrics dictionary
        requirements: Optional content requirements
        content_type: Type of content
        
    Returns:
        Dictionary with quality score and breakdown
    """
    score = 100.0
    deductions = []
    
    warnings = metrics.get('warnings', [])
    
    # Deduct points for warnings
    for warning in warnings:
        warning_lower = warning.lower()
        
        # Critical issues (deduct more)
        if any(kw in warning_lower for kw in ['missing', 'no questions detected', 'no examples', 'no sections']):
            deductions.append({'type': 'critical', 'penalty': 10, 'message': warning})
            score -= 10
        # Major issues
        elif any(kw in warning_lower for kw in ['only', 'require', 'need', 'exceeds maximum', 'below minimum']):
            deductions.append({'type': 'major', 'penalty': 5, 'message': warning})
            score -= 5
        # Minor issues
        else:
            deductions.append({'type': 'minor', 'penalty': 2, 'message': warning})
            score -= 2
    
    # Content-type specific scoring
    if content_type == "lecture":
        word_count = metrics.get('word_count', 0)
        if requirements:
            min_words = requirements.get('min_word_count', 0)
            max_words = requirements.get('max_word_count', 0)
            if min_words and max_words:
                if word_count < min_words:
                    shortfall = min_words - word_count
                    penalty = min(15, shortfall / 10)  # Up to 15 points
                    score -= penalty
                    deductions.append({
                        'type': 'word_count',
                        'penalty': penalty,
                        'message': f"Word count below minimum ({word_count} < {min_words})"
                    })
                elif word_count > max_words:
                    excess = word_count - max_words
                    penalty = min(10, excess / 20)  # Up to 10 points
                    score -= penalty
                    deductions.append({
                        'type': 'word_count',
                        'penalty': penalty,
                        'message': f"Word count exceeds maximum ({word_count} > {max_words})"
                    })
    
    elif content_type == "questions":
        total_questions = metrics.get('total_questions', 0)
        expected = requirements.get('num_questions', 10) if requirements else 10
        
        if total_questions < expected:
            missing = expected - total_questions
            penalty = min(20, missing * 3)  # Up to 20 points
            score -= penalty
            deductions.append({
                'type': 'completeness',
                'penalty': penalty,
                'message': f"Only {total_questions}/{expected} questions generated"
            })
    
    score = max(0.0, score)
    
    # Determine quality level
    if score >= 90:
        quality_level = 'excellent'
    elif score >= 75:
        quality_level = 'good'
    elif score >= 60:
        quality_level = 'acceptable'
    else:
        quality_level = 'needs_improvement'
    
    return {
        'overall_score': round(score, 1),
        'quality_level': quality_level,
        'deductions': deductions,
        'warning_count': len(warnings),
        'critical_issues': len([d for d in deductions if d['type'] == 'critical'])
    }


def aggregate_validation_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregate validation results across multiple sessions/modules.
    
    Args:
        results: List of validation result dictionaries
        
    Returns:
        Aggregated results dictionary
    """
    if not results:
        return {
            'total_items': 0,
            'average_score': 0.0,
            'quality_distribution': {},
            'common_issues': [],
            'overall_quality': 'unknown'
        }
    
    scores = [r.get('quality_score', {}).get('overall_score', 0) for r in results if r.get('quality_score')]
    avg_score = sum(scores) / len(scores) if scores else 0.0
    
    # Quality level distribution
    quality_levels = [r.get('quality_score', {}).get('quality_level', 'unknown') for r in results if r.get('quality_score')]
    quality_distribution = {}
    for level in quality_levels:
        quality_distribution[level] = quality_distribution.get(level, 0) + 1
    
    # Collect common issues
    all_issues = []
    for result in results:
        issues = result.get('issues', [])
        if isinstance(issues, list):
            all_issues.extend(issues)
    
    # Count issue frequency
    issue_counts = {}
    for issue in all_issues:
        issue_msg = issue.get('message', str(issue))
        issue_counts[issue_msg] = issue_counts.get(issue_msg, 0) + 1
    
    # Get top 5 most common issues
    common_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Determine overall quality
    if avg_score >= 90:
        overall_quality = 'excellent'
    elif avg_score >= 75:
        overall_quality = 'good'
    elif avg_score >= 60:
        overall_quality = 'acceptable'
    else:
        overall_quality = 'needs_improvement'
    
    return {
        'total_items': len(results),
        'average_score': round(avg_score, 1),
        'quality_distribution': quality_distribution,
        'common_issues': [{'issue': issue, 'count': count} for issue, count in common_issues],
        'overall_quality': overall_quality,
        'scores_range': {
            'min': min(scores) if scores else 0,
            'max': max(scores) if scores else 0
        }
    }

