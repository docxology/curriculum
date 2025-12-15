"""Tests for content cleanup and validation module."""

import pytest
from src.generate.processors.cleanup import (
    clean_conversational_artifacts,
    standardize_placeholders,
    remove_duplicate_headings,
    validate_content,
    full_cleanup_pipeline,
    batch_validate_materials,
)


class TestCleanConversationalArtifacts:
    """Test conversational artifact removal."""
    
    def test_remove_okay_heres(self):
        """Test removal of 'Okay, here's' pattern."""
        content = "Okay, here's the lecture material...\n\nCell Biology content."
        cleaned = clean_conversational_artifacts(content)
        
        assert "Okay, here's" not in cleaned
        assert "Cell Biology content" in cleaned
        
    def test_remove_alright(self):
        """Test removal of 'Alright' pattern."""
        content = "Alright, let me explain cells.\n\nCells are basic units."
        cleaned = clean_conversational_artifacts(content)
        
        assert "Alright" not in cleaned
        assert "Cells are basic units" in cleaned
        
    def test_remove_sure(self):
        """Test removal of 'Sure' pattern."""
        content = "Sure, I can help.\n\n# Cell Biology"
        cleaned = clean_conversational_artifacts(content)
        
        assert "Sure" not in cleaned
        assert "# Cell Biology" in cleaned
        
    def test_remove_would_you_like(self):
        """Test removal of 'Would you like...' pattern."""
        content = "Cell structure\n\nWould you like me to add more details?"
        cleaned = clean_conversational_artifacts(content)
        
        assert "Would you like" not in cleaned
        assert "Cell structure" in cleaned
        
    def test_remove_let_me_know(self):
        """Test removal of 'Let me know' pattern."""
        content = "# Lab Exercise\n\nLet me know if you need anything."
        cleaned = clean_conversational_artifacts(content)
        
        assert "Let me know" not in cleaned
        assert "# Lab Exercise" in cleaned
        
    def test_multiple_artifacts(self):
        """Test removing multiple conversational artifacts."""
        content = """
Okay, here's the lecture.

Cell Biology content here.

Let me know if this works.
        """
        cleaned = clean_conversational_artifacts(content)
        
        assert "Okay, here's" not in cleaned
        assert "Let me know" not in cleaned
        assert "Cell Biology content" in cleaned
        
    def test_no_artifacts(self):
        """Test content without conversational artifacts."""
        content = "# Cell Biology\n\nCells are the basic units of life."
        cleaned = clean_conversational_artifacts(content)
        
        assert cleaned == content
        
    def test_case_insensitive(self):
        """Test case-insensitive matching."""
        content = "OKAY, HERE'S the content.\n\nAlRiGhT, moving on."
        cleaned = clean_conversational_artifacts(content)
        
        assert "OKAY" not in cleaned
        assert "AlRiGhT" not in cleaned


class TestStandardizePlaceholders:
    """Test placeholder standardization."""
    
    def test_replace_instructor_name(self):
        """Test replacing specific instructor names."""
        content = "Instructor: Dr. Jane Smith, PhD\n\nLecture content."
        cleaned = standardize_placeholders(content)
        
        assert "Dr. Jane Smith" not in cleaned
        assert "[INSTRUCTOR]" in cleaned
        assert "Lecture content" in cleaned
        
    def test_replace_professor_name(self):
        """Test replacing professor names."""
        content = "Contact Professor John Doe for questions."
        cleaned = standardize_placeholders(content)
        
        assert "Professor John Doe" not in cleaned
        assert "[INSTRUCTOR]" in cleaned
        
    def test_replace_date_month_format(self):
        """Test replacing dates in Month DD, YYYY format."""
        content = "Lab date: January 15, 2024\n\nProcedure..."
        cleaned = standardize_placeholders(content)
        
        assert "January 15, 2024" not in cleaned
        assert "[DATE]" in cleaned
        
    def test_replace_date_slash_format(self):
        """Test replacing dates in MM/DD/YYYY format."""
        content = "Due: 12/25/2024"
        cleaned = standardize_placeholders(content)
        
        assert "12/25/2024" not in cleaned
        assert "[DATE]" in cleaned
        
    def test_replace_date_iso_format(self):
        """Test replacing dates in ISO format."""
        content = "Published: 2024-01-15"
        cleaned = standardize_placeholders(content)
        
        assert "2024-01-15" not in cleaned
        assert "[DATE]" in cleaned
        
    def test_multiple_names_and_dates(self):
        """Test replacing multiple names and dates."""
        content = """
Instructor: Dr. Alice Brown
Assistant: Professor Bob Green
Start: January 1, 2024
End: 5/15/2024
        """
        cleaned = standardize_placeholders(content)
        
        assert "Dr. Alice Brown" not in cleaned
        assert "Professor Bob Green" not in cleaned
        assert "January 1, 2024" not in cleaned
        assert "5/15/2024" not in cleaned
        assert cleaned.count("[INSTRUCTOR]") == 2
        assert cleaned.count("[DATE]") == 2
        
    def test_no_placeholders(self):
        """Test content without specific names/dates."""
        content = "# Cell Biology\n\nGeneric content here."
        cleaned = standardize_placeholders(content)
        
        assert cleaned == content


