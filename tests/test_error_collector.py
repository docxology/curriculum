"""Tests for error collector module."""

import pytest
from src.utils.error_collector import ErrorCollector, ErrorEntry, ErrorSeverity, ErrorType


class TestErrorCollector:
    """Test ErrorCollector class."""
    
    def test_init(self):
        """Test ErrorCollector initialization."""
        collector = ErrorCollector()
        assert len(collector) == 0
        assert not collector
        assert len(collector.get_all_issues()) == 0
    
    def test_add_error_critical(self):
        """Test adding critical error."""
        collector = ErrorCollector()
        collector.add_error(
            type="validation",
            message="Missing question marks",
            severity="CRITICAL",
            context="Module 1 Session 2",
            content_type="questions",
            module_id=1,
            session_num=2
        )
        
        assert len(collector) == 1
        assert len(collector.get_critical_issues()) == 1
        assert len(collector.get_warnings()) == 0
        assert len(collector.get_info()) == 0
        
        issue = collector.get_critical_issues()[0]
        assert issue.message == "Missing question marks"
        assert issue.severity == "CRITICAL"
        assert issue.context == "Module 1 Session 2"
        assert issue.content_type == "questions"
        assert issue.module_id == 1
        assert issue.session_num == 2
    
    def test_add_error_warning(self):
        """Test adding warning."""
        collector = ErrorCollector()
        collector.add_error(
            type="validation",
            message="Word count below minimum",
            severity="WARNING",
            context="Module 1 Session 1",
            content_type="lecture"
        )
        
        assert len(collector) == 1
        assert len(collector.get_critical_issues()) == 0
        assert len(collector.get_warnings()) == 1
        assert len(collector.get_info()) == 0
    
    def test_add_error_info(self):
        """Test adding info-level entry."""
        collector = ErrorCollector()
        collector.add_error(
            type="generation",
            message="Content generated successfully",
            severity="INFO",
            context="Module 1"
        )
        
        assert len(collector) == 1
        assert len(collector.get_critical_issues()) == 0
        assert len(collector.get_warnings()) == 0
        assert len(collector.get_info()) == 1
    
    def test_add_warning(self):
        """Test add_warning convenience method."""
        collector = ErrorCollector()
        collector.add_warning(
            type="validation",
            message="Diagram needs review",
            context="Module 2 Session 1",
            content_type="diagram"
        )
        
        assert len(collector) == 1
        assert len(collector.get_warnings()) == 1
        warning = collector.get_warnings()[0]
        assert warning.severity == "WARNING"
        assert warning.message == "Diagram needs review"
    
    def test_get_all_issues_sorted(self):
        """Test get_all_issues returns sorted by severity."""
        collector = ErrorCollector()
        
        # Add in mixed order
        collector.add_error(type="test", message="Info", severity="INFO")
        collector.add_error(type="test", message="Critical", severity="CRITICAL")
        collector.add_error(type="test", message="Warning", severity="WARNING")
        
        all_issues = collector.get_all_issues()
        assert len(all_issues) == 3
        # Should be sorted: CRITICAL, WARNING, INFO
        assert all_issues[0].severity == "CRITICAL"
        assert all_issues[1].severity == "WARNING"
        assert all_issues[2].severity == "INFO"
    
    def test_get_by_content_type(self):
        """Test filtering by content type."""
        collector = ErrorCollector()
        collector.add_error(type="test", message="Q1", content_type="questions")
        collector.add_error(type="test", message="Q2", content_type="questions")
        collector.add_error(type="test", message="L1", content_type="lecture")
        
        questions = collector.get_by_content_type("questions")
        assert len(questions) == 2
        assert all(q.content_type == "questions" for q in questions)
    
    def test_get_by_type(self):
        """Test filtering by error type."""
        collector = ErrorCollector()
        collector.add_error(type="validation", message="V1")
        collector.add_error(type="validation", message="V2")
        collector.add_error(type="generation", message="G1")
        
        validation = collector.get_by_type("validation")
        assert len(validation) == 2
        assert all(v.type == "validation" for v in validation)
    
    def test_get_by_context(self):
        """Test filtering by context."""
        collector = ErrorCollector()
        collector.add_error(type="test", message="M1", context="Module 1 Session 1")
        collector.add_error(type="test", message="M2", context="Module 1 Session 1")
        collector.add_error(type="test", message="M3", context="Module 2 Session 1")
        
        module1 = collector.get_by_context("Module 1 Session 1")
        assert len(module1) == 2
        assert all(m.context == "Module 1 Session 1" for m in module1)
    
    def test_get_summary(self):
        """Test summary generation."""
        collector = ErrorCollector()
        collector.add_error(type="validation", message="E1", severity="CRITICAL", content_type="questions")
        collector.add_error(type="validation", message="W1", severity="WARNING", content_type="lecture")
        collector.add_error(type="validation", message="W2", severity="WARNING", content_type="lecture")
        collector.add_error(type="generation", message="I1", severity="INFO")
        
        summary = collector.get_summary()
        
        assert summary['total_errors'] == 1
        assert summary['total_warnings'] == 2
        assert summary['total_info'] == 1
        assert summary['total_issues'] == 4
        assert summary['by_content_type']['questions'] == 1
        assert summary['by_content_type']['lecture'] == 2
        assert summary['by_error_type']['validation'] == 3
        assert summary['by_error_type']['generation'] == 1
        assert summary['by_severity']['CRITICAL'] == 1
        assert summary['by_severity']['WARNING'] == 2
        assert summary['by_severity']['INFO'] == 1
    
    def test_clear(self):
        """Test clearing all issues."""
        collector = ErrorCollector()
        collector.add_error(type="test", message="Test", severity="CRITICAL")
        collector.add_error(type="test", message="Test2", severity="WARNING")
        
        assert len(collector) == 2
        collector.clear()
        assert len(collector) == 0
        assert len(collector.get_all_issues()) == 0
    
    def test_to_dict(self):
        """Test exporting to dictionary."""
        collector = ErrorCollector()
        collector.add_error(
            type="validation",
            message="Test error",
            severity="CRITICAL",
            context="Module 1",
            content_type="questions",
            module_id=1,
            session_num=2,
            metadata={"key": "value"}
        )
        
        data = collector.to_dict()
        
        assert 'errors' in data
        assert 'warnings' in data
        assert 'info' in data
        assert 'summary' in data
        assert len(data['errors']) == 1
        assert data['errors'][0]['message'] == "Test error"
        assert data['errors'][0]['metadata']['key'] == "value"
    
    def test_bool(self):
        """Test boolean conversion."""
        collector = ErrorCollector()
        assert not collector
        
        collector.add_error(type="test", message="Test", severity="WARNING")
        assert collector
    
    def test_len(self):
        """Test length calculation."""
        collector = ErrorCollector()
        assert len(collector) == 0
        
        collector.add_error(type="test", message="E1", severity="CRITICAL")
        collector.add_error(type="test", message="W1", severity="WARNING")
        collector.add_error(type="test", message="I1", severity="INFO")
        
        assert len(collector) == 3
    
    def test_metadata(self):
        """Test metadata storage."""
        collector = ErrorCollector()
        collector.add_error(
            type="validation",
            message="Test",
            severity="CRITICAL",
            metadata={"category": "format", "impact": "high"}
        )
        
        issue = collector.get_critical_issues()[0]
        assert issue.metadata["category"] == "format"
        assert issue.metadata["impact"] == "high"




