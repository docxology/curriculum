"""Tests for website content_loader module."""

import pytest
from pathlib import Path
from src.website import content_loader


class TestContentLoader:
    """Test content_loader functions."""
    
    def test_get_content_types(self):
        """Test get_content_types returns all content types."""
        content_types = content_loader.get_content_types()
        
        assert isinstance(content_types, list)
        assert len(content_types) > 0
        # Check for primary content types
        assert "lecture" in content_types
        assert "lab" in content_types
        assert "study_notes" in content_types
        assert "questions" in content_types
        # Check for secondary content types
        assert "application" in content_types
        assert "extension" in content_types
        assert "visualization" in content_types
    
    def test_scan_module_content_valid_structure(self, tmp_path):
        """Test scan_module_content with valid module directory."""
        module_dir = tmp_path / "module_01_test"
        session_dir = module_dir / "session_01"
        session_dir.mkdir(parents=True)
        
        # Create all primary content files
        (session_dir / "lecture.md").write_text("# Lecture")
        (session_dir / "lab.md").write_text("# Lab")
        (session_dir / "study_notes.md").write_text("# Notes")
        (session_dir / "questions.md").write_text("# Questions")
        (session_dir / "diagram_1.mmd").write_text("graph TD\nA-->B")
        
        result = content_loader.scan_module_content(module_dir)
        
        assert "session_01" in result
        session_content = result["session_01"]
        
        assert session_content["lecture"] is not None
        assert session_content["lab"] is not None
        assert session_content["study_notes"] is not None
        assert session_content["questions"] is not None
        assert session_content["diagram_1"] is not None
    
    def test_scan_module_content_missing_sessions(self, tmp_path):
        """Test scan_module_content with missing session directories."""
        module_dir = tmp_path / "module_01_test"
        module_dir.mkdir()
        # No session directories
        
        result = content_loader.scan_module_content(module_dir)
        
        assert result == {}
    
    def test_scan_module_content_partial_content(self, tmp_path):
        """Test scan_module_content with partial content (some files missing)."""
        module_dir = tmp_path / "module_01_test"
        session_dir = module_dir / "session_01"
        session_dir.mkdir(parents=True)
        
        # Only create some files
        (session_dir / "lecture.md").write_text("# Lecture")
        # Missing lab.md, study_notes.md, etc.
        
        result = content_loader.scan_module_content(module_dir)
        
        assert "session_01" in result
        session_content = result["session_01"]
        
        assert session_content["lecture"] is not None
        assert session_content["lab"] is None
        assert session_content["study_notes"] is None
    
    def test_scan_module_content_nonexistent_directory(self, tmp_path):
        """Test scan_module_content with non-existent directory."""
        nonexistent_dir = tmp_path / "nonexistent_module"
        
        result = content_loader.scan_module_content(nonexistent_dir)
        
        # Should return empty dict, not raise
        assert result == {}
    
    def test_scan_module_content_multiple_sessions(self, tmp_path):
        """Test scan_module_content with multiple sessions."""
        module_dir = tmp_path / "module_01_test"
        session1_dir = module_dir / "session_01"
        session2_dir = module_dir / "session_02"
        session1_dir.mkdir(parents=True)
        session2_dir.mkdir()
        
        (session1_dir / "lecture.md").write_text("# Lecture 1")
        (session2_dir / "lecture.md").write_text("# Lecture 2")
        
        result = content_loader.scan_module_content(module_dir)
        
        assert "session_01" in result
        assert "session_02" in result
        assert result["session_01"]["lecture"] is not None
        assert result["session_02"]["lecture"] is not None
    
    def test_scan_module_content_diagram_discovery(self, tmp_path):
        """Test scan_module_content discovers multiple diagram files."""
        module_dir = tmp_path / "module_01_test"
        session_dir = module_dir / "session_01"
        session_dir.mkdir(parents=True)
        
        # Create multiple diagram files
        (session_dir / "diagram_1.mmd").write_text("graph TD\nA-->B")
        (session_dir / "diagram_2.mmd").write_text("graph LR\nC-->D")
        (session_dir / "diagram_3.mmd").write_text("graph TB\nE-->F")
        
        result = content_loader.scan_module_content(module_dir)
        
        session_content = result["session_01"]
        assert "diagram_1" in session_content
        assert "diagram_2" in session_content
        assert "diagram_3" in session_content
        assert session_content["diagram_1"] is not None
        assert session_content["diagram_2"] is not None
        assert session_content["diagram_3"] is not None
    
    def test_scan_module_content_no_diagrams(self, tmp_path):
        """Test scan_module_content when no diagrams exist."""
        module_dir = tmp_path / "module_01_test"
        session_dir = module_dir / "session_01"
        session_dir.mkdir(parents=True)
        
        (session_dir / "lecture.md").write_text("# Lecture")
        # No diagram files
        
        result = content_loader.scan_module_content(module_dir)
        
        session_content = result["session_01"]
        # Should have diagram_1 set to None
        assert session_content.get("diagram_1") is None
    
    def test_scan_module_content_secondary_types(self, tmp_path):
        """Test scan_module_content with secondary content types."""
        module_dir = tmp_path / "module_01_test"
        session_dir = module_dir / "session_01"
        session_dir.mkdir(parents=True)
        
        # Create secondary content files
        (session_dir / "application.md").write_text("# Application")
        (session_dir / "extension.md").write_text("# Extension")
        (session_dir / "visualization.mmd").write_text("graph TD\nA-->B")
        (session_dir / "integration.md").write_text("# Integration")
        
        result = content_loader.scan_module_content(module_dir)
        
        session_content = result["session_01"]
        assert session_content["application"] is not None
        assert session_content["extension"] is not None
        assert session_content["visualization"] is not None
        assert session_content["integration"] is not None
    
    def test_scan_module_content_visualization_is_mmd(self, tmp_path):
        """Test scan_module_content correctly identifies visualization.mmd."""
        module_dir = tmp_path / "module_01_test"
        session_dir = module_dir / "session_01"
        session_dir.mkdir(parents=True)
        
        # visualization should be .mmd, not .md
        (session_dir / "visualization.mmd").write_text("graph TD\nA-->B")
        (session_dir / "visualization.md").write_text("# Visualization")  # Wrong extension
        
        result = content_loader.scan_module_content(module_dir)
        
        session_content = result["session_01"]
        # Should find .mmd file, not .md
        assert session_content["visualization"] is not None
        assert session_content["visualization"].suffix == ".mmd"
    
    def test_load_markdown_content_valid_file(self, tmp_path):
        """Test load_markdown_content with valid markdown file."""
        markdown_file = tmp_path / "test.md"
        content = "# Test Heading\n\nThis is test content."
        markdown_file.write_text(content, encoding='utf-8')
        
        result = content_loader.load_markdown_content(markdown_file)
        
        assert result == content
    
    def test_load_markdown_content_nonexistent_file(self, tmp_path):
        """Test load_markdown_content raises FileNotFoundError for missing file."""
        nonexistent_file = tmp_path / "nonexistent.md"
        
        with pytest.raises(FileNotFoundError, match="File not found"):
            content_loader.load_markdown_content(nonexistent_file)
    
    def test_load_markdown_content_with_unicode(self, tmp_path):
        """Test load_markdown_content handles Unicode characters."""
        markdown_file = tmp_path / "unicode.md"
        content = "# Test\n\nSpecial: é ñ 中文 🧬"
        markdown_file.write_text(content, encoding='utf-8')
        
        result = content_loader.load_markdown_content(markdown_file)
        
        assert result == content
        assert "é" in result
        assert "🧬" in result
    
    def test_load_mermaid_content_valid_file(self, tmp_path):
        """Test load_mermaid_content with valid .mmd file."""
        mermaid_file = tmp_path / "test.mmd"
        content = "graph TD\nA-->B\nB-->C"
        mermaid_file.write_text(content, encoding='utf-8')
        
        result = content_loader.load_mermaid_content(mermaid_file)
        
        assert result == content
    
    def test_load_mermaid_content_nonexistent_file(self, tmp_path):
        """Test load_mermaid_content raises FileNotFoundError for missing file."""
        nonexistent_file = tmp_path / "nonexistent.mmd"
        
        with pytest.raises(FileNotFoundError, match="File not found"):
            content_loader.load_mermaid_content(nonexistent_file)
    
    def test_load_mermaid_content_with_special_chars(self, tmp_path):
        """Test load_mermaid_content handles special characters."""
        mermaid_file = tmp_path / "special.mmd"
        content = 'graph TD\nA["Label with quotes"]-->B["Another: label"]'
        mermaid_file.write_text(content, encoding='utf-8')
        
        result = content_loader.load_mermaid_content(mermaid_file)
        
        assert result == content
        assert '"Label with quotes"' in result
    
    def test_scan_module_content_sorted_sessions(self, tmp_path):
        """Test scan_module_content processes sessions in sorted order."""
        module_dir = tmp_path / "module_01_test"
        # Create sessions out of order
        session3_dir = module_dir / "session_03"
        session1_dir = module_dir / "session_01"
        session2_dir = module_dir / "session_02"
        session3_dir.mkdir(parents=True)
        session1_dir.mkdir()
        session2_dir.mkdir()
        
        (session1_dir / "lecture.md").write_text("# Session 1")
        (session2_dir / "lecture.md").write_text("# Session 2")
        (session3_dir / "lecture.md").write_text("# Session 3")
        
        result = content_loader.scan_module_content(module_dir)
        
        # Should be in sorted order
        session_keys = list(result.keys())
        assert session_keys == ["session_01", "session_02", "session_03"]
    
    def test_scan_module_content_ignores_non_session_dirs(self, tmp_path):
        """Test scan_module_content ignores directories not matching session_* pattern."""
        module_dir = tmp_path / "module_01_test"
        session_dir = module_dir / "session_01"
        other_dir = module_dir / "other_directory"
        session_dir.mkdir(parents=True)
        other_dir.mkdir()
        
        (session_dir / "lecture.md").write_text("# Lecture")
        (other_dir / "lecture.md").write_text("# Other")
        
        result = content_loader.scan_module_content(module_dir)
        
        # Should only include session_01, not other_directory
        assert "session_01" in result
        assert "other_directory" not in result







