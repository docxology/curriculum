"""Error and warning collector for content generation.

This module provides a centralized error collection system that categorizes
and tracks errors/warnings by severity, type, content type, and context.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class ErrorSeverity(Enum):
    """Error severity levels."""
    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    INFO = "INFO"


class ErrorType(Enum):
    """Error type categories."""
    VALIDATION = "validation"
    GENERATION = "generation"
    FORMAT = "format"
    CONTENT = "content"
    SYSTEM = "system"
    UNKNOWN = "unknown"


@dataclass
class ErrorEntry:
    """Structured error entry."""
    type: str
    severity: str
    message: str
    context: Optional[str] = None
    content_type: Optional[str] = None
    module_id: Optional[int] = None
    session_num: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class ErrorCollector:
    """Centralized error and warning collector.
    
    Collects, categorizes, and tracks errors/warnings during content generation.
    Provides methods to query, filter, and summarize collected issues.
    """
    
    def __init__(self):
        """Initialize empty error collector."""
        self._errors: List[ErrorEntry] = []
        self._warnings: List[ErrorEntry] = []
        self._info: List[ErrorEntry] = []
    
    def add_error(
        self,
        type: str,
        message: str,
        severity: str = "CRITICAL",
        context: Optional[str] = None,
        content_type: Optional[str] = None,
        module_id: Optional[int] = None,
        session_num: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add an error entry.
        
        Args:
            type: Error type (validation, generation, format, etc.)
            message: Error message
            severity: Severity level (CRITICAL, WARNING, INFO)
            context: Context string (e.g., "Module 1 Session 2")
            content_type: Content type (lecture, lab, questions, etc.)
            module_id: Module ID number
            session_num: Session number
            metadata: Additional metadata dictionary
        """
        entry = ErrorEntry(
            type=type,
            severity=severity.upper(),
            message=message,
            context=context,
            content_type=content_type,
            module_id=module_id,
            session_num=session_num,
            metadata=metadata or {}
        )
        
        severity_upper = severity.upper()
        if severity_upper == ErrorSeverity.CRITICAL.value:
            self._errors.append(entry)
        elif severity_upper == ErrorSeverity.WARNING.value:
            self._warnings.append(entry)
        else:
            self._info.append(entry)
    
    def add_warning(
        self,
        type: str,
        message: str,
        context: Optional[str] = None,
        content_type: Optional[str] = None,
        module_id: Optional[int] = None,
        session_num: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add a warning entry.
        
        Args:
            type: Warning type (validation, generation, format, etc.)
            message: Warning message
            context: Context string (e.g., "Module 1 Session 2")
            content_type: Content type (lecture, lab, questions, etc.)
            module_id: Module ID number
            session_num: Session number
            metadata: Additional metadata dictionary
        """
        self.add_error(
            type=type,
            message=message,
            severity="WARNING",
            context=context,
            content_type=content_type,
            module_id=module_id,
            session_num=session_num,
            metadata=metadata
        )
    
    def get_all_issues(self) -> List[ErrorEntry]:
        """Get all issues (errors, warnings, info) combined.
        
        Returns:
            List of all error entries sorted by severity (CRITICAL first)
        """
        all_issues = self._errors + self._warnings + self._info
        # Sort by severity: CRITICAL > WARNING > INFO
        severity_order = {
            ErrorSeverity.CRITICAL.value: 0,
            ErrorSeverity.WARNING.value: 1,
            ErrorSeverity.INFO.value: 2
        }
        return sorted(all_issues, key=lambda e: severity_order.get(e.severity, 99))
    
    def get_critical_issues(self) -> List[ErrorEntry]:
        """Get all critical issues.
        
        Returns:
            List of critical error entries
        """
        return self._errors.copy()
    
    def get_warnings(self) -> List[ErrorEntry]:
        """Get all warnings.
        
        Returns:
            List of warning entries
        """
        return self._warnings.copy()
    
    def get_info(self) -> List[ErrorEntry]:
        """Get all info-level entries.
        
        Returns:
            List of info entries
        """
        return self._info.copy()
    
    def get_by_content_type(self, content_type: str) -> List[ErrorEntry]:
        """Get all issues for a specific content type.
        
        Args:
            content_type: Content type to filter by
            
        Returns:
            List of error entries for the content type
        """
        return [
            entry for entry in self.get_all_issues()
            if entry.content_type == content_type
        ]
    
    def get_by_type(self, error_type: str) -> List[ErrorEntry]:
        """Get all issues of a specific error type.
        
        Args:
            error_type: Error type to filter by
            
        Returns:
            List of error entries of the specified type
        """
        return [
            entry for entry in self.get_all_issues()
            if entry.type == error_type
        ]
    
    def get_by_context(self, context: str) -> List[ErrorEntry]:
        """Get all issues for a specific context.
        
        Args:
            context: Context string to filter by
            
        Returns:
            List of error entries for the context
        """
        return [
            entry for entry in self.get_all_issues()
            if entry.context == context
        ]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics of collected issues.
        
        Returns:
            Dictionary with summary statistics:
            - total_errors: Count of critical errors
            - total_warnings: Count of warnings
            - total_info: Count of info entries
            - total_issues: Total count
            - by_content_type: Count by content type
            - by_error_type: Count by error type
            - by_severity: Count by severity
        """
        all_issues = self.get_all_issues()
        
        # Count by content type
        by_content_type: Dict[str, int] = {}
        for entry in all_issues:
            ct = entry.content_type or "unknown"
            by_content_type[ct] = by_content_type.get(ct, 0) + 1
        
        # Count by error type
        by_error_type: Dict[str, int] = {}
        for entry in all_issues:
            et = entry.type or "unknown"
            by_error_type[et] = by_error_type.get(et, 0) + 1
        
        # Count by severity
        by_severity: Dict[str, int] = {
            ErrorSeverity.CRITICAL.value: len(self._errors),
            ErrorSeverity.WARNING.value: len(self._warnings),
            ErrorSeverity.INFO.value: len(self._info)
        }
        
        return {
            "total_errors": len(self._errors),
            "total_warnings": len(self._warnings),
            "total_info": len(self._info),
            "total_issues": len(all_issues),
            "by_content_type": by_content_type,
            "by_error_type": by_error_type,
            "by_severity": by_severity
        }
    
    def clear(self) -> None:
        """Clear all collected errors and warnings."""
        self._errors.clear()
        self._warnings.clear()
        self._info.clear()
    
    def to_dict(self) -> Dict[str, Any]:
        """Export all issues to dictionary format.
        
        Returns:
            Dictionary with all issues in structured format
        """
        return {
            "errors": [
                {
                    "type": e.type,
                    "severity": e.severity,
                    "message": e.message,
                    "context": e.context,
                    "content_type": e.content_type,
                    "module_id": e.module_id,
                    "session_num": e.session_num,
                    "metadata": e.metadata
                }
                for e in self._errors
            ],
            "warnings": [
                {
                    "type": w.type,
                    "severity": w.severity,
                    "message": w.message,
                    "context": w.context,
                    "content_type": w.content_type,
                    "module_id": w.module_id,
                    "session_num": w.session_num,
                    "metadata": w.metadata
                }
                for w in self._warnings
            ],
            "info": [
                {
                    "type": i.type,
                    "severity": i.severity,
                    "message": i.message,
                    "context": i.context,
                    "content_type": i.content_type,
                    "module_id": i.module_id,
                    "session_num": i.session_num,
                    "metadata": i.metadata
                }
                for i in self._info
            ],
            "summary": self.get_summary()
        }
    
    def __len__(self) -> int:
        """Return total number of issues."""
        return len(self._errors) + len(self._warnings) + len(self._info)
    
    def __bool__(self) -> bool:
        """Return True if any issues collected."""
        return len(self) > 0
    
    def analyze_error_patterns(self) -> Dict[str, Any]:
        """Analyze error patterns to identify common failure modes.
        
        Returns:
            Dictionary with pattern analysis including:
            - most_common_errors: List of most frequent error types
            - error_trends: Trends in error frequency
            - content_type_patterns: Error patterns by content type
            - severity_distribution: Distribution of error severities
        """
        all_issues = self.get_all_issues()
        
        if not all_issues:
            return {
                'most_common_errors': [],
                'error_trends': {},
                'content_type_patterns': {},
                'severity_distribution': {}
            }
        
        # Count errors by type
        error_type_counts = defaultdict(int)
        for issue in all_issues:
            error_type_counts[issue.type] += 1
        
        # Most common errors
        most_common = sorted(error_type_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Error trends (by content type)
        content_type_patterns = defaultdict(lambda: defaultdict(int))
        for issue in all_issues:
            ct = issue.content_type or "unknown"
            content_type_patterns[ct][issue.type] += 1
        
        # Severity distribution
        severity_distribution = defaultdict(int)
        for issue in all_issues:
            severity_distribution[issue.severity] += 1
        
        return {
            'most_common_errors': [{'type': t, 'count': c} for t, c in most_common],
            'error_trends': dict(error_type_counts),
            'content_type_patterns': {
                ct: dict(patterns) for ct, patterns in content_type_patterns.items()
            },
            'severity_distribution': dict(severity_distribution),
            'total_issues': len(all_issues)
        }
    
    def suggest_recovery(self, error_type: str, content_type: str) -> List[str]:
        """Suggest recovery strategies based on error type and content type.
        
        Args:
            error_type: Type of error
            content_type: Type of content
            
        Returns:
            List of recovery suggestions
        """
        suggestions = []
        
        # Pattern-based suggestions
        if error_type == "validation":
            if content_type == "questions":
                suggestions.extend([
                    "Check question format: Use **Question N:** format",
                    "Ensure all questions end with '?'",
                    "Verify MC questions have exactly 4 options (A, B, C, D)",
                    "Add **Explanation:** sections for all MC questions"
                ])
            elif content_type == "lecture":
                suggestions.extend([
                    "Check word count is within required range",
                    "Ensure minimum number of examples are included",
                    "Verify section structure (use ## for major sections)",
                    "Add more concrete examples if needed"
                ])
            elif content_type == "study_notes":
                suggestions.extend([
                    "Ensure key concepts use **Concept:** format",
                    "Check concept count is within 3-10 range",
                    "Verify word count is under maximum"
                ])
        
        elif error_type == "format":
            suggestions.extend([
                "Review prompt template for format specifications",
                "Add format examples to prompt",
                "Check template variables are correctly filled"
            ])
        
        elif error_type == "generation":
            suggestions.extend([
                "Check LLM service is running and accessible",
                "Verify model is available and loaded",
                "Check timeout settings are appropriate",
                "Review prompt length and complexity"
            ])
        
        # If no specific suggestions, provide generic ones
        if not suggestions:
            suggestions.append("Review error message for specific guidance")
            suggestions.append("Check logs for detailed error information")
            suggestions.append("Consider regenerating with adjusted parameters")
        
        return suggestions
    
    def track_trends(self, time_window: Optional[int] = None) -> Dict[str, Any]:
        """Track error trends over time.
        
        Args:
            time_window: Optional time window in seconds (not implemented yet, uses all data)
            
        Returns:
            Dictionary with trend analysis
        """
        all_issues = self.get_all_issues()
        
        if not all_issues:
            return {
                'error_rate': 0.0,
                'trend': 'stable',
                'recent_errors': []
            }
        
        # Calculate error rate (errors per total issues)
        critical_count = len(self.get_critical_issues())
        warning_count = len(self.get_warnings())
        total = len(all_issues)
        
        error_rate = critical_count / total if total > 0 else 0.0
        
        # Determine trend (simplified - would need timestamps for real trend analysis)
        if error_rate > 0.5:
            trend = 'increasing'
        elif error_rate < 0.2:
            trend = 'decreasing'
        else:
            trend = 'stable'
        
        # Get recent errors (last 10)
        recent_errors = [
            {
                'type': e.type,
                'severity': e.severity,
                'message': e.message[:100],  # Truncate long messages
                'content_type': e.content_type
            }
            for e in all_issues[-10:]
        ]
        
        return {
            'error_rate': round(error_rate, 2),
            'trend': trend,
            'recent_errors': recent_errors,
            'critical_ratio': critical_count / total if total > 0 else 0.0
        }
    
    def assess_quality_impact(self) -> Dict[str, Any]:
        """Assess impact of errors on overall content quality.
        
        Returns:
            Dictionary with quality impact assessment
        """
        all_issues = self.get_all_issues()
        
        if not all_issues:
            return {
                'overall_impact': 'none',
                'quality_score_estimate': 100,
                'affected_content_types': [],
                'critical_blockers': []
            }
        
        # Calculate impact score (lower is worse)
        impact_score = 100.0
        
        # Deduct points for critical errors
        critical_errors = self.get_critical_issues()
        impact_score -= len(critical_errors) * 10
        
        # Deduct points for warnings
        warnings = self.get_warnings()
        impact_score -= len(warnings) * 2
        
        impact_score = max(0.0, impact_score)
        
        # Determine overall impact
        if impact_score >= 90:
            overall_impact = 'minimal'
        elif impact_score >= 75:
            overall_impact = 'moderate'
        elif impact_score >= 60:
            overall_impact = 'significant'
        else:
            overall_impact = 'severe'
        
        # Get affected content types
        affected_types = set()
        for issue in all_issues:
            if issue.content_type:
                affected_types.add(issue.content_type)
        
        # Get critical blockers (errors that prevent content from being usable)
        critical_blockers = [
            {
                'type': e.type,
                'message': e.message,
                'content_type': e.content_type,
                'context': e.context
            }
            for e in critical_errors[:5]  # Top 5 blockers
        ]
        
        return {
            'overall_impact': overall_impact,
            'quality_score_estimate': round(impact_score, 1),
            'affected_content_types': list(affected_types),
            'critical_blockers': critical_blockers,
            'total_issues': len(all_issues),
            'critical_count': len(critical_errors),
            'warning_count': len(warnings)
        }