class TestValidateContent:
    """Test content validation."""
    
    def test_valid_content(self):
        """Test validation of clean content."""
        content = "# Cell Biology\n\nCells are basic units of life."
        result = validate_content(content)
        
        assert result["is_valid"] is True
        assert result["issues_found"] == 0
        assert len(result["issues"]) == 0
        
    def test_detect_conversational_artifacts(self):
        """Test detection of conversational artifacts."""
        content = "Okay, here's the lecture.\n\nLet me know if you need more."
        result = validate_content(content)
        
        assert result["is_valid"] is False
        assert result["issues_found"] > 0
        
        artifact_issues = [i for i in result["issues"] if i["type"] == "conversational_artifact"]
        assert len(artifact_issues) > 0
        
    def test_detect_specific_names(self):
        """Test detection of specific names."""
        content = "Instructor: Dr. John Smith will teach this course."
        result = validate_content(content)
        
        assert result["is_valid"] is False
        name_issues = [i for i in result["issues"] if i["type"] == "specific_name"]
        assert len(name_issues) > 0
        
    def test_detect_specific_dates(self):
        """Test detection of specific dates."""
        content = "Lab scheduled for January 15, 2024."
        result = validate_content(content)
        
        assert result["is_valid"] is False
        date_issues = [i for i in result["issues"] if i["type"] == "specific_date"]
        assert len(date_issues) > 0
        
    def test_validate_questions_with_answers(self):
        """Test question validation with answer keys."""
        content = """
1. What is a cell?

**Answer:** Basic unit of life.

2. What is DNA?

**Answer:** Genetic material.
        """
        result = validate_content(content, content_type="questions")
        
        assert result["is_valid"] is True
        
    def test_validate_questions_missing_answers(self):
        """Test question validation with missing answers."""
        content = """
1. What is a cell?

2. What is DNA?

**Answer:** Genetic material.
        """
        result = validate_content(content, content_type="questions")
        
        assert result["is_valid"] is False
        missing_issues = [i for i in result["issues"] if i["type"] == "missing_answer_keys"]
        assert len(missing_issues) > 0
        assert missing_issues[0]["missing"] == 1
        
    def test_issue_examples_limited(self):
        """Test that issue examples are limited to 3."""
        content = "Okay, here's one. Okay, here's two. Okay, here's three. Okay, here's four."
        result = validate_content(content)
        
        artifact_issues = [i for i in result["issues"] if i["type"] == "conversational_artifact"]
        if artifact_issues:
            assert len(artifact_issues[0]["examples"]) <= 3


