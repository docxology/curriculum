"""Smart retry system with pattern learning and adaptive strategies.

This module provides intelligent retry logic that learns from failure patterns
and adapts retry strategies based on success rates and error types.
"""

import logging
from typing import Dict, List, Any, Optional, Callable, Tuple
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class RetryStrategy(Enum):
    """Retry strategy types."""
    IMMEDIATE = "immediate"  # Retry immediately with same prompt
    ENHANCED = "enhanced"  # Retry with enhanced prompt (add feedback)
    SIMPLIFIED = "simplified"  # Retry with simplified prompt
    ADAPTIVE = "adaptive"  # Choose strategy based on error pattern


@dataclass
class RetryPattern:
    """Pattern of failures for learning."""
    error_type: str
    error_message: str
    content_type: str
    attempt_count: int
    success: bool
    timestamp: datetime = field(default_factory=datetime.now)
    strategy_used: Optional[str] = None
    fix_applied: Optional[str] = None


@dataclass
class RetryStats:
    """Statistics for retry patterns."""
    total_attempts: int = 0
    successful_attempts: int = 0
    failed_attempts: int = 0
    success_rate: float = 0.0
    patterns: List[RetryPattern] = field(default_factory=list)
    error_frequency: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    strategy_success_rates: Dict[str, float] = field(default_factory=lambda: defaultdict(float))


