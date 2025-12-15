"""Cross-session consistency validation.

This module provides functions to validate coherence across sessions,
track concept progression, and ensure logical flow in course content.
"""

import logging
from typing import Dict, List, Any, Set, Optional
from collections import defaultdict
import re

logger = logging.getLogger(__name__)


def extract_concepts_from_text(text: str) -> Set[str]:
    """Extract key concepts from text (bold terms, defined terms, etc.).
    
    Args:
        text: Text content to extract concepts from
        
    Returns:
        Set of concept names (normalized)
    """
    concepts = set()
    
    # Extract bold terms: **Term** or **Term:**
    bold_pattern = r'\*\*([^*]+?)\*\*:?'
    bold_matches = re.findall(bold_pattern, text)
    concepts.update(b.lower().strip() for b in bold_matches)
    
    # Extract defined terms (Term: definition or Term - definition)
    definition_patterns = [
        r'([A-Z][a-zA-Z\s]+?):\s+[A-Z]',  # Term: Definition
        r'([A-Z][a-zA-Z\s]+?)\s+-\s+[A-Z]',  # Term - Definition
    ]
    for pattern in definition_patterns:
        matches = re.findall(pattern, text)
        concepts.update(m.lower().strip() for m in matches if len(m.strip()) < 50)
    
    return concepts


def track_concept_progression(sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Track how concepts progress across sessions.
    
    Args:
        sessions: List of session dictionaries with content
        
    Returns:
        Dictionary with concept progression analysis
    """
    concept_history = {}  # concept -> list of (session_num, first_mention, last_mention)
    concept_introductions = {}  # concept -> session_num where first introduced
    
    for session in sessions:
        session_num = session.get('session_number', 0)
        session_title = session.get('session_title', '')
        
        # Extract concepts from session
        concepts = set()
        
        # From key_concepts field
        key_concepts = session.get('key_concepts', [])
        concepts.update(c.lower().strip() for c in key_concepts)
        
        # From subtopics
        subtopics = session.get('subtopics', [])
        for subtopic in subtopics:
            # Extract potential concept names (capitalized terms)
            words = subtopic.split()
            for word in words:
                if word[0].isupper() and len(word) > 3:
                    concepts.add(word.lower())
        
        # Track concept appearances
        for concept in concepts:
            if concept not in concept_history:
                concept_history[concept] = []
                concept_introductions[concept] = session_num
            concept_history[concept].append(session_num)
    
    # Analyze progression issues
    issues = []
    
    # Check for concepts that appear and disappear (gaps)
    for concept, appearances in concept_history.items():
        if len(appearances) > 1:
            appearances_sorted = sorted(appearances)
            gaps = []
            for i in range(len(appearances_sorted) - 1):
                gap = appearances_sorted[i+1] - appearances_sorted[i]
                if gap > 3:
                    gaps.append((appearances_sorted[i], appearances_sorted[i+1], gap))
            
            if gaps:
                issues.append({
                    'type': 'concept_gap',
                    'concept': concept,
                    'gaps': gaps,
                    'message': f"Concept '{concept}' has gaps in coverage: {gaps}"
                })
    
    # Check for concepts introduced late that should be early
    for concept, intro_session in concept_introductions.items():
        concept_lower = concept.lower()
        # Basic concepts should appear early
        basic_indicators = ['introduction', 'basic', 'fundamental', 'foundation', 'overview', 'principle']
        if any(ind in concept_lower for ind in basic_indicators) and intro_session > 3:
            issues.append({
                'type': 'late_basic_concept',
                'concept': concept,
                'introduced_in': intro_session,
                'message': f"Basic concept '{concept}' introduced late (session {intro_session})"
            })
    
    return {
        'concept_count': len(concept_history),
        'concept_history': concept_history,
        'concept_introductions': concept_introductions,
        'issues': issues,
        'total_issues': len(issues)
    }


def validate_cross_session_consistency(
    outline_data: Dict[str, Any],
    generated_content: Optional[Dict[int, Dict[int, Dict[str, str]]]] = None
) -> Dict[str, Any]:
    """Validate consistency across sessions in a course.
    
    Args:
        outline_data: Parsed JSON outline data
        generated_content: Optional dictionary of generated content:
            {module_id: {session_num: {'lecture': text, 'lab': text, ...}}}
        
    Returns:
        Dictionary with consistency validation results
    """
    modules = outline_data.get('modules', [])
    all_sessions = []
    
    # Collect all sessions
    for module in modules:
        for session in module.get('sessions', []):
            session_with_module = session.copy()
            session_with_module['module_id'] = module.get('module_id')
            session_with_module['module_name'] = module.get('module_name', '')
            all_sessions.append(session_with_module)
    
    # Track concept progression
    progression_result = track_concept_progression(all_sessions)
    
    # Check for topic coherence (related topics should be close together)
    coherence_issues = []
    for i, session1 in enumerate(all_sessions):
        for j, session2 in enumerate(all_sessions[i+1:], start=i+1):
            # Check if sessions have related topics but are far apart
            topics1 = set(t.lower() for t in session1.get('subtopics', []))
            topics2 = set(t.lower() for t in session2.get('subtopics', []))
            
            # Calculate similarity
            if topics1 and topics2:
                intersection = topics1 & topics2
                union = topics1 | topics2
                if union:
                    similarity = len(intersection) / len(union)
                    
                    # If highly similar but far apart, flag as coherence issue
                    if similarity > 0.3 and (j - i) > 3:
                        coherence_issues.append({
                            'type': 'topic_separation',
                            'session1': session1.get('session_number'),
                            'session2': session2.get('session_number'),
                            'similarity': similarity,
                            'gap': j - i,
                            'message': f"Related topics in sessions {session1.get('session_number')} and {session2.get('session_number')} are {j-i} sessions apart"
                        })
    
    # Check for missing prerequisites (if generated content available)
    prerequisite_issues = []
    if generated_content:
        # This would require more sophisticated analysis of actual content
        # For now, we'll just note that content analysis is available
        pass
    
    all_issues = progression_result['issues'] + coherence_issues
    
    return {
        'is_consistent': len(all_issues) == 0,
        'total_issues': len(all_issues),
        'progression_issues': len(progression_result['issues']),
        'coherence_issues': len(coherence_issues),
        'issues': all_issues,
        'concept_progression': progression_result,
        'recommendations': _generate_consistency_recommendations(all_issues)
    }


def _generate_consistency_recommendations(issues: List[Dict[str, Any]]) -> List[str]:
    """Generate recommendations based on consistency issues.
    
    Args:
        issues: List of consistency issues
        
    Returns:
        List of recommendation strings
    """
    recommendations = []
    
    concept_gaps = [i for i in issues if i.get('type') == 'concept_gap']
    if concept_gaps:
        recommendations.append(f"Consider adding intermediate sessions to bridge {len(concept_gaps)} concept gaps")
    
    late_basics = [i for i in issues if i.get('type') == 'late_basic_concept']
    if late_basics:
        recommendations.append(f"Move {len(late_basics)} basic concepts to earlier sessions")
    
    topic_separations = [i for i in issues if i.get('type') == 'topic_separation']
    if topic_separations:
        recommendations.append(f"Consider reorganizing {len(topic_separations)} related topic pairs that are far apart")
    
    if not recommendations:
        recommendations.append("No consistency issues detected - course structure is coherent")
    
    return recommendations