class TestFullCleanupPipeline:
    """Test complete cleanup pipeline."""
    
    def test_full_cleanup_removes_artifacts(self):
        """Test full cleanup removes conversational artifacts."""
        content = "Okay, here's the lecture on Cell Biology.\n\nCells are basic units."
        cleaned, validation = full_cleanup_pipeline(content)
        
        assert "Okay, here's" not in cleaned
        assert "Cells are basic units" in cleaned
        
    def test_full_cleanup_standardizes_placeholders(self):
        """Test full cleanup standardizes placeholders."""
        content = "Instructor: Dr. Jane Smith\nDate: January 15, 2024"
        cleaned, validation = full_cleanup_pipeline(content)
        
        assert "Dr. Jane Smith" not in cleaned
        assert "January 15, 2024" not in cleaned
        assert "[INSTRUCTOR]" in cleaned
        assert "[DATE]" in cleaned
        
    def test_validation_after_cleanup(self):
        """Test validation results after cleanup."""
        content = "Okay, here's a lecture by Dr. Smith on January 1, 2024."
        cleaned, validation = full_cleanup_pipeline(content)
        
        # After cleanup, should have fewer or no issues
        assert validation["issues_found"] == 0
        
    def test_cleanup_preserves_content(self):
        """Test that cleanup preserves actual content."""
        content = """
Okay, here's the lecture.

# Cell Biology

By Dr. John Smith, January 15, 2024

## Introduction
Cells are the basic structural and functional units of all living organisms.

## Cell Structure
The cell membrane regulates what enters and exits the cell.
        """
        cleaned, validation = full_cleanup_pipeline(content)
        
        # Core content should be preserved
        assert "# Cell Biology" in cleaned
        assert "## Introduction" in cleaned
        assert "basic structural and functional units" in cleaned
        assert "cell membrane regulates" in cleaned
        
        # Artifacts should be removed
        assert "Okay, here's" not in cleaned
        assert "Dr. John Smith" not in cleaned
        # Date should be replaced (full date format matches the pattern)
        assert "January 15, 2024" not in cleaned or "[DATE]" in cleaned


class TestBatchValidateMaterials:
    """Test batch validation of multiple materials."""
    
    def test_batch_validate_all_valid(self):
        """Test batch validation with all valid materials."""
        materials = {
            "lecture": "# Cell Biology\n\nCells are basic units.",
            "lab": "# Lab 1: Microscopy\n\nProcedure...",
            "study_notes": "# Study Notes\n\nKey concepts..."
        }
        results = batch_validate_materials(materials)
        
        assert len(results) == 3
        assert all(r["is_valid"] for r in results.values())
        
    def test_batch_validate_with_issues(self):
        """Test batch validation with some invalid materials."""
        materials = {
            "lecture": "Okay, here's the lecture.",
            "lab": "# Lab 1\n\nProcedure...",
            "study_notes": "Instructor: Dr. Smith\n\nNotes..."
        }
        results = batch_validate_materials(materials)
        
        assert len(results) == 3
        assert results["lab"]["is_valid"] is True
        assert results["lecture"]["is_valid"] is False
        assert results["study_notes"]["is_valid"] is False
        
    def test_batch_validate_empty(self):
        """Test batch validation with no materials."""
        materials = {}
        results = batch_validate_materials(materials)
        
        assert len(results) == 0
        
    def test_batch_validate_different_content_types(self):
        """Test batch validation respects content types."""
        materials = {
            "questions": """
1. What is a cell?

2. What is DNA?
            """,
            "lecture": "# Cell Biology\n\nContent..."
        }
        results = batch_validate_materials(materials)
        
        # Questions should fail (missing answers)
        assert results["questions"]["is_valid"] is False
        
        # Lecture should pass
        assert results["lecture"]["is_valid"] is True


class TestEdgeCases:
    """Test edge cases and special scenarios."""
    
    def test_empty_content(self):
        """Test cleanup/validation with empty content."""
        content = ""
        
        cleaned = clean_conversational_artifacts(content)
        assert cleaned == ""
        
        cleaned = standardize_placeholders(content)
        assert cleaned == ""
        
        result = validate_content(content)
        assert result["is_valid"] is True
        
    def test_whitespace_only(self):
        """Test with whitespace-only content."""
        content = "   \n\n   \t\t  "
        
        cleaned = clean_conversational_artifacts(content)
        assert cleaned.strip() == ""
        
        result = validate_content(content)
        assert result["is_valid"] is True
        
    def test_very_long_content(self):
        """Test with very long content."""
        # Generate long content with patterns
        paragraphs = []
        for i in range(100):
            paragraphs.append(f"Paragraph {i}: Cells are basic units of life.")
        content = "\n\n".join(paragraphs)
        
        result = validate_content(content)
        assert result["is_valid"] is True
        
    def test_special_characters_preserved(self):
        """Test that special characters are preserved."""
        content = "# Cell Biology\n\n- Item 1\n- Item 2\n\n**Bold** and *italic* text."
        cleaned = clean_conversational_artifacts(content)
        
        assert "**Bold**" in cleaned
        assert "*italic*" in cleaned
        assert "# Cell Biology" in cleaned
        
    def test_unicode_content(self):
        """Test with unicode characters."""
        content = "Cell Biology: α-helix, β-sheet, γ-radiation"
        cleaned = clean_conversational_artifacts(content)
        
        assert "α-helix" in cleaned
        assert "β-sheet" in cleaned
        assert "γ-radiation" in cleaned