class SmartRetrySystem:
    """Smart retry system with pattern learning.
    
    Tracks retry patterns, learns from failures, and adapts strategies.
    """
    
    def __init__(self, max_history: int = 100):
        """Initialize smart retry system.
        
        Args:
            max_history: Maximum number of patterns to keep in history
        """
        self.max_history = max_history
        self.pattern_history: deque = deque(maxlen=max_history)
        self.stats = RetryStats()
        self.content_type_stats: Dict[str, RetryStats] = defaultdict(RetryStats)
    
    def record_attempt(
        self,
        error_type: str,
        error_message: str,
        content_type: str,
        attempt_count: int,
        success: bool,
        strategy_used: Optional[str] = None,
        fix_applied: Optional[str] = None
    ) -> None:
        """Record a retry attempt pattern.
        
        Args:
            error_type: Type of error encountered
            error_message: Error message
            content_type: Type of content being generated
            attempt_count: Number of attempts made
            success: Whether the attempt was successful
            strategy_used: Strategy used for this attempt
            fix_applied: Fix that was applied (if any)
        """
        pattern = RetryPattern(
            error_type=error_type,
            error_message=error_message,
            content_type=content_type,
            attempt_count=attempt_count,
            success=success,
            strategy_used=strategy_used,
            fix_applied=fix_applied
        )
        
        self.pattern_history.append(pattern)
        
        # Update stats
        self.stats.total_attempts += 1
        if success:
            self.stats.successful_attempts += 1
        else:
            self.stats.failed_attempts += 1
        
        # Update content type stats
        ct_stats = self.content_type_stats[content_type]
        ct_stats.total_attempts += 1
        if success:
            ct_stats.successful_attempts += 1
        else:
            ct_stats.failed_attempts += 1
        
        # Update error frequency
        self.stats.error_frequency[error_type] += 1
        ct_stats.error_frequency[error_type] += 1
        
        # Update strategy success rates
        if strategy_used:
            if strategy_used not in self.stats.strategy_success_rates:
                self.stats.strategy_success_rates[strategy_used] = 0.0
            
            # Calculate success rate for this strategy
            strategy_patterns = [p for p in self.pattern_history if p.strategy_used == strategy_used]
            if strategy_patterns:
                successes = sum(1 for p in strategy_patterns if p.success)
                self.stats.strategy_success_rates[strategy_used] = successes / len(strategy_patterns)
        
        # Recalculate overall success rate
        if self.stats.total_attempts > 0:
            self.stats.success_rate = self.stats.successful_attempts / self.stats.total_attempts
    
    def analyze_error_pattern(self, error_message: str, content_type: str) -> Dict[str, Any]:
        """Analyze error message to identify pattern and suggest strategy.
        
        Args:
            error_message: Error message to analyze
            content_type: Type of content being generated
            
        Returns:
            Dictionary with pattern analysis and suggested strategy
        """
        error_lower = error_message.lower()
        
        # Identify error category
        error_category = "unknown"
        suggested_strategy = RetryStrategy.ENHANCED
        
        if any(kw in error_lower for kw in ['format', 'missing question marks', 'missing', 'do not have']):
            error_category = "format"
            suggested_strategy = RetryStrategy.ENHANCED
        elif any(kw in error_lower for kw in ['word count', 'too many', 'too few', 'exceeds', 'below']):
            error_category = "content_length"
            suggested_strategy = RetryStrategy.ENHANCED
        elif any(kw in error_lower for kw in ['only', 'require', 'need']):
            error_category = "completeness"
            suggested_strategy = RetryStrategy.ENHANCED
        elif any(kw in error_lower for kw in ['no questions detected', 'no examples', 'no sections']):
            error_category = "missing_content"
            suggested_strategy = RetryStrategy.SIMPLIFIED
        
        # Check if we've seen this pattern before
        similar_patterns = [
            p for p in self.pattern_history
            if p.content_type == content_type and error_category in p.error_type.lower()
        ]
        
        # Find most successful strategy for this pattern
        if similar_patterns:
            strategy_success = defaultdict(int)
            for pattern in similar_patterns:
                if pattern.strategy_used and pattern.success:
                    strategy_success[pattern.strategy_used] += 1
            
            if strategy_success:
                best_strategy = max(strategy_success.items(), key=lambda x: x[1])[0]
                suggested_strategy = RetryStrategy(best_strategy) if best_strategy in [s.value for s in RetryStrategy] else RetryStrategy.ENHANCED
        
        return {
            'error_category': error_category,
            'suggested_strategy': suggested_strategy,
            'similar_patterns_found': len(similar_patterns),
            'success_rate_for_category': self._calculate_category_success_rate(error_category, content_type)
        }
    
    def _calculate_category_success_rate(self, error_category: str, content_type: str) -> float:
        """Calculate success rate for a specific error category.
        
        Args:
            error_category: Error category
            content_type: Content type
            
        Returns:
            Success rate (0.0-1.0)
        """
        category_patterns = [
            p for p in self.pattern_history
            if p.content_type == content_type and error_category in p.error_type.lower()
        ]
        
        if not category_patterns:
            return 0.0
        
        successes = sum(1 for p in category_patterns if p.success)
        return successes / len(category_patterns)
    
    def should_retry(
        self,
        error_message: str,
        content_type: str,
        attempt_count: int,
        max_retries: int
    ) -> Tuple[bool, Optional[RetryStrategy]]:
        """Determine if retry should be attempted and which strategy to use.
        
        Args:
            error_message: Error message
            content_type: Content type
            attempt_count: Current attempt count
            max_retries: Maximum retries allowed
            
        Returns:
            Tuple of (should_retry, suggested_strategy)
        """
        if attempt_count >= max_retries:
            return False, None
        
        # Analyze error pattern
        analysis = self.analyze_error_pattern(error_message, content_type)
        
        # Check success rate for this category
        success_rate = analysis['success_rate_for_category']
        
        # If success rate is very low (<20%), don't retry
        if success_rate < 0.2 and attempt_count > 0:
            logger.debug(f"Low success rate ({success_rate:.1%}) for error category, skipping retry")
            return False, None
        
        # Use suggested strategy
        strategy = analysis['suggested_strategy']
        
        return True, strategy
    
    def get_retry_feedback(
        self,
        error_message: str,
        content_type: str,
        previous_warnings: List[str],
        requirements: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate targeted retry feedback based on error patterns.
        
        Args:
            error_message: Error message
            content_type: Content type
            previous_warnings: List of previous warnings
            requirements: Content requirements dictionary
            
        Returns:
            Feedback string to add to prompt
        """
        analysis = self.analyze_error_pattern(error_message, content_type)
        error_category = analysis['error_category']
        
        # Generate category-specific feedback
        feedback_parts = []
        
        if error_category == "format":
            feedback_parts.append("FORMAT ISSUES DETECTED:")
            format_issues = [w for w in previous_warnings if any(k in w.lower() for k in ['format', 'missing', 'question marks'])]
            if format_issues:
                feedback_parts.append("\n".join(f"  - {w}" for w in format_issues[:3]))
            feedback_parts.append("\nCRITICAL: Ensure proper formatting (e.g., **Question N:** for questions)")
        
        elif error_category == "content_length":
            feedback_parts.append("CONTENT LENGTH ISSUES:")
            length_issues = [w for w in previous_warnings if any(k in w.lower() for k in ['word count', 'too many', 'too few', 'exceeds'])]
            if length_issues:
                feedback_parts.append("\n".join(f"  - {w}" for w in length_issues[:2]))
            if requirements:
                min_words = requirements.get('min_word_count', 0)
                max_words = requirements.get('max_word_count', 0)
                if min_words and max_words:
                    feedback_parts.append(f"\nCRITICAL: Ensure word count is between {min_words} and {max_words} words")
        
        elif error_category == "completeness":
            feedback_parts.append("COMPLETENESS ISSUES:")
            completeness_issues = [w for w in previous_warnings if any(k in w.lower() for k in ['only', 'require', 'need', 'missing'])]
            if completeness_issues:
                feedback_parts.append("\n".join(f"  - {w}" for w in completeness_issues[:3]))
            feedback_parts.append("\nCRITICAL: Ensure all required elements are present")
        
        elif error_category == "missing_content":
            feedback_parts.append("MISSING CONTENT ISSUES:")
            missing_issues = [w for w in previous_warnings if 'no ' in w.lower() or 'missing' in w.lower()]
            if missing_issues:
                feedback_parts.append("\n".join(f"  - {w}" for w in missing_issues[:3]))
            feedback_parts.append("\nCRITICAL: Ensure all required content types are generated")
        
        if not feedback_parts:
            # Generic feedback
            feedback_parts.append("PREVIOUS ATTEMPT ISSUES:")
            feedback_parts.append("\n".join(f"  - {w}" for w in previous_warnings[:3]))
        
        separator = "═" * 63
        return f"\n\n{separator}\nVALIDATION FEEDBACK FROM PREVIOUS ATTEMPT:\n{separator}\n\n" + "\n\n".join(feedback_parts)
    
    def get_stats(self, content_type: Optional[str] = None) -> RetryStats:
        """Get retry statistics.
        
        Args:
            content_type: Optional content type to filter by
            
        Returns:
            RetryStats object
        """
        if content_type:
            return self.content_type_stats.get(content_type, RetryStats())
        return self.stats
    
    def get_most_common_errors(self, content_type: Optional[str] = None, limit: int = 5) -> List[Tuple[str, int]]:
        """Get most common error types.
        
        Args:
            content_type: Optional content type to filter by
            limit: Maximum number of errors to return
            
        Returns:
            List of (error_type, count) tuples
        """
        if content_type:
            stats = self.content_type_stats.get(content_type, RetryStats())
        else:
            stats = self.stats
        
        sorted_errors = sorted(stats.error_frequency.items(), key=lambda x: x[1], reverse=True)
        return sorted_errors[:limit]


# Global instance for shared learning across generators
_global_retry_system = SmartRetrySystem()


def get_retry_system() -> SmartRetrySystem:
    """Get the global retry system instance.
    
    Returns:
        Global SmartRetrySystem instance
    """
    return _global_retry_system

