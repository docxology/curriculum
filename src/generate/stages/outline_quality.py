"""Outline quality validation and scoring.

This module provides comprehensive quality checks for course outlines including:
- Topic overlap detection
- Learning progression validation
- Balance checking (sessions, concepts, objectives)
- Coherence scoring
- Completeness validation
"""

import logging
from typing import Dict, List, Any, Tuple, Set
from collections import Counter
import re

logger = logging.getLogger(__name__)


def _normalize_text(text: str) -> str:
    """Normalize text for comparison (lowercase, remove punctuation).
    
    Args:
        text: Text to normalize
        
    Returns:
        Normalized text
    """
    # Remove common words and normalize
    text = text.lower().strip()
    # Remove common punctuation
    text = re.sub(r'[^\w\s]', '', text)
    return text


def _extract_keywords(text: str, min_length: int = 3) -> Set[str]:
    """Extract meaningful keywords from text.
    
    Args:
        text: Text to extract keywords from
        min_length: Minimum keyword length
        
    Returns:
        Set of keywords
    """
    normalized = _normalize_text(text)
    # Split into words and filter
    words = normalized.split()
    # Filter out common stop words and short words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may', 'might', 'must', 'can'}
    keywords = {w for w in words if len(w) >= min_length and w not in stop_words}
    return keywords


def detect_topic_overlap(outline_data: Dict[str, Any], threshold: float = 0.5) -> List[Dict[str, Any]]:
    """Detect overlapping or redundant topics across sessions/modules.
    
    Args:
        outline_data: Parsed JSON outline data
        threshold: Similarity threshold (0.0-1.0) for considering topics overlapping
        
    Returns:
        List of overlap issues with details
    """
    overlaps = []
    modules = outline_data.get('modules', [])
    
    # Collect all topics with their context
    all_topics = []
    for module in modules:
        module_id = module.get('module_id')
        module_name = module.get('module_name', '')
        for session in module.get('sessions', []):
            session_num = session.get('session_number')
            session_title = session.get('session_title', '')
            
            # Check subtopics
            for subtopic in session.get('subtopics', []):
                all_topics.append({
                    'text': subtopic,
                    'module_id': module_id,
                    'module_name': module_name,
                    'session_num': session_num,
                    'session_title': session_title,
                    'type': 'subtopic'
                })
            
            # Check session titles
            all_topics.append({
                'text': session_title,
                'module_id': module_id,
                'module_name': module_name,
                'session_num': session_num,
                'session_title': session_title,
                'type': 'session_title'
            })
    
    # Compare all pairs
    for i, topic1 in enumerate(all_topics):
        keywords1 = _extract_keywords(topic1['text'])
        if not keywords1:
            continue
            
        for j, topic2 in enumerate(all_topics[i+1:], start=i+1):
            keywords2 = _extract_keywords(topic2['text'])
            if not keywords2:
                continue
            
            # Calculate Jaccard similarity
            intersection = keywords1 & keywords2
            union = keywords1 | keywords2
            if union:
                similarity = len(intersection) / len(union)
            else:
                similarity = 0.0
            
            if similarity >= threshold:
                # Check if they're in different contexts (not just same topic repeated)
                if (topic1['module_id'] != topic2['module_id'] or 
                    topic1['session_num'] != topic2['session_num']):
                    overlaps.append({
                        'topic1': topic1['text'],
                        'topic2': topic2['text'],
                        'similarity': similarity,
                        'context1': f"Module {topic1['module_id']}, Session {topic1['session_num']}",
                        'context2': f"Module {topic2['module_id']}, Session {topic2['session_num']}",
                        'type1': topic1['type'],
                        'type2': topic2['type']
                    })
    
    return overlaps