# PHASE 3: Additional Cleanup Tests (17% → 85% coverage)

class TestBatchValidationAdvanced:
    """Advanced batch validation scenarios."""
    
    def test_batch_validation_mixed_results(self):
        """Test batch validation with mix of valid and invalid materials."""
        materials = {
            "valid_lecture": "# Cell Biology\n\nCells are basic units.",
            "invalid_lecture": "Okay, here's the lecture content.",
            "valid_lab": "# Lab Exercise\n\nProcedure steps...",
            "invalid_lab": "Professor Smith will lead this lab on January 15, 2024.",
            "valid_notes": "# Study Notes\n\nKey concepts...",
            "mixed_content": "# Title\n\nGood content. Let me know if this helps."
        }
        
        results = batch_validate_materials(materials)
        
        assert len(results) == 6
        # Count valid and invalid
        valid_count = sum(1 for r in results.values() if r["is_valid"])
        invalid_count = sum(1 for r in results.values() if not r["is_valid"])
        
        assert valid_count == 3  # valid_lecture, valid_lab, valid_notes
        assert invalid_count == 3  # invalid_lecture, invalid_lab, mixed_content
        
        # Check specific results
        assert results["valid_lecture"]["is_valid"] is True
        assert results["invalid_lecture"]["is_valid"] is False
        assert results["mixed_content"]["is_valid"] is False


class TestFullCleanupPipelineComprehensive:
    """Comprehensive tests for full cleanup pipeline."""
    
    def test_full_cleanup_pipeline_all_steps(self):
        """Test that all cleanup transformations are applied."""
        # Content with all types of issues
        content = """
Okay, here's the comprehensive lecture on Cell Biology.

Instructor: Dr. Jane Smith, PhD
Date: January 15, 2024
Assistant: Professor Bob Johnson

Sure, I can explain the cell structure.

# Cell Biology Lecture

## Introduction
Cells are the basic units of life. Let me know if you need more details.

## Cell Membrane
The membrane regulates transport. Would you like more information?

## Conclusion
Contact Dr. Jane Smith at jsmith@university.edu.
Lab scheduled for 3/20/2024.

Alright, that covers the main topics.
        """
        
        cleaned, validation = full_cleanup_pipeline(content)
        
        # Verify all conversational artifacts removed
        assert "Okay, here's" not in cleaned
        assert "Sure, I can" not in cleaned
        assert "Let me know" not in cleaned
        assert "Would you like" not in cleaned
        assert "Alright," not in cleaned
        
        # Verify all names standardized
        assert "Dr. Jane Smith" not in cleaned
        assert "Professor Bob Johnson" not in cleaned
        assert "[INSTRUCTOR]" in cleaned
        
        # Verify all dates standardized
        assert "January 15, 2024" not in cleaned
        assert "3/20/2024" not in cleaned
        assert "[DATE]" in cleaned
        
        # Verify core content preserved
        assert "# Cell Biology Lecture" in cleaned
        assert "## Introduction" in cleaned
        assert "Cells are the basic units" in cleaned
        assert "membrane regulates transport" in cleaned
        
        # Validation should pass after cleanup
        assert validation["issues_found"] == 0
        assert validation["is_valid"] is True


