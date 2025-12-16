"""Tests for ErrorCollector edge cases and advanced scenarios.

Tests error collection with large datasets, mixed error types,
and various edge cases that might occur in real-world usage.
"""

import pytest
from src.utils.error_collector import ErrorCollector, ErrorEntry
from src.utils.summary_generator import (
    categorize_errors_by_type,
    format_error_list,
    generate_validation_summary,
    generate_stage_summary
)


class TestErrorCollectorEdgeCases:
    """Test ErrorCollector with edge cases and large datasets."""
    
    def test_large_error_collection(self):
        """Test error collection with a large number of errors."""
        collector = ErrorCollector()
        
        # Add 100 errors
        for i in range(100):
            collector.add_error(
                type="validation",
                message=f"Error {i}",
                severity="WARNING" if i % 2 == 0 else "CRITICAL",
                content_type="questions" if i % 3 == 0 else "lecture",
                module_id=(i % 5) + 1,
                session_num=(i % 3) + 1
            )
        
        summary = collector.get_summary()
        assert summary['total_issues'] == 100
        assert summary['total_errors'] == 50  # Half are CRITICAL
        assert summary['total_warnings'] == 50
    
    def test_mixed_error_types(self):
        """Test error collection with mixed error types and severities."""
        collector = ErrorCollector()
        
        # Add various error types
        collector.add_error(type="validation", message="V1", severity="CRITICAL")
        collector.add_error(type="validation", message="V2", severity="WARNING")
        collector.add_error(type="generation", message="G1", severity="CRITICAL")
        collector.add_error(type="format", message="F1", severity="WARNING")
        collector.add_error(type="network", message="N1", severity="CRITICAL")
        collector.add_error(type="unknown", message="U1", severity="INFO")
        
        summary = collector.get_summary()
        assert summary['total_issues'] == 6
        assert summary['total_errors'] == 3  # CRITICAL
        assert summary['total_warnings'] == 2
        assert summary['total_info'] == 1
        
        # Check by error type
        by_type = summary['by_error_type']
        assert by_type['validation'] == 2
        assert by_type['generation'] == 1
        assert by_type['format'] == 1
        assert by_type['network'] == 1
        assert by_type['unknown'] == 1
    
    def test_error_categorization_accuracy(self):
        """Test that error categorization correctly groups errors."""
        collector = ErrorCollector()
        
        # Add errors that should be categorized together
        collector.add_error(type="validation", message="V1")
        collector.add_error(type="validation", message="V2")
        collector.add_error(type="generation", message="G1")
        collector.add_error(type="generation", message="G2")
        collector.add_error(type="generation", message="G3")
        
        errors = collector.get_all_issues()
        categorized = categorize_errors_by_type(errors)
        
        assert len(categorized['validation']) == 2
        assert len(categorized['generation']) == 3
    
    def test_summary_with_mixed_content_types(self):
        """Test summary generation with errors across multiple content types."""
        collector = ErrorCollector()
        
        # Add errors for different content types
        collector.add_error(type="validation", message="Q1", content_type="questions")
        collector.add_error(type="validation", message="Q2", content_type="questions")
        collector.add_error(type="validation", message="L1", content_type="lecture")
        collector.add_error(type="validation", message="D1", content_type="diagram")
        collector.add_error(type="validation", message="SN1", content_type="study_notes")
        
        summary = collector.get_summary()
        by_content = summary['by_content_type']
        
        assert by_content['questions'] == 2
        assert by_content['lecture'] == 1
        assert by_content['diagram'] == 1
        assert by_content['study_notes'] == 1
    
    def test_format_error_list_with_max_items(self):
        """Test error list formatting respects max_items limit."""
        collector = ErrorCollector()
        
        # Add 20 errors
        for i in range(20):
            collector.add_error(type="test", message=f"Error {i}")
        
        errors = collector.get_all_issues()
        formatted = format_error_list(errors, max_items=10, show_context=False)
        
        # Should have 10 items + 1 "... and X more" message
        assert len(formatted) == 11
        assert "... and 10 more errors" in formatted[-1]
    
    def test_format_error_list_shows_context(self):
        """Test that error list formatting includes context when requested."""
        collector = ErrorCollector()
        
        collector.add_error(
            type="validation",
            message="Test error",
            context="Module 1 Session 2",
            module_id=1,
            session_num=2,
            content_type="questions"
        )
        
        errors = collector.get_all_issues()
        formatted = format_error_list(errors, max_items=10, show_context=True)
        
        assert len(formatted) == 1
        assert "Test error" in formatted[0]
        assert "Context: Module 1 Session 2" in formatted[0]
    
    def test_critical_issues_extraction(self):
        """Test that critical issues are correctly identified."""
        collector = ErrorCollector()
        
        collector.add_error(type="test", message="C1", severity="CRITICAL")
        collector.add_error(type="test", message="C2", severity="CRITICAL")
        collector.add_error(type="test", message="W1", severity="WARNING")
        collector.add_error(type="test", message="I1", severity="INFO")
        
        critical = collector.get_critical_issues()
        assert len(critical) == 2
        assert all(e.severity == "CRITICAL" for e in critical)
    
    def test_warnings_extraction(self):
        """Test that warnings are correctly identified."""
        collector = ErrorCollector()
        
        collector.add_error(type="test", message="W1", severity="WARNING")
        collector.add_error(type="test", message="W2", severity="WARNING")
        collector.add_error(type="test", message="C1", severity="CRITICAL")
        
        warnings = collector.get_warnings()
        assert len(warnings) == 2
        assert all(e.severity == "WARNING" for e in warnings)
    
    def test_empty_collector_summary(self):
        """Test summary generation with empty collector."""
        collector = ErrorCollector()
        
        summary = collector.get_summary()
        assert summary['total_issues'] == 0
        assert summary['total_errors'] == 0
        assert summary['total_warnings'] == 0
        assert summary['total_info'] == 0
        assert summary['by_content_type'] == {}
        assert summary['by_error_type'] == {}
    
    def test_stage_summary_with_large_dataset(self, caplog):
        """Test stage summary generation with large error dataset."""
        import logging
        
        collector = ErrorCollector()
        
        # Add 50 errors
        for i in range(50):
            collector.add_error(
                type="validation",
                message=f"Error {i}",
                severity="CRITICAL" if i % 5 == 0 else "WARNING",
                module_id=(i % 5) + 1,
                session_num=(i % 3) + 1
            )
        
        with caplog.at_level(logging.INFO):
            generate_stage_summary(
                collector,
                "Test Stage",
                logging.getLogger("test"),
                total_items=100,
                successful_items=50,
                failed_items=50
            )
        
        # Should complete without errors
        assert len(caplog.records) > 0
    
    def test_validation_summary_with_mixed_severities(self, caplog):
        """Test validation summary with mixed error severities."""
        import logging
        
        collector = ErrorCollector()
        
        # Add mixed severities
        for i in range(10):
            severity = ["CRITICAL", "WARNING", "INFO"][i % 3]
            collector.add_error(
                type="validation",
                message=f"Error {i}",
                severity=severity,
                content_type=["questions", "lecture", "diagram"][i % 3]
            )
        
        test_logger = logging.getLogger("test")
        with caplog.at_level(logging.INFO, logger="test"):
            generate_validation_summary(collector, test_logger)
        
        all_log_text = caplog.text
        assert "[VALIDATION SUMMARY]" in all_log_text
        assert "Total Issues: 10" in all_log_text

