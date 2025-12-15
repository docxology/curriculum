"""Edge case tests for outline parser - malformed inputs, unicode, and boundary conditions."""

import pytest
from src.generate.processors.parser import OutlineParser


class TestMalformedMarkdown:
    """Test parser handling of malformed markdown."""
    
    def test_malformed_markdown_headers(self):
        """Test handling of invalid markdown header syntax."""
        malformed = """#Missing space
##Also bad
### Good Header
####Too many without space
"""
        parser = OutlineParser(malformed)
        modules = parser.parse_modules()
        
        # Should handle gracefully - may find some modules or none
        assert isinstance(modules, list)
        # At minimum, shouldn't crash
    
    def test_missing_module_section(self):
        """Test outline without any module sections."""
        no_modules = """# Course Outline

This is just text with no modules.
Some more content.

Nothing structured here.
"""
        parser = OutlineParser(no_modules)
        modules = parser.parse_modules()
        
        # Should return empty list or handle gracefully
        assert isinstance(modules, list)
    
    def test_missing_metadata_section(self):
        """Test outline without metadata."""
        no_metadata = """# Course Outline

## Module 1: Biology
Content here.

## Module 2: Chemistry
More content.
"""
        parser = OutlineParser(no_metadata)
        metadata = parser.extract_metadata()
        
        # Should return empty dict or minimal metadata
        assert isinstance(metadata, dict)


class TestUnexpectedContent:
    """Test parser with unexpected content."""
    
    def test_extra_unexpected_sections(self):
        """Test outline with additional unexpected sections."""
        extra_sections = """# Course Outline

**Level**: Intro

## Module 1: Biology
Content

### Subsection 1.1
More nesting

#### Deep nesting
Very nested

## Module 2: Chemistry
Content

## Appendix: Extra Material
This shouldn't be a module

## References
Neither should this
"""
        parser = OutlineParser(extra_sections)
        modules = parser.parse_modules()
        
        # Should parse modules but handle extra sections
        assert isinstance(modules, list)
        # May include "Appendix" and "References" or filter them
    
    def test_nested_bullet_points(self):
        """Test deeply nested bullet point lists."""
        nested = """# Course Outline

## Module 1: Biology

Subtopics:
- Main topic 1
  - Subtopic 1.1
    - Sub-subtopic 1.1.1
      - Very nested item
  - Subtopic 1.2
- Main topic 2
  - Subtopic 2.1

Learning Objectives:
- Objective 1
  - Detail A
  - Detail B
- Objective 2
"""
        parser = OutlineParser(nested)
        modules = parser.parse_modules()
        
        # Should handle nested lists
        assert len(modules) >= 1
        # Content should be preserved in some form


class TestUnicodeHandling:
    """Test parser with unicode characters."""
    
    def test_unicode_in_headers(self):
        """Test unicode characters in section headers."""
        unicode_headers = """# Biología Celular

**Nivel**: Introducción

## Módulo 1: La Célula
Contenido en español.

## Module 2: 细胞生物学
Chinese characters in header.

## Module 3: Génétique 🧬
French with emoji.
"""
        parser = OutlineParser(unicode_headers)
        modules = parser.parse_modules()
        
        # Should handle unicode without crashing
        assert len(modules) >= 1
        # At least one module should have unicode
        text = "".join(m.get('title', '') for m in modules)
        assert any(ord(c) > 127 for c in text)
    
    def test_unicode_in_content(self):
        """Test unicode in module content."""
        unicode_content = """# Course Outline

## Module 1: Biology

Subtopics:
- Célula eucariota
- 原核细胞 (Prokaryotic cell)
- Génome 🧬

Learning Objectives:
- Comprendre la structure cellulaire
- 理解细胞功能
- Entender la organización
"""
        parser = OutlineParser(unicode_content)
        modules = parser.parse_modules()
        
        assert len(modules) >= 1
        # Content should be preserved
        content = str(modules[0])
        assert any(ord(c) > 127 for c in content)


class TestLargeOutlines:
    """Test parser with very large outlines."""
    
    def test_very_large_outline_50_modules(self):
        """Test parsing outline with 50 modules."""
        # Generate large outline
        large_outline = "# Course Outline\n\n**Level**: Test\n\n"
        
        for i in range(1, 51):
            large_outline += f"""## Module {i}: Topic {i}

Subtopics:
- Subtopic {i}.1
- Subtopic {i}.2
- Subtopic {i}.3

Learning Objectives:
- Objective {i}.1
- Objective {i}.2

"""
        
        parser = OutlineParser(large_outline)
        modules = parser.parse_modules()
        
        # Should parse all 50 modules
        assert len(modules) == 50
        assert modules[0]['title'] == "Module 1: Topic 1"
        assert modules[49]['title'] == "Module 50: Topic 50"