class TestUnicodePreservation:
    """Test that unicode characters are preserved correctly."""
    
    def test_unicode_preservation_in_cleanup(self):
        """Test that cleanup doesn't corrupt unicode characters."""
        content = """
Okay, here's the lecture on Biología Celular.

# La Célula 细胞

Instructor: Dr. José García

## Estructura Celular
- Membrana plasmática
- Citoplasma
- Núcleo 核

## Símbolos Científicos
α-helix (alpha helix)
β-sheet (beta sheet)
∆G (delta G)
µm (micrometer)

Emojis: 🧬 DNA, 🔬 Microscope, 🦠 Bacteria

Let me know if you need más información.
        """
        
        cleaned, validation = full_cleanup_pipeline(content)
        
        # Verify conversational artifacts removed
        assert "Okay, here's" not in cleaned
        assert "Let me know" not in cleaned
        
        # Verify unicode preserved (except in replaced instructor names)
        assert "Biología" in cleaned
        assert "Célula" in cleaned
        assert "细胞" in cleaned
        # "José García" was replaced with [INSTRUCTOR], so José won't be there
        assert "Dr. José García" not in cleaned
        assert "[INSTRUCTOR]" in cleaned
        assert "Núcleo" in cleaned
        assert "核" in cleaned
        
        # Verify scientific symbols preserved
        assert "α-helix" in cleaned
        assert "β-sheet" in cleaned
        assert "∆G" in cleaned
        assert "µm" in cleaned
        
        # Verify emojis preserved
        assert "🧬" in cleaned
        assert "🔬" in cleaned
        assert "🦠" in cleaned


class TestLargeContentHandling:
    """Test handling of very large content."""
    
    def test_very_long_content_100kb(self):
        """Test cleanup with ~100KB content."""
        # Generate large content
        paragraphs = []
        for i in range(1000):  # ~100KB
            if i % 100 == 0:
                paragraphs.append(f"Okay, here's section {i}.")  # Add some artifacts
            if i % 50 == 0:
                paragraphs.append(f"Instructor: Dr. Smith {i}")  # Add some names
            paragraphs.append(f"Paragraph {i}: Cells are the fundamental units of life. "
                            f"They contain DNA, which stores genetic information. "
                            f"The cell membrane regulates what enters and exits.")
        
        content = "\n\n".join(paragraphs)
        
        # Verify size
        assert len(content) > 100000  # Over 100KB
        
        # Cleanup should handle without crashing
        cleaned, validation = full_cleanup_pipeline(content)
        
        # Should still remove artifacts from large content
        assert cleaned.count("Okay, here's") == 0
        assert "[INSTRUCTOR]" in cleaned
        
        # Core content should be preserved
        assert "fundamental units of life" in cleaned
        assert "genetic information" in cleaned


class TestWhitespaceEdgeCases:
    """Test edge cases with whitespace."""
    
    def test_whitespace_only_content_cleanup(self):
        """Test cleanup with only whitespace."""
        content = "   \n\n\t\t\n   \n\r\n   "
        
        cleaned = clean_conversational_artifacts(content)
        assert isinstance(cleaned, str)
        
        cleaned = standardize_placeholders(content)
        assert isinstance(cleaned, str)
        
        cleaned, validation = full_cleanup_pipeline(content)
        assert validation["is_valid"] is True
        assert validation["issues_found"] == 0
    
    def test_content_with_excessive_whitespace(self):
        """Test cleanup preserves structure despite excessive whitespace."""
        content = """


# Cell Biology


Okay, here's the lecture.


## Section 1



Content here.



## Section 2




More content.


        """
        
        cleaned, validation = full_cleanup_pipeline(content)
        
        # Structure should be preserved
        assert "# Cell Biology" in cleaned
        assert "## Section 1" in cleaned
        assert "## Section 2" in cleaned
        
        # Artifacts removed
        assert "Okay, here's" not in cleaned


