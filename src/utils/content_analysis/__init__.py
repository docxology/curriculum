"""Content analysis utilities for quality assessment.

This package provides modular content analysis functions organized by purpose:
- counters: Counting functions for text elements
- analyzers: Analysis functions for different content types
- mermaid: Mermaid diagram validation
- logging: Metrics logging utilities
"""

# Import counting functions
from src.utils.content_analysis.counters import (
    count_words,
    count_sections,
    count_subsections,
    count_examples,
    count_definitions,
    count_cross_references,
)

# Import analysis functions
from src.utils.content_analysis.analyzers import (
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
    validate_prompt_quality,
    calculate_quality_score,
    aggregate_validation_results,
)

# Import Mermaid validation
from src.utils.content_analysis.mermaid import (
    validate_mermaid_syntax,
)

# Import logging utilities
from src.utils.content_analysis.logging import (
    log_content_metrics,
)

# Import consistency validation
from src.utils.content_analysis.consistency import (
    validate_cross_session_consistency,
    track_concept_progression,
)

__all__ = [
    # Counting functions
    'count_words',
    'count_sections',
    'count_subsections',
    'count_examples',
    'count_definitions',
    'count_cross_references',
    # Analysis functions
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
    # Quality and validation
    'validate_prompt_quality',
    'calculate_quality_score',
    'aggregate_validation_results',
    # Consistency validation
    'validate_cross_session_consistency',
    'track_concept_progression',
    # Mermaid validation
    'validate_mermaid_syntax',
    # Logging
    'log_content_metrics',
]






