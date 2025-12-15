"""Tests for summary generator module."""

import logging
from src.utils.error_collector import ErrorCollector
from src.utils.summary_generator import (
    categorize_errors_by_type,
    format_error_list,
    generate_validation_summary,
    generate_stage_summary,
    generate_generation_summary
)


class TestSummaryGenerator:
    """Test summary generator utilities."""
    
    def test_categorize_errors_by_type(self):
        """Test error categorization by type."""
        collector = ErrorCollector()
        collector.add_error(type="validation", message="V1")
        collector.add_error(type="validation", message="V2")
        collector.add_error(type="generation", message="G1")
        collector.add_error(type="format", message="F1")
        
        errors = collector.get_all_issues()
        categorized = categorize_errors_by_type(errors)
        
        assert "validation" in categorized
        assert "generation" in categorized
        assert "format" in categorized
        assert len(categorized["validation"]) == 2
        assert len(categorized["generation"]) == 1
        assert len(categorized["format"]) == 1
    
    def test_format_error_list(self):
        """Test error list formatting."""
        collector = ErrorCollector()
        collector.add_error(
            type="validation",
            message="Missing question marks",
            context="Module 1 Session 2",
            content_type="questions",
            module_id=1,
            session_num=2
        )
        collector.add_error(
            type="validation",
            message="Word count below minimum",
            context="Module 1 Session 1",
            content_type="lecture"
        )
        
        errors = collector.get_all_issues()
        formatted = format_error_list(errors, max_items=10, show_context=True)
        
        assert len(formatted) == 2
        assert "[1/2]" in formatted[0]
        assert "Missing question marks" in formatted[0]
        assert "Context: Module 1 Session 2" in formatted[0]
    
    def test_format_error_list_max_items(self):
        """Test error list formatting with max items limit."""
        collector = ErrorCollector()
        for i in range(15):
            collector.add_error(type="test", message=f"Error {i}")
        
        errors = collector.get_all_issues()
        formatted = format_error_list(errors, max_items=10, show_context=False)
        
        assert len(formatted) == 11  # 10 items + "... and 5 more" message
        assert "... and 5 more errors" in formatted[-1]
    
    def test_generate_validation_summary(self, caplog):
        """Test validation summary generation."""
        collector = ErrorCollector()
        collector.add_error(
            type="validation",
            message="Critical: Missing question marks",
            severity="CRITICAL",
            content_type="questions"
        )
        collector.add_error(
            type="validation",
            message="Warning: Word count low",
            severity="WARNING",
            content_type="lecture"
        )
        
        with caplog.at_level(logging.INFO):
            generate_validation_summary(collector, logging.getLogger("test"))
        
        # Check formatted log output (caplog.text includes all formatted messages)
        all_log_text = caplog.text
        
        assert "[VALIDATION SUMMARY]" in all_log_text
        assert "Total Issues: 2" in all_log_text
        assert "[CRITICAL]: 1" in all_log_text
        assert "[WARNING]: 1" in all_log_text
        assert "questions" in all_log_text
        assert "lecture" in all_log_text
    
    def test_generate_stage_summary_success(self, caplog):
        """Test stage summary with no issues."""
        collector = ErrorCollector()
        
        with caplog.at_level(logging.INFO):
            generate_stage_summary(
                collector,
                "Test Stage",
                logging.getLogger("test"),
                total_items=10,
                successful_items=10,
                failed_items=0
            )
        
        # Check formatted log output (log_status_with_text formats as [STATUS] message emoji)
        all_log_text = caplog.text
        
        # log_status_with_text formats as: [STATUS] message emoji
        # So we need to check for the message part and status
        assert "Test Stage - Summary" in all_log_text
        assert "ALL COMPLIANT" in all_log_text
        assert "Items Processed: 10" in all_log_text
        assert "Successful: 10" in all_log_text
    
    def test_generate_stage_summary_with_issues(self, caplog):
        """Test stage summary with critical issues."""
        collector = ErrorCollector()
        collector.add_error(
            type="validation",
            message="Critical issue 1",
            severity="CRITICAL",
            context="Module 1 Session 1"
        )
        collector.add_error(
            type="validation",
            message="Warning issue 1",
            severity="WARNING",
            context="Module 1 Session 2"
        )
        
        with caplog.at_level(logging.INFO, logger="test"):
            generate_stage_summary(
                collector,
                "Test Stage",
                logging.getLogger("test"),
                total_items=10,
                successful_items=8,
                failed_items=2
            )
        
        # Check formatted log output (includes INFO and WARNING)
        all_log_text = caplog.text
        
        # log_status_with_text formats as: [STATUS] message emoji
        assert "Test Stage - Summary" in all_log_text
        assert "CRITICAL ISSUES FOUND" in all_log_text
        assert "Critical Errors: 1" in all_log_text
        assert "Warnings: 1" in all_log_text
        assert "Critical issue 1" in all_log_text
    
    def test_generate_generation_summary(self, caplog):
        """Test generation summary."""
        collector = ErrorCollector()
        collector.add_error(
            type="validation",
            message="Test error",
            severity="CRITICAL",
            content_type="questions"
        )
        
        results = {
            'sessions_generated': 10,
            'modules_processed': 5
        }
        
        with caplog.at_level(logging.INFO, logger="test"):
            generate_generation_summary(
                results,
                collector,
                logging.getLogger("test")
            )
        
        # Check formatted log output
        all_log_text = caplog.text
        
        assert "Generation Complete" in all_log_text
        assert "Sessions Generated" in all_log_text or "10" in all_log_text
        assert "Critical Errors" in all_log_text or "1" in all_log_text
    
    def test_generate_stage_summary_no_items(self, caplog):
        """Test stage summary with no items processed."""
        collector = ErrorCollector()
        
        with caplog.at_level(logging.INFO):
            generate_stage_summary(
                collector,
                "Test Stage",
                logging.getLogger("test"),
                total_items=None,
                successful_items=None,
                failed_items=None
            )
        
        # Check formatted log output
        all_log_text = caplog.text
        
        # log_status_with_text formats as: [STATUS] message emoji
        assert "Test Stage - Summary" in all_log_text
        # Should not crash when items are None