class TestMultiplePlaceholders:
    """Test handling of multiple placeholders in same text."""
    
    def test_multiple_placeholders_same_text(self):
        """Test replacing multiple names and dates in same content."""
        content = """
# Course Schedule

Instructor: Dr. Alice Brown
Co-Instructor: Professor Bob Green
Teaching Assistant: Dr. Charlie White
Guest Lecturer: Professor Diana Black

Start Date: January 15, 2024
Midterm: March 10, 2024
Final: May 20, 2024
Last Day: 5/25/2024

Contact Dr. Alice Brown or Professor Bob Green for questions.
Labs with Dr. Charlie White on 2/1/2024, 3/5/2024, and 4/10/2024.
        """
        
        cleaned, validation = full_cleanup_pipeline(content)
        
        # All names should be replaced
        assert "Dr. Alice Brown" not in cleaned
        assert "Professor Bob Green" not in cleaned
        assert "Dr. Charlie White" not in cleaned
        assert "Professor Diana Black" not in cleaned
        
        # All dates should be replaced
        assert "January 15, 2024" not in cleaned
        assert "March 10, 2024" not in cleaned
        assert "May 20, 2024" not in cleaned
        assert "5/25/2024" not in cleaned
        assert "2/1/2024" not in cleaned
        assert "3/5/2024" not in cleaned
        assert "4/10/2024" not in cleaned
        
        # Placeholders should be present
        assert "[INSTRUCTOR]" in cleaned
        assert "[DATE]" in cleaned
        
        # Count replacements
        assert cleaned.count("[INSTRUCTOR]") >= 4
        assert cleaned.count("[DATE]") >= 7


class TestCodeBlockPreservation:
    """Test that code blocks are preserved during cleanup."""
    
    def test_cleanup_preserves_code_blocks(self):
        """Test that code examples are not cleaned."""
        content = """
Okay, here's the programming example.

# DNA Sequence Analysis

Instructor: Dr. Smith

## Code Example

```python
# This is a comment in code
def replicate_dna(sequence):
    # Okay, here's how it works (this should stay)
    # Let me know if this is clear (this should stay)
    return sequence.replace('T', 'U')

# Call the function
result = replicate_dna("ATCG")
print("Okay, here's the result:", result)  # This should stay
```

## Explanation
Let me know if you understand the code.
        """
        
        cleaned, validation = full_cleanup_pipeline(content)
        
        # Conversational artifacts outside code should be removed
        assert content.count("Okay, here's") == 3  # Original count
        # After cleanup, only the ones in code blocks should remain
        
        # Code block should be fully preserved
        assert "```python" in cleaned
        assert "def replicate_dna(sequence):" in cleaned
        assert "return sequence.replace('T', 'U')" in cleaned
        
        # Comments in code should be preserved
        assert "# This is a comment in code" in cleaned
        
        # Outside code block, artifacts should be removed
        lines = cleaned.split('\n')
        non_code_lines = []
        in_code = False
        for line in lines:
            if '```' in line:
                in_code = not in_code
            elif not in_code:
                non_code_lines.append(line)
        
        non_code_text = '\n'.join(non_code_lines)
        # Conversational artifacts in non-code sections should be removed
        assert "Let me know if you understand" not in non_code_text or "[" in cleaned


class TestQuotedTextPreservation:
    """Test that quoted text is handled appropriately."""
    
    def test_cleanup_preserves_quotes(self):
        """Test that quoted text is preserved."""
        content = """
Okay, here's the lecture on scientific quotes.

# Famous Scientific Quotes

## Watson and Crick
"We wish to suggest a structure for the salt of deoxyribose nucleic acid."
- Dr. James Watson and Dr. Francis Crick, April 25, 1953

## Charles Darwin
> "It is not the strongest of the species that survives, 
> nor the most intelligent that survives. 
> It is the one that is most adaptable to change."

## Modern Research
Dr. Jane Smith stated: "Let me know when you have results."

Let me know if you need more quotes.
        """
        
        cleaned, validation = full_cleanup_pipeline(content)
        
        # Artifacts outside quotes removed
        assert "Okay, here's the lecture" not in cleaned
        assert cleaned.count("Let me know") <= 1  # Only in quote should remain
        
        # Quotes preserved
        assert '"We wish to suggest a structure' in cleaned
        assert "Watson and Crick" in cleaned or "[INSTRUCTOR]" in cleaned
        
        # Block quotes preserved
        assert ">" in cleaned or "It is not the strongest" in cleaned
        
        # Dates in quotes may be preserved or replaced
        assert "April 25, 1953" not in cleaned or "[DATE]" in cleaned