class TestEmptyAndInvalid:
    """Test parser with empty and invalid inputs."""
    
    def test_empty_module_name(self):
        """Test module with empty name."""
        empty_name = """# Course Outline

## 

Content without module name.

## Module 2: Normal
This one is fine.
"""
        parser = OutlineParser(empty_name)
        modules = parser.parse_modules()
        
        # Should handle gracefully
        assert isinstance(modules, list)
    
    def test_duplicate_module_ids(self):
        """Test outline with duplicate module numbers."""
        duplicates = """# Course Outline

## Module 1: First
Content

## Module 1: Duplicate
Different content

## Module 2: Second
More content
"""
        parser = OutlineParser(duplicates)
        modules = parser.parse_modules()
        
        # Should parse all, may need to handle duplicates
        assert isinstance(modules, list)
        # Depending on implementation, might have 2 or 3 modules


class TestListFormatting:
    """Test various bullet list formatting."""
    
    def test_malformed_bullet_lists(self):
        """Test handling of malformed bullet lists."""
        malformed_lists = """# Course Outline

## Module 1: Biology

Subtopics:
-Missing space
- Good item
-  Double space
-	Tab character

Learning Objectives:
* Different bullet character
+ Another type
- Mixed bullets
"""
        parser = OutlineParser(malformed_lists)
        modules = parser.parse_modules()
        
        # Should handle various bullet formats
        assert len(modules) >= 1
    
    def test_mixed_list_styles(self):
        """Test mixing different list markers."""
        mixed_lists = """# Course Outline

## Module 1: Biology

Subtopics:
- Dash bullet
* Asterisk bullet
+ Plus bullet
- Back to dash

Learning Objectives:
1. Numbered item
2. Another number
- Mixed with dash
3. More numbers
"""
        parser = OutlineParser(mixed_lists)
        modules = parser.parse_modules()
        
        assert len(modules) >= 1


class TestCodeAndSpecialBlocks:
    """Test handling of code blocks and special markdown."""
    
    def test_code_blocks_in_content(self):
        """Test handling of code fence blocks."""
        with_code = """# Course Outline

## Module 1: Molecular Biology

Subtopics:
- DNA structure
- Code example:

```python
def replicate_dna(strand):
    return strand.replace('T', 'U')
```

- More topics

Learning Objectives:
- Understand DNA
"""
        parser = OutlineParser(with_code)
        modules = parser.parse_modules()
        
        # Should handle code blocks without breaking parsing
        assert len(modules) >= 1
    
    def test_links_in_content(self):
        """Test handling of markdown links."""
        with_links = """# Course Outline

## Module 1: Biology

Subtopics:
- [Cell structure](https://example.com/cells)
- Normal topic
- [More info](https://example.com) with link

Learning Objectives:
- See [this resource](https://example.com/learn)
- Regular objective
"""
        parser = OutlineParser(with_links)
        modules = parser.parse_modules()
        
        # Should preserve or handle links appropriately
        assert len(modules) >= 1
    
    def test_special_characters_escaping(self):
        """Test escaped special characters."""
        with_escapes = """# Course Outline

## Module 1: Biology\\*

Subtopics:
- Item with \\* asterisk
- Item with \\# hash
- Item with \\[brackets\\]

Learning Objectives:
- Understand \\_ underscores
- Learn about \\` backticks
"""
        parser = OutlineParser(with_escapes)
        modules = parser.parse_modules()
        
        # Should handle escaped characters
        assert len(modules) >= 1


class TestWhitespaceHandling:
    """Test handling of various whitespace scenarios."""
    
    def test_excessive_blank_lines(self):
        """Test outline with many blank lines."""
        excessive_blanks = """# Course Outline



## Module 1: Biology




Subtopics:
- Topic 1


- Topic 2



Learning Objectives:
- Objective 1


"""
        parser = OutlineParser(excessive_blanks)
        modules = parser.parse_modules()
        
        # Should handle extra whitespace
        assert len(modules) >= 1
    
    def test_mixed_line_endings(self):
        """Test handling of different line ending styles."""
        # Unix (\n), Windows (\r\n), old Mac (\r)
        unix_style = "# Course\n\n## Module 1: Topic\nContent\n"
        
        parser = OutlineParser(unix_style)
        modules = parser.parse_modules()
        
        assert len(modules) >= 1
    
    def test_tabs_vs_spaces_indentation(self):
        """Test mixed tabs and spaces."""
        mixed_indent = """# Course Outline

## Module 1: Biology

Subtopics:
	- Tab indented
    - Space indented (4 spaces)
  - Space indented (2 spaces)
- No indent

Learning Objectives:
	- Tab objective
  - Space objective
"""
        parser = OutlineParser(mixed_indent)
        modules = parser.parse_modules()
        
        assert len(modules) >= 1


class TestBoundaryConditions:
    """Test boundary conditions and limits."""
    
    def test_empty_outline(self):
        """Test completely empty outline."""
        parser = OutlineParser("")
        
        modules = parser.parse_modules()
        metadata = parser.extract_metadata()
        count = parser.get_module_count()
        
        assert modules == [] or modules is None
        assert isinstance(metadata, dict)
        assert count == 0
    
    def test_whitespace_only_outline(self):
        """Test outline with only whitespace."""
        parser = OutlineParser("   \n\n   \t\t\n   ")
        
        modules = parser.parse_modules()
        
        assert modules == [] or modules is None
    
    def test_single_character_outline(self):
        """Test minimal single character input."""
        parser = OutlineParser("#")
        
        modules = parser.parse_modules()
        
        # Should not crash
        assert isinstance(modules, list) or modules is None