def validate_learning_progression(outline_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Validate that learning progression is logical across sessions.
    
    Args:
        outline_data: Parsed JSON outline data
        
    Returns:
        List of progression issues
    """
    issues = []
    modules = outline_data.get('modules', [])
    
    # Track concepts mentioned across sessions
    concept_history = {}
    
    for module in modules:
        module_id = module.get('module_id')
        module_name = module.get('module_name', '')
        
        for session in module.get('sessions', []):
            session_num = session.get('session_number')
            session_title = session.get('session_title', '')
            key_concepts = session.get('key_concepts', [])
            learning_objectives = session.get('learning_objectives', [])
            
            # Check if advanced concepts appear before basics
            for concept in key_concepts:
                concept_lower = concept.lower()
                
                # Check for advanced keywords that should come later
                advanced_indicators = ['advanced', 'complex', 'sophisticated', 'integration', 'synthesis', 'application']
                basic_indicators = ['introduction', 'basic', 'fundamental', 'foundation', 'overview', 'principles']
                
                has_advanced = any(ind in concept_lower for ind in advanced_indicators)
                has_basic = any(ind in concept_lower for ind in basic_indicators)
                
                if has_advanced and session_num == 1:
                    issues.append({
                        'type': 'advanced_early',
                        'concept': concept,
                        'session': session_num,
                        'module': module_id,
                        'message': f"Advanced concept '{concept}' appears in early session {session_num}"
                    })
            
            # Track concept progression
            for concept in key_concepts:
                if concept not in concept_history:
                    concept_history[concept] = session_num
                else:
                    # Concept repeated - check if it's building on previous
                    first_mention = concept_history[concept]
                    if session_num - first_mention > 3:
                        # Concept reappears after gap - might indicate missing progression
                        issues.append({
                            'type': 'concept_gap',
                            'concept': concept,
                            'first_session': first_mention,
                            'current_session': session_num,
                            'gap': session_num - first_mention,
                            'message': f"Concept '{concept}' reappears after {session_num - first_mention} session gap"
                        })
    
    return issues


def validate_balance(outline_data: Dict[str, Any], expected_sessions: int = None) -> Dict[str, Any]:
    """Validate balance across modules (sessions, concepts, objectives).
    
    Args:
        outline_data: Parsed JSON outline data
        expected_sessions: Expected total number of sessions
        
    Returns:
        Dictionary with balance metrics and issues
    """
    modules = outline_data.get('modules', [])
    metadata = outline_data.get('course_metadata', {})
    
    if expected_sessions is None:
        expected_sessions = metadata.get('total_sessions', len(modules) * 2)
    
    # Collect statistics per module
    module_stats = []
    total_sessions = 0
    total_concepts = 0
    total_objectives = 0
    
    for module in modules:
        sessions = module.get('sessions', [])
        num_sessions = len(sessions)
        total_sessions += num_sessions
        
        concepts_in_module = 0
        objectives_in_module = 0
        
        for session in sessions:
            concepts_in_module += len(session.get('key_concepts', []))
            objectives_in_module += len(session.get('learning_objectives', []))
        
        total_concepts += concepts_in_module
        total_objectives += objectives_in_module
        
        module_stats.append({
            'module_id': module.get('module_id'),
            'module_name': module.get('module_name', ''),
            'sessions': num_sessions,
            'concepts': concepts_in_module,
            'objectives': objectives_in_module,
            'concepts_per_session': concepts_in_module / num_sessions if num_sessions > 0 else 0,
            'objectives_per_session': objectives_in_module / num_sessions if num_sessions > 0 else 0
        })
    
    # Calculate averages
    avg_sessions_per_module = total_sessions / len(modules) if modules else 0
    avg_concepts_per_session = total_concepts / total_sessions if total_sessions > 0 else 0
    avg_objectives_per_session = total_objectives / total_sessions if total_sessions > 0 else 0
    
    # Check for imbalances
    issues = []
    
    # Session distribution
    session_counts = [m['sessions'] for m in module_stats]
    if session_counts:
        min_sessions = min(session_counts)
        max_sessions = max(session_counts)
        if max_sessions - min_sessions > 2:
            issues.append({
                'type': 'session_imbalance',
                'min': min_sessions,
                'max': max_sessions,
                'difference': max_sessions - min_sessions,
                'message': f"Session distribution uneven: {min_sessions}-{max_sessions} sessions per module"
            })
    
    # Concepts per session
    concepts_per_session = [m['concepts_per_session'] for m in module_stats if m['sessions'] > 0]
    if concepts_per_session:
        min_concepts = min(concepts_per_session)
        max_concepts = max(concepts_per_session)
        if max_concepts - min_concepts > 3:
            issues.append({
                'type': 'concept_imbalance',
                'min': min_concepts,
                'max': max_concepts,
                'difference': max_concepts - min_concepts,
                'message': f"Concept distribution uneven: {min_concepts:.1f}-{max_concepts:.1f} concepts per session"
            })
    
    # Objectives per session
    objectives_per_session = [m['objectives_per_session'] for m in module_stats if m['sessions'] > 0]
    if objectives_per_session:
        min_objectives = min(objectives_per_session)
        max_objectives = max(objectives_per_session)
        if max_objectives - min_objectives > 2:
            issues.append({
                'type': 'objective_imbalance',
                'min': min_objectives,
                'max': max_objectives,
                'difference': max_objectives - min_objectives,
                'message': f"Objective distribution uneven: {min_objectives:.1f}-{max_objectives:.1f} objectives per session"
            })
    
    # Check total session count
    if total_sessions != expected_sessions:
        issues.append({
            'type': 'session_count_mismatch',
            'expected': expected_sessions,
            'actual': total_sessions,
            'difference': abs(total_sessions - expected_sessions),
            'message': f"Session count mismatch: expected {expected_sessions}, got {total_sessions}"
        })
    
    return {
        'total_modules': len(modules),
        'total_sessions': total_sessions,
        'expected_sessions': expected_sessions,
        'total_concepts': total_concepts,
        'total_objectives': total_objectives,
        'avg_sessions_per_module': avg_sessions_per_module,
        'avg_concepts_per_session': avg_concepts_per_session,
        'avg_objectives_per_session': avg_objectives_per_session,
        'module_stats': module_stats,
        'issues': issues
    }


def calculate_quality_score(outline_data: Dict[str, Any], expected_sessions: int = None) -> Dict[str, Any]:
    """Calculate overall quality score for outline (0-100 scale).
    
    Args:
        outline_data: Parsed JSON outline data
        expected_sessions: Expected total number of sessions
        
    Returns:
        Dictionary with quality score and breakdown
    """
    score = 100.0
    deductions = []
    
    # Check topic overlap (deduct up to 20 points)
    overlaps = detect_topic_overlap(outline_data, threshold=0.6)
    if overlaps:
        overlap_penalty = min(20, len(overlaps) * 2)
        score -= overlap_penalty
        deductions.append({
            'category': 'topic_overlap',
            'penalty': overlap_penalty,
            'count': len(overlaps),
            'details': overlaps[:5]  # Top 5 overlaps
        })
    
    # Check learning progression (deduct up to 15 points)
    progression_issues = validate_learning_progression(outline_data)
    if progression_issues:
        progression_penalty = min(15, len(progression_issues) * 3)
        score -= progression_penalty
        deductions.append({
            'category': 'learning_progression',
            'penalty': progression_penalty,
            'count': len(progression_issues),
            'details': progression_issues[:5]  # Top 5 issues
        })
    
    # Check balance (deduct up to 15 points)
    balance_result = validate_balance(outline_data, expected_sessions)
    if balance_result.get('issues'):
        balance_penalty = min(15, len(balance_result['issues']) * 3)
        score -= balance_penalty
        deductions.append({
            'category': 'balance',
            'penalty': balance_penalty,
            'count': len(balance_result['issues']),
            'details': balance_result['issues']
        })
    
    # Check completeness (deduct up to 10 points)
    modules = outline_data.get('modules', [])
    metadata = outline_data.get('course_metadata', {})
    expected_modules = metadata.get('total_modules', len(modules))
    
    if len(modules) != expected_modules:
        completeness_penalty = 10
        score -= completeness_penalty
        deductions.append({
            'category': 'completeness',
            'penalty': completeness_penalty,
            'count': 1,
            'details': [{
                'type': 'module_count_mismatch',
                'expected': expected_modules,
                'actual': len(modules)
            }]
        })
    
    # Ensure score doesn't go below 0
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
        'balance_metrics': balance_result,
        'overlap_count': len(overlaps),
        'progression_issue_count': len(progression_issues)
    }


def validate_outline_quality(outline_data: Dict[str, Any], expected_sessions: int = None) -> Dict[str, Any]:
    """Comprehensive outline quality validation.
    
    Args:
        outline_data: Parsed JSON outline data
        expected_sessions: Expected total number of sessions
        
    Returns:
        Dictionary with validation results including:
        - is_valid: Boolean indicating if outline passes quality checks
        - quality_score: Overall quality score (0-100)
        - issues: List of all issues found
        - recommendations: List of improvement recommendations
    """
    # Run all quality checks
    overlaps = detect_topic_overlap(outline_data)
    progression_issues = validate_learning_progression(outline_data)
    balance_result = validate_balance(outline_data, expected_sessions)
    quality_score = calculate_quality_score(outline_data, expected_sessions)
    
    # Collect all issues
    all_issues = []
    all_issues.extend([{'type': 'overlap', **o} for o in overlaps])
    all_issues.extend(progression_issues)
    all_issues.extend(balance_result.get('issues', []))
    
    # Generate recommendations
    recommendations = []
    
    if overlaps:
        recommendations.append({
            'priority': 'high',
            'category': 'topic_overlap',
            'message': f"Found {len(overlaps)} topic overlaps. Consider consolidating or differentiating overlapping topics.",
            'count': len(overlaps)
        })
    
    if progression_issues:
        recommendations.append({
            'priority': 'medium',
            'category': 'learning_progression',
            'message': f"Found {len(progression_issues)} progression issues. Review concept ordering and prerequisites.",
            'count': len(progression_issues)
        })
    
    if balance_result.get('issues'):
        recommendations.append({
            'priority': 'medium',
            'category': 'balance',
            'message': f"Found {len(balance_result['issues'])} balance issues. Consider redistributing sessions/concepts/objectives.",
            'count': len(balance_result['issues'])
        })
    
    if quality_score['overall_score'] < 75:
        recommendations.append({
            'priority': 'high',
            'category': 'overall_quality',
            'message': f"Overall quality score is {quality_score['overall_score']:.1f}/100. Review and address identified issues.",
            'score': quality_score['overall_score']
        })
    
    # Determine if outline passes (score >= 60 and no critical issues)
    is_valid = quality_score['overall_score'] >= 60 and len([i for i in all_issues if i.get('type') == 'advanced_early']) == 0
    
    return {
        'is_valid': is_valid,
        'quality_score': quality_score,
        'issues': all_issues,
        'recommendations': recommendations,
        'overlap_count': len(overlaps),
        'progression_issue_count': len(progression_issues),
        'balance_issue_count': len(balance_result.get('issues', []))
    }