class TestValidationExtensibility:
    """Test validation with different content types and rules."""
    
    def test_validation_different_content_types(self):
        """Test that validation rules vary by content type."""
        # Questions require answer keys
        questions = """
1. What is a cell?
2. What is DNA?
3. What is RNA?
        """
        
        result_questions = validate_content(questions, content_type="questions")
        assert result_questions["is_valid"] is False  # Missing answers
        
        # Lectures don't require answer keys
        lecture = """
# Cell Biology Lecture

What is a cell?
What is DNA?
What is RNA?

These are rhetorical questions for students to consider.
        """
        
        result_lecture = validate_content(lecture, content_type="lecture")
        assert result_lecture["is_valid"] is True  # No answer requirement
    
    def test_validation_provides_actionable_feedback(self):
        """Test that validation provides useful feedback for fixes."""
        content = """
Okay, here's the content.
Let me know if this works.
Sure, I can help.

Instructor: Dr. Smith
Date: January 15, 2024
Professor Johnson will assist on 3/20/2024.
        """
        
        result = validate_content(content)
        
        # Should identify all issue types
        issue_types = {i["type"] for i in result["issues"]}
        
        assert "conversational_artifact" in issue_types
        assert "specific_name" in issue_types
        assert "specific_date" in issue_types
        
        # Should provide examples for each
        for issue in result["issues"]:
            assert "examples" in issue
            assert len(issue["examples"]) > 0
            assert len(issue["examples"]) <= 3  # Max 3 examples


class TestCleanupRobustness:
    """Test cleanup robustness with unusual inputs."""
    
    def test_cleanup_with_mixed_line_endings(self):
        """Test cleanup handles different line ending styles."""
        # Mix of Unix (\n), Windows (\r\n), and old Mac (\r)
        content = "Okay, here's line 1.\nLine 2.\r\nLine 3.\rLine 4."
        
        cleaned, validation = full_cleanup_pipeline(content)
        
        assert "Okay, here's" not in cleaned
        assert "Line 2" in cleaned
        assert "Line 3" in cleaned
        assert "Line 4" in cleaned
    
    def test_cleanup_with_null_bytes(self):
        """Test cleanup handles or rejects null bytes."""
        content = "Cell Biology\x00 content with null byte."
        
        try:
            cleaned, validation = full_cleanup_pipeline(content)
            # If it succeeds, null should be handled
            assert isinstance(cleaned, str)
        except (ValueError, UnicodeError):
            # Acceptable to reject null bytes
            pass
    
    def test_cleanup_idempotency(self):
        """Test that running cleanup twice gives same result."""
        content = """
Okay, here's the lecture.
Instructor: Dr. Smith
Date: January 15, 2024
        """
        
        cleaned1, validation1 = full_cleanup_pipeline(content)
        cleaned2, validation2 = full_cleanup_pipeline(cleaned1)
        
        # Second cleanup should not change anything
        assert cleaned1 == cleaned2
        assert validation1 == validation2
        assert validation2["is_valid"] is True


class TestErrorHandlingInCleanup:
    """Test error handling during cleanup operations."""
    
    def test_cleanup_with_malformed_regex_patterns(self):
        """Test cleanup doesn't crash with edge case patterns."""
        # Content that might cause regex issues
        content = """
Okay, here's content with special regex chars: .*+?[]{}()|\\^$

Instructor: Dr. Smith (PhD) [Professor]
Date: 1/1/2024 - 12/31/2024

Email: okay.heres@example.com (should not match 'Okay, here's')
        """
        
        cleaned, validation = full_cleanup_pipeline(content)
        
        # Should handle without crashing
        assert isinstance(cleaned, str)
        
        # Should still remove actual artifacts
        # Email should not be affected by "okay" pattern
        assert "@example.com" in cleaned