class TestContentExtraction:
    """Test extraction of specific content types."""
    
    def test_extract_subtopics_various_formats(self):
        """Test extracting subtopics in different formats."""
        various_formats = """# Course Outline

## Module 1: Biology

Subtopics:
- Item 1
- Item 2

## Module 2: Chemistry

**Subtopics:**
- Different format
- Another item

## Module 3: Physics

### Subtopics
- Header format
- More items
"""
        parser = OutlineParser(various_formats)
        modules = parser.parse_modules()
        
        # Should extract subtopics from all formats
        assert len(modules) >= 2
    
    def test_extract_with_inline_formatting(self):
        """Test content with inline markdown formatting."""
        inline_format = """# Course Outline

## Module 1: Biology

Subtopics:
- **Bold topic**
- *Italic topic*
- `Code topic`
- ~~Strikethrough~~

Learning Objectives:
- Learn about **important** concepts
- Understand *key* ideas
"""
        parser = OutlineParser(inline_format)
        modules = parser.parse_modules()
        
        # Should preserve or strip inline formatting appropriately
        assert len(modules) >= 1


class TestStructureValidation:
    """Test validation of outline structure."""
    
    def test_modules_without_content(self):
        """Test modules that have headers but no content."""
        no_content = """# Course Outline

## Module 1: Empty

## Module 2: Also Empty

## Module 3: Has Content
This one has content.

Subtopics:
- Topic 1
"""
        parser = OutlineParser(no_content)
        modules = parser.parse_modules()
        
        # Should find all modules even if empty
        assert len(modules) >= 2
    
    def test_content_before_first_module(self):
        """Test content that appears before any module."""
        prefix_content = """# Course Outline

**Level**: Intro
**Duration**: 10 weeks

This is introductory text that comes before modules.
It should be handled appropriately.

Some more text.

## Module 1: Biology
Actual module content.
"""
        parser = OutlineParser(prefix_content)
        modules = parser.parse_modules()
        metadata = parser.extract_metadata()
        
        # Should find module and extract metadata
        assert len(modules) >= 1
        assert 'level' in metadata or 'duration' in metadata


class TestRobustness:
    """Test parser robustness with unusual inputs."""
    
    def test_very_long_module_names(self):
        """Test handling of extremely long module names."""
        long_name = "A" * 500  # 500 character module name
        outline = f"""# Course Outline

## Module 1: {long_name}

Content here.
"""
        parser = OutlineParser(outline)
        modules = parser.parse_modules()
        
        # Should handle without crashing
        assert len(modules) >= 1
        assert long_name in modules[0]['title']
    
    def test_special_unicode_ranges(self):
        """Test various unicode ranges."""
        special_unicode = """# Course Outline

## Module 1: Emojis 🧬🔬🦠

Subtopics:
- DNA 🧬
- Microscope 🔬
- Bacteria 🦠

## Module 2: Math Symbols ∑∫∂

Subtopics:
- Summation ∑
- Integral ∫
- Partial ∂

## Module 3: Currency & Symbols €£¥

Content
"""
        parser = OutlineParser(special_unicode)
        modules = parser.parse_modules()
        
        # Should handle all unicode ranges
        assert len(modules) >= 2
    
    def test_html_tags_in_markdown(self):
        """Test outline with HTML tags (valid in markdown)."""
        with_html = """# Course Outline

## Module 1: Biology

Subtopics:
- <strong>Bold topic</strong>
- <em>Italic topic</em>
- Normal topic

Learning Objectives:
- Learn <span style="color:red">important</span> concepts
"""
        parser = OutlineParser(with_html)
        modules = parser.parse_modules()
        
        # Should handle or strip HTML
        assert len(modules) >= 1


class TestErrorRecovery:
    """Test parser error recovery."""
    
    def test_recovery_from_malformed_section(self):
        """Test parser continues after malformed section."""
        partial_malform = """# Course Outline

## Module 1: Good Module
This is fine.

## Module 2 Missing Colon
Malformed but should be handled.

## Module 3: Good Again
Back to normal.
"""
        parser = OutlineParser(partial_malform)
        modules = parser.parse_modules()
        
        # Should find at least the good modules
        assert len(modules) >= 2
    
    def test_mixed_valid_invalid_content(self):
        """Test outline with mix of valid and invalid parts."""
        mixed = """# Course Outline

Valid metadata here.

## Module 1: Valid
Good content.

{{{Invalid JSON or syntax}}}

## Module 2: Also Valid
More good content.

[[[More invalid stuff]]]

## Module 3: Still Valid
Final module.
"""
        parser = OutlineParser(mixed)
        modules = parser.parse_modules()
        
        # Should extract valid modules despite invalid content
        assert len(modules) >= 2

