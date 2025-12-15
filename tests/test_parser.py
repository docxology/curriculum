"""Tests for parser module."""

import pytest
from src.generate.processors.parser import OutlineParser


@pytest.fixture
def sample_outline():
    """Sample outline for testing."""
    return """# Introductory Biology - Course Outline

**Level**: Undergraduate  
**Duration**: 16 weeks  

---

## Module 1: Cell Biology

Subtopics:
- Cell structure and organization
- Membrane structure and function
- Organelles and their roles

Learning Objectives:
- Understand basic cell structure
- Explain organelle functions
- Describe membrane properties

## Module 2: Genetics

Subtopics:
- DNA structure
- Gene expression
- Inheritance patterns

Learning Objectives:
- Explain DNA structure
- Understand transcription and translation
- Apply Mendelian genetics

## Module 3: Evolution

Subtopics:
- Natural selection
- Adaptation
- Speciation

Learning Objectives:
- Explain natural selection
- Understand evolutionary mechanisms
"""


@pytest.fixture
def minimal_outline():
    """Minimal outline for testing."""
    return """# Course Outline

## Module 1: Topic A
Content about topic A.

## Module 2: Topic B
Content about topic B.
"""


class TestOutlineParser:
    """Test OutlineParser class."""
    
    def test_init(self, sample_outline):
        """Test parser initialization."""
        parser = OutlineParser(sample_outline)
        assert parser.outline_text == sample_outline
        
    def test_parse_modules(self, sample_outline):
        """Test parsing modules from outline."""
        parser = OutlineParser(sample_outline)
        modules = parser.parse_modules()
        
        assert len(modules) == 3
        assert modules[0]['title'] == "Module 1: Cell Biology"
        assert modules[1]['title'] == "Module 2: Genetics"
        assert modules[2]['title'] == "Module 3: Evolution"
        
    def test_extract_metadata(self, sample_outline):
        """Test extracting metadata from outline."""
        parser = OutlineParser(sample_outline)
        metadata = parser.extract_metadata()
        
        assert 'level' in metadata
        assert 'duration' in metadata
        assert 'Undergraduate' in metadata['level']
        assert '16 weeks' in metadata['duration']
        
    def test_get_module_count(self, sample_outline):
        """Test counting modules."""
        parser = OutlineParser(sample_outline)
        count = parser.get_module_count()
        
        assert count == 3
        
    def test_get_module_by_index(self, sample_outline):
        """Test retrieving specific module."""
        parser = OutlineParser(sample_outline)
        modules = parser.parse_modules()
        
        module = parser.get_module_by_index(0)
        assert module['title'] == "Module 1: Cell Biology"
        
        module = parser.get_module_by_index(1)
        assert module['title'] == "Module 2: Genetics"
        
    def test_get_module_by_index_invalid(self, sample_outline):
        """Test retrieving module with invalid index."""
        parser = OutlineParser(sample_outline)
        
        with pytest.raises(IndexError):
            parser.get_module_by_index(10)
            
    def test_extract_subtopics(self, sample_outline):
        """Test extracting subtopics from module."""
        parser = OutlineParser(sample_outline)
        modules = parser.parse_modules()
        
        subtopics = parser.extract_subtopics(modules[0]['content'])
        assert len(subtopics) >= 2
        assert any('cell structure' in s.lower() for s in subtopics)
        
    def test_extract_objectives(self, sample_outline):
        """Test extracting learning objectives."""
        parser = OutlineParser(sample_outline)
        modules = parser.parse_modules()
        
        objectives = parser.extract_objectives(modules[0]['content'])
        assert len(objectives) >= 2
        assert any('cell structure' in o.lower() for o in objectives)
        
    def test_parse_minimal_outline(self, minimal_outline):
        """Test parsing minimal outline format."""
        parser = OutlineParser(minimal_outline)
        modules = parser.parse_modules()
        
        assert len(modules) == 2
        assert modules[0]['title'] == "Module 1: Topic A"
        
    def test_to_dict(self, sample_outline):
        """Test converting parsed outline to dictionary."""
        parser = OutlineParser(sample_outline)
        result = parser.to_dict()
        
        assert 'metadata' in result
        assert 'modules' in result
        assert len(result['modules']) == 3
        
    def test_empty_outline(self):
        """Test handling empty outline."""
        parser = OutlineParser("")
        modules = parser.parse_modules()
        
        assert len(modules) == 0
        
    def test_outline_without_modules(self):
        """Test outline with no module markers."""
        outline = "# Course Title\n\nSome content without module markers."
        parser = OutlineParser(outline)
        modules = parser.parse_modules()
        
        assert len(modules) == 0
        
    def test_get_course_title(self, sample_outline):
        """Test extracting course title."""
        parser = OutlineParser(sample_outline)
        title = parser.get_course_title()
        
        assert "Introductory Biology" in title
        
    def test_get_course_title_no_title(self):
        """Test with outline that has no clear title."""
        parser = OutlineParser("No title here\nJust content")
        title = parser.get_course_title()
        
        assert title is None or len(title) == 0