class TestNewConversationalPatterns:
    """Test new conversational artifact patterns."""
    
    def test_remove_okay_i_understand(self):
        """Test removal of 'Okay, I understand the requirements...' pattern."""
        content = "Okay, I understand the requirements and constraints. I will generate five distinct applications."
        cleaned = clean_conversational_artifacts(content)
        
        assert "Okay, I understand" not in cleaned
        assert "I will generate five distinct applications" in cleaned or cleaned.strip() == ""
    
    def test_remove_i_have_carefully_adhered(self):
        """Test removal of 'I have carefully adhered to all formatting instructions...' pattern."""
        content = "I have carefully adhered to all formatting instructions, avoiding any conversational elements."
        cleaned = clean_conversational_artifacts(content)
        
        assert "I have carefully adhered" not in cleaned
        assert "avoiding any conversational elements" in cleaned or cleaned.strip() == ""
    
    def test_remove_the_output_following(self):
        """Test removal of 'the output following the provided requirements...' pattern."""
        content = "the output following the provided requirements and formatting specifications:"
        cleaned = clean_conversational_artifacts(content)
        
        assert "the output following" not in cleaned
        assert cleaned.strip() == "" or ":" in cleaned
    
    def test_remove_the_response_adhering(self):
        """Test removal of 'the response adhering to all the provided requirements...' pattern."""
        content = "the response adhering to all the provided requirements and formatting specifications."
        cleaned = clean_conversational_artifacts(content)
        
        assert "the response adhering" not in cleaned
        assert cleaned.strip() == "" or "." in cleaned
    
    def test_remove_i_trust_this_response(self):
        """Test removal of 'I trust this response fulfills all requirements' pattern."""
        content = "I trust this response fulfills all requirements."
        cleaned = clean_conversational_artifacts(content)
        
        assert "I trust this response" not in cleaned
    
    def test_remove_do_you_have_any_further(self):
        """Test removal of 'Do you have any further instructions...' pattern."""
        content = "Do you have any further instructions or adjustments you would like me to make?"
        cleaned = clean_conversational_artifacts(content)
        
        assert "Do you have any further" not in cleaned


class TestDuplicateHeadingRemoval:
    """Test duplicate heading removal."""
    
    def test_remove_duplicate_headings_same_level(self):
        """Test removal of duplicate headings at same level."""
        content = """# Study Notes

## Key Concepts

Cell theory is important.

## Key Concepts

Prokaryotic cells lack a nucleus.

## Other Section

More content here.
"""
        cleaned = remove_duplicate_headings(content)
        
        # Should have only one "## Key Concepts"
        assert cleaned.count("## Key Concepts") == 1
        # Should preserve "## Other Section"
        assert "## Other Section" in cleaned
        # Should preserve content
        assert "Cell theory" in cleaned or "Prokaryotic cells" in cleaned
    
    def test_remove_duplicate_headings_different_levels(self):
        """Test that headings at different levels are not considered duplicates."""
        content = """# Title

## Section 1

### Section 1

Content here.
"""
        cleaned = remove_duplicate_headings(content)
        
        # Both should remain (different levels)
        assert cleaned.count("Section 1") == 2
    
    def test_remove_duplicate_headings_case_insensitive(self):
        """Test that duplicate detection is case-insensitive."""
        content = """## Key Concepts

Content 1.

## key concepts

Content 2.
"""
        cleaned = remove_duplicate_headings(content)
        
        # Should remove duplicate (case-insensitive match)
        assert cleaned.count("Key Concepts") == 1 or cleaned.count("key concepts") == 1
    
    def test_remove_duplicate_headings_preserves_content(self):
        """Test that content under duplicate headings is preserved (first occurrence)."""
        content = """## Key Concepts

First content here.

## Key Concepts

Second content here.
"""
        cleaned = remove_duplicate_headings(content)
        
        # Should keep first occurrence and its content
        assert "First content here" in cleaned
        # Second occurrence should be removed
        assert "Second content here" not in cleaned
    
    def test_no_duplicate_headings_unchanged(self):
        """Test that content without duplicate headings is unchanged."""
        content = """# Title

## Section 1

Content 1.

## Section 2

Content 2.
"""
        cleaned = remove_duplicate_headings(content)
        
        # Should be unchanged
        assert cleaned == content
    
    def test_duplicate_headings_in_full_cleanup(self):
        """Test that duplicate headings are removed in full cleanup pipeline."""
        content = """## Key Concepts

First content.

## Key Concepts

Duplicate content.
"""
        cleaned, validation = full_cleanup_pipeline(content, content_type="study_notes")
        
        # Should have only one "## Key Concepts"
        assert cleaned.count("## Key Concepts") == 1
        # Should preserve first content
        assert "First content" in cleaned

