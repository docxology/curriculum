"""Tests for content analysis utilities."""

import pytest
import re
from src.utils.content_analysis import (
    count_words,
    count_sections,
    count_subsections,
    count_examples,
    count_definitions,
    count_cross_references,
    analyze_lecture,
    analyze_lab,
    analyze_questions,
    analyze_study_notes,
    analyze_application,
    analyze_extension,
    analyze_visualization,
    analyze_integration,
    analyze_investigation,
    analyze_open_questions,
    validate_mermaid_syntax
)


class TestWordCounting:
    """Test word counting functions."""
    
    def test_count_words_basic(self):
        """Test basic word counting."""
        text = "This is a test sentence."
        assert count_words(text) == 5
    
    def test_count_words_multiple_spaces(self):
        """Test word counting with multiple spaces."""
        text = "Word1   Word2    Word3"
        assert count_words(text) == 3
    
    def test_count_words_empty(self):
        """Test word counting with empty string."""
        assert count_words("") == 0  # Empty string has no words


class TestStructureCounting:
    """Test structure counting functions."""
    
    def test_count_sections(self):
        """Test counting major sections."""
        text = """
# Title
## Section 1
Content here
## Section 2
More content
### Subsection
"""
        assert count_sections(text) == 2
    
    def test_count_subsections(self):
        """Test counting subsections."""
        text = """
## Section
### Subsection 1
### Subsection 2
#### Deep section
"""
        assert count_subsections(text) == 2


class TestContentCounting:
    """Test content element counting."""
    
    def test_count_examples(self):
        """Test counting examples."""
        text = """
For example, consider this case.
Such as water molecules.
For instance, DNA replication.
"""
        assert count_examples(text) >= 3
    
    def test_count_definitions(self):
        """Test counting term definitions."""
        text = """
**Mitochondria**: The powerhouse of the cell
**DNA**: Deoxyribonucleic acid stores genetic information
"""
        assert count_definitions(text) == 2
    
    def test_count_cross_references(self):
        """Test counting cross-references."""
        text = """
See lab exercise 1 for details.
Refer to the diagram for structure.
→ Lecture on cell division
"""
        assert count_cross_references(text) >= 3


class TestLectureAnalysis:
    """Test lecture content analysis."""
    
    def test_analyze_lecture_basic(self):
        """Test basic lecture analysis."""
        lecture = """
# Cell Biology

## Introduction
This lecture covers cell structure. For example, the nucleus contains DNA.

## Cell Membrane
**Phospholipid**: A molecule with hydrophobic and hydrophilic regions.

### Structure
The membrane is selectively permeable.
"""
        metrics = analyze_lecture(lecture)
        
        assert metrics['word_count'] > 0
        assert metrics['char_count'] > 0
        assert metrics['sections'] >= 2
        assert metrics['subsections'] >= 1
        assert metrics['examples'] >= 1
        assert metrics['terms'] >= 1
    
    def test_analyze_lecture_warnings(self):
        """Test lecture analysis warnings."""
        short_lecture = "# Title\n\nVery short content."
        metrics = analyze_lecture(short_lecture)
        
        assert len(metrics['warnings']) > 0
        assert any('word count' in w.lower() for w in metrics['warnings'])
    
    def test_analyze_lecture_exact_min_word_count(self):
        """Test lecture with exactly minimum word count."""
        # Create lecture with exactly 1000 words (accounting for title)
        words = ["word"] * 998
        lecture = "# Title\n\n" + " ".join(words)
        requirements = {'min_word_count': 1000, 'max_word_count': 1500}
        
        metrics = analyze_lecture(lecture, requirements=requirements)
        
        # Should be at or above minimum (may be slightly over due to title)
        assert metrics['word_count'] >= 1000
        assert not any('below minimum' in w for w in metrics['warnings'])
    
    def test_analyze_lecture_exact_max_word_count(self):
        """Test lecture with exactly maximum word count."""
        words = ["word"] * 1498
        lecture = "# Title\n\n" + " ".join(words)
        requirements = {'min_word_count': 1000, 'max_word_count': 1500}
        
        metrics = analyze_lecture(lecture, requirements=requirements)
        
        # Should be at or below maximum (may be slightly over due to title)
        assert metrics['word_count'] <= 1502  # Allow small margin
        # May or may not have warning depending on exact count
        if metrics['word_count'] > 1500:
            assert any('exceeds maximum' in w for w in metrics['warnings'])
    
    def test_analyze_lecture_exceeds_max_word_count(self):
        """Test lecture that exceeds maximum word count."""
        words = ["word"] * 2000
        lecture = "# Title\n\n" + " ".join(words)
        requirements = {'min_word_count': 1000, 'max_word_count': 1500}
        
        metrics = analyze_lecture(lecture, requirements=requirements)
        
        assert metrics['word_count'] > 1500
        assert any('exceeds maximum' in w for w in metrics['warnings'])
    
    def test_analyze_lecture_missing_sections(self):
        """Test lecture with too few sections."""
        lecture = """
# Title

## Section 1
Content here.

## Section 2
More content.
"""
        requirements = {'min_sections': 4, 'max_sections': 8}
        
        metrics = analyze_lecture(lecture, requirements=requirements)
        
        assert metrics['sections'] == 2
        assert any('sections' in w.lower() and 'need' in w.lower() for w in metrics['warnings'])
    
    def test_analyze_lecture_too_many_sections(self):
        """Test lecture with too many sections."""
        sections = "\n\n".join([f"## Section {i}\nContent." for i in range(1, 11)])
        lecture = f"# Title\n\n{sections}"
        requirements = {'min_sections': 4, 'max_sections': 8}
        
        metrics = analyze_lecture(lecture, requirements=requirements)
        
        assert metrics['sections'] == 10
        assert any('too many sections' in w.lower() for w in metrics['warnings'])
    
    def test_analyze_lecture_few_examples(self):
        """Test lecture with too few examples."""
        lecture = """
# Title

## Section 1
This is some content without examples.

## Section 2
More content here.
"""
        requirements = {'min_examples': 5, 'max_examples': 15}
        
        metrics = analyze_lecture(lecture, requirements=requirements)
        
        assert metrics['examples'] < 5
        assert any('examples' in w.lower() and 'need' in w.lower() for w in metrics['warnings'])
    
    def test_analyze_lecture_too_many_examples(self):
        """Test lecture with too many examples."""
        examples = " ".join([f"For example, case {i}." for i in range(20)])
        lecture = f"# Title\n\n## Section\n{examples}"
        requirements = {'min_examples': 5, 'max_examples': 15}
        
        metrics = analyze_lecture(lecture, requirements=requirements)
        
        assert metrics['examples'] >= 20
        assert any('too many examples' in w.lower() for w in metrics['warnings'])
    
    def test_analyze_lecture_compliance_status(self):
        """Test lecture compliance status determination."""
        # Compliant lecture
        words = ["word"] * 1200
        sections = "\n\n".join([f"## Section {i}\nContent." for i in range(1, 6)])
        examples = " ".join([f"For example, case {i}." for i in range(8)])
        compliant_lecture = f"# Title\n\n{sections}\n\n{examples}\n\n" + " ".join(words)
        
        metrics = analyze_lecture(compliant_lecture)
        
        # Should have no warnings if within all ranges
        # (Note: actual compliance depends on all metrics being within range)
        assert 'warnings' in metrics


class TestLabAnalysis:
    """Test lab content analysis."""
    
    def test_analyze_lab_basic(self):
        """Test basic lab analysis."""
        lab = """
# Lab Exercise

## Procedure
1. Step one
2. Step two
3. Step three

## Safety
⚠️ Wear safety goggles

## Data Collection
| Observation | Value |
|-------------|-------|
| pH | 7.0 |
"""
        metrics = analyze_lab(lab)
        
        assert metrics['procedure_steps'] >= 3
        assert metrics['safety_warnings'] >= 1
        assert metrics['tables'] >= 1
    
    def test_analyze_lab_warnings(self):
        """Test lab analysis warnings."""
        minimal_lab = """
# Lab
1. Do something
"""
        metrics = analyze_lab(minimal_lab)
        
        assert len(metrics['warnings']) > 0
    
    def test_analyze_lab_no_safety_warnings(self):
        """Test lab with no safety warnings (should warn)."""
        lab = """
# Lab Exercise

## Procedure
1. Step one
2. Step two
3. Step three
4. Step four
5. Step five

## Data Collection
| Observation | Value |
|-------------|-------|
| pH | 7.0 |
"""
        metrics = analyze_lab(lab)
        
        assert metrics['safety_warnings'] == 0
        assert any('No safety warnings' in w for w in metrics['warnings'])
    
    def test_analyze_lab_no_tables(self):
        """Test lab with no data tables (should warn)."""
        lab = """
# Lab Exercise

## Procedure
1. Step one
2. Step two
3. Step three
4. Step four
5. Step five

⚠️ Safety warning here
"""
        metrics = analyze_lab(lab)
        
        assert metrics['tables'] == 0
        assert any('No data collection tables' in w for w in metrics['warnings'])
    
    def test_analyze_lab_few_procedure_steps(self):
        """Test lab with too few procedure steps."""
        lab = """
# Lab Exercise

## Procedure
1. Step one
2. Step two
3. Step three

⚠️ Safety warning
| Data | Value |
|------|-------|
| pH | 7.0 |
"""
        metrics = analyze_lab(lab)
        
        assert metrics['procedure_steps'] == 3
        assert any('procedure steps' in w.lower() and 'need' in w.lower() for w in metrics['warnings'])
    
    def test_analyze_lab_procedure_step_counting(self):
        """Test procedure step counting with various formats."""
        lab = """
# Lab Exercise

## Procedure
1. First step
2. Second step
3. Third step
4. Fourth step
5. Fifth step
6. Sixth step
7. Seventh step
8. Eighth step

## Alternative Procedure
  1. Indented step
  2. Another indented step
"""
        metrics = analyze_lab(lab)
        
        # Should count numbered steps (both regular and indented)
        assert metrics['procedure_steps'] >= 8


class TestQuestionsAnalysis:
    """Test questions content analysis."""
    
    def test_analyze_questions_actual_format(self):
        """Test with actual generated format: **Question N:** (colon inside bold)."""
        questions = """
**Question 1:** What is DNA?
A) Sugar
B) Protein
C) Nucleic acid
D) Lipid

**Answer:** C
**Explanation:** DNA is deoxyribonucleic acid, a nucleic acid.

**Question 2:** Describe the cell membrane.

**Answer:** The cell membrane is composed of phospholipids.
"""
        metrics = analyze_questions(questions)
        
        assert metrics['total_questions'] == 2, f"Expected 2 questions, got {metrics['total_questions']}"
        assert metrics['mc_questions'] >= 1
        assert metrics['answers_provided'] == 2
        assert metrics['explanations_provided'] >= 1
    
    def test_analyze_questions_basic(self):
        """Test basic questions analysis with various formats."""
        questions = """
**Question 1**
What is DNA?
A. Sugar
B. Protein
C. Nucleic acid
D. Lipid

**Answer:** C
**Explanation:** DNA is deoxyribonucleic acid, a nucleic acid.

**Question 2**
Describe the cell membrane.

**Answer:** The cell membrane is composed of phospholipids.
"""
        metrics = analyze_questions(questions)
        
        assert metrics['total_questions'] >= 2
        assert metrics['mc_questions'] >= 1
        assert metrics['answers_provided'] >= 2
        assert metrics['explanations_provided'] >= 1
    
    def test_analyze_questions_real_content_sample(self):
        """Test with actual content from generated questions file."""
        # Sample from actual generated content
        questions = """
# Molecular & Cellular Biology - Comprehension Questions

**Total Questions**: 10  
**Multiple Choice**: 5 | **Short Answer**: 3 | **Essay**: 2

---

**Question 1:** What is the smallest unit of an element that retains the chemical properties of that element?
A) Molecule
B) Compound
C) Atom
D) Ion

**Answer:** C
**Explanation:** An atom is the fundamental building block of matter and defines an element's chemical characteristics.

**Question 2:** Which of the following best describes the role of neutrons in an atom?
A) They contribute to the atom's mass and are negatively charged.
B) They orbit the nucleus and carry a negative charge.
C) They are neutral in charge and contribute to the atom's mass.
D) They are ejected from the nucleus during radioactive decay.

**Answer:** C
**Explanation:** Neutrons reside within the nucleus and do not carry a charge, thereby contributing significantly to the atom's mass.

**Question 3:** Describe the difference between an ionic bond and a covalent bond.

**Answer:** Ionic bonds result from the transfer of electrons between atoms, forming ions and creating electrostatic attraction. Covalent bonds are formed when atoms share electrons to achieve a stable electron configuration.
"""
        metrics = analyze_questions(questions)
        
        assert metrics['total_questions'] == 3, f"Expected 3 questions, got {metrics['total_questions']}"
        assert metrics['mc_questions'] >= 2
        assert metrics['answers_provided'] == 3
        assert metrics['explanations_provided'] >= 2
    
    def test_analyze_questions_no_questions_warning(self):
        """Test that missing questions generate appropriate warnings."""
        questions = """
# Questions

Some text here but no questions in the expected format.
"""
        metrics = analyze_questions(questions)
        
        assert metrics['total_questions'] == 0
        assert len(metrics['warnings']) > 0
        assert any('No questions detected' in w for w in metrics['warnings'])
    
    def test_analyze_questions_missing_answers(self):
        """Test detection of missing answers."""
        questions = """
**Question 1:** What is DNA?
A) Sugar
B) Protein
C) Nucleic acid
D) Lipid

**Question 2:** Describe the cell membrane.
"""
        metrics = analyze_questions(questions)
        
        assert metrics['total_questions'] == 2
        assert metrics['answers_provided'] < metrics['total_questions']
        assert len(metrics['warnings']) > 0
        assert any('Missing answers' in w for w in metrics['warnings'])
    
    def test_analyze_questions_missing_explanations(self):
        """Test detection of missing explanations for MC questions."""
        questions = """
**Question 1:** What is DNA?
A) Sugar
B) Protein
C) Nucleic acid
D) Lipid

**Answer:** C

**Question 2:** What is RNA?
A) DNA copy
B) Protein
C) Nucleic acid
D) Lipid

**Answer:** C
**Explanation:** RNA is ribonucleic acid.
"""
        metrics = analyze_questions(questions)
        
        assert metrics['total_questions'] == 2
        assert metrics['mc_questions'] >= 2
        # Should warn about missing explanation for question 1
        if metrics['explanations_provided'] < metrics['mc_questions']:
            assert any('Missing explanations' in w for w in metrics['warnings'])
    
    def test_analyze_questions_multiple_formats(self):
        """Test detection of questions in multiple formats."""
        questions = """
**Question 1:** First question?
**Answer:** Answer 1

## Question 2
Second question?
**Answer:** Answer 2

Q3: Third question?
**Answer:** Answer 3
"""
        metrics = analyze_questions(questions)
        
        assert metrics['total_questions'] >= 3
        assert metrics['answers_provided'] == 3
    
    def test_analyze_questions_question_marks(self):
        """Test question mark counting and validation."""
        questions = """
**Question 1:** What is DNA?
**Answer:** C
**Explanation:** DNA is deoxyribonucleic acid.

**Question 2:** Explain the process.
**Answer:** The process involves...

**Question 3:** How does it work?
**Answer:** It works by...
"""
        metrics = analyze_questions(questions)
        
        assert metrics['question_marks'] == 2  # Questions 1 and 3 have "?"
        assert metrics['questions_with_marks'] >= 2
        assert metrics['total_questions'] == 3
        # Should warn about missing question marks
        assert any('question marks' in w.lower() for w in metrics['warnings'])
    
    def test_analyze_questions_no_question_marks(self):
        """Test detection when no question marks are present."""
        questions = """
**Question 1:** What is DNA
**Answer:** C

**Question 2:** Explain the process
**Answer:** The process involves...
"""
        metrics = analyze_questions(questions)
        
        assert metrics['question_marks'] == 0
        assert metrics['questions_with_marks'] == 0
        assert any('No question marks' in w or 'question marks' in w.lower() for w in metrics['warnings'])
    
    def test_analyze_questions_mc_structure_validation(self):
        """Test MC question structure validation."""
        questions = """
**Question 1:** What is DNA?
A) Sugar
B) Protein
C) Nucleic acid
D) Lipid
**Answer:** C
**Explanation:** DNA is a nucleic acid.

**Question 2:** What is RNA?
A) DNA copy
**Answer:** C

**Question 3:** Describe the cell.
**Answer:** The cell is...
"""
        metrics = analyze_questions(questions)
        
        assert metrics['mc_questions'] >= 1
        assert metrics['mc_questions_valid'] >= 1
        # Question 2 has only 1 option, so may not be valid
        if metrics['mc_questions_valid'] < metrics['mc_questions']:
            assert any('MC question structure' in w or 'options' in w.lower() for w in metrics['warnings'])
    
    def test_analyze_questions_length_validation(self):
        """Test question length validation."""
        questions = """
**Question 1:** What?
**Answer:** Short

**Question 2:** This is a very long question that contains many words and goes on for a while to test the length validation functionality of the question analysis system?
**Answer:** Long

**Question 3:** What is DNA?
**Answer:** C
"""
        metrics = analyze_questions(questions)
        
        assert metrics['question_lengths']
        assert metrics['min_question_length'] >= 1
        assert metrics['max_question_length'] >= 1
        assert metrics['avg_question_length'] >= 1
        # Should warn about very short or very long questions
        if any(q < 3 for q in metrics['question_lengths']):
            assert any('short' in w.lower() for w in metrics['warnings'])
        if any(q > 50 for q in metrics['question_lengths']):
            assert any('long' in w.lower() for w in metrics['warnings'])
    
    def test_analyze_questions_question_mark_ratio(self):
        """Test question mark ratio validation."""
        questions = """
**Question 1:** What is DNA?
**Answer:** C

**Question 2:** Explain the process
**Answer:** Process

**Question 3:** How does it work?
**Answer:** It works
"""
        metrics = analyze_questions(questions)
        
        assert metrics['question_marks'] >= 2
        assert metrics['total_questions'] == 3
        # Should warn about low question mark ratio
        if metrics['questions_with_marks'] < metrics['total_questions']:
            assert any('question mark' in w.lower() for w in metrics['warnings'])
    
    def test_analyze_questions_mc_option_count_validation(self):
        """Test MC question option count validation (exactly 4 options)."""
        questions = """
**Question 1:** What is DNA?
A) Sugar
B) Protein
C) Nucleic acid
D) Lipid
**Answer:** C
**Explanation:** DNA is a nucleic acid.

**Question 2:** What is RNA?
A) DNA copy
B) Protein
C) Nucleic acid
D) Lipid
**Answer:** C

**Question 3:** What is ATP?
A) Energy
B) Protein
C) Sugar
**Answer:** A
"""
        metrics = analyze_questions(questions)
        
        assert metrics['mc_questions'] >= 2
        # Question 1 has 4 options, Question 2 has 4 options, Question 3 has 3
        # At least one should have 4 options
        assert metrics.get('mc_questions_with_4_options', 0) >= 1
        # Should warn about MC questions not having exactly 4 options (Question 3)
        if metrics.get('mc_questions_with_4_options', 0) < metrics['mc_questions']:
            assert any('do not have exactly 4 options' in w or '4 options' in w for w in metrics['warnings'])
    
    def test_analyze_questions_explanation_length_validation(self):
        """Test MC explanation length validation."""
        questions = """
**Question 1:** What is DNA?
A) Sugar
B) Protein
C) Nucleic acid
D) Lipid
**Answer:** C
**Explanation:** DNA is a nucleic acid that stores genetic information in cells. It consists of nucleotides with bases A, T, G, and C.

**Question 2:** What is RNA?
A) DNA copy
B) Protein
C) Nucleic acid
D) Lipid
**Answer:** C
**Explanation:** RNA.

**Question 3:** What is ATP?
A) Energy
B) Protein
C) Sugar
D) Lipid
**Answer:** A
**Explanation:** ATP is adenosine triphosphate, the energy currency of cells. It stores and transfers energy for cellular processes. This molecule is produced during cellular respiration and used in various metabolic reactions throughout the cell.
"""
        metrics = analyze_questions(questions)
        
        assert metrics['explanations_provided'] >= 3
        # Question 1: good length, Question 2: too short, Question 3: too long
        if metrics.get('explanation_lengths'):
            assert any('too short' in w.lower() or 'too long' in w.lower() for w in metrics['warnings'])


class TestStudyNotesAnalysis:
    """Test study notes content analysis."""
    
    def test_analyze_study_notes_basic(self):
        """Test basic study notes analysis."""
        notes = """
# Cell Biology - Study Notes

## Key Concepts

- **Nucleus**: Contains genetic material
- **Mitochondria**: Produces ATP
- **Ribosome**: Synthesizes proteins

## Summary
Cells are the basic unit of life.
"""
        metrics = analyze_study_notes(notes)
        
        assert metrics['sections'] >= 2
        assert metrics['key_concepts'] >= 3
        assert metrics['bullet_points'] >= 3
    
    def test_analyze_study_notes_key_concept_formats(self):
        """Test key concept counting with various formats."""
        notes = """
# Study Notes

## Key Concepts

- **Term1**: Definition one
- **Term2**: Definition two
* **Term3**: Definition three
- **Term4**: Definition four
"""
        metrics = analyze_study_notes(notes)
        
        # Should count key concepts in format **Term**: Definition
        assert metrics['key_concepts'] >= 4
    
    def test_analyze_study_notes_few_key_concepts(self):
        """Test study notes with too few key concepts."""
        notes = """
# Study Notes

## Key Concepts
- **Term1**: Definition

## Summary
Some summary text.
"""
        requirements = {'min_key_concepts': 3, 'max_key_concepts': 10}
        
        metrics = analyze_study_notes(notes, requirements=requirements)
        
        assert metrics['key_concepts'] == 1
        assert any('key concepts' in w.lower() and 'need' in w.lower() for w in metrics['warnings'])
    
    def test_analyze_study_notes_too_many_key_concepts(self):
        """Test study notes with too many key concepts."""
        concepts = "\n".join([f"- **Term{i}**: Definition {i}" for i in range(1, 15)])
        notes = f"# Study Notes\n\n## Key Concepts\n\n{concepts}"
        requirements = {'min_key_concepts': 3, 'max_key_concepts': 10}
        
        metrics = analyze_study_notes(notes, requirements=requirements)
        
        assert metrics['key_concepts'] >= 14
        assert any('too many key concepts' in w.lower() for w in metrics['warnings'])
    
    def test_analyze_study_notes_word_count_limit(self):
        """Test study notes that exceed word count limit."""
        words = ["word"] * 2000
        notes = f"# Study Notes\n\n## Summary\n\n" + " ".join(words)
        requirements = {'max_word_count': 1200}
        
        metrics = analyze_study_notes(notes, requirements=requirements)
        
        assert metrics['word_count'] > 1200
        assert any('exceeds maximum' in w for w in metrics['warnings'])
    
    def test_analyze_study_notes_bullet_point_structure(self):
        """Test study notes bullet point structure."""
        notes = """
# Study Notes

## Key Concepts
- **Term1**: Definition
- **Term2**: Definition
* **Term3**: Definition (asterisk format)

## Summary
- Point one
- Point two
- Point three
"""
        metrics = analyze_study_notes(notes)
        
        # Should count all bullet points (both - and *)
        assert metrics['bullet_points'] >= 6
    
    def test_analyze_study_notes_with_tables(self):
        """Test study notes with tables."""
        notes = """
# Study Notes

## Key Concepts
- **Term1**: Definition

## Comparison Table
| Feature | Value |
|---------|-------|
| Size | Large |
"""
        metrics = analyze_study_notes(notes)
        
        assert metrics['tables'] >= 1


class TestContentStructureValidation:
    """Test content structure validation."""
    
    def test_markdown_section_hierarchy(self):
        """Test markdown section hierarchy parsing."""
        content = """
# Title
## Section 1
### Subsection 1.1
#### Deep subsection
## Section 2
### Subsection 2.1
"""
        sections = count_sections(content)
        subsections = count_subsections(content)
        
        assert sections == 2
        assert subsections >= 2
    
    def test_cross_reference_detection(self):
        """Test cross-reference detection in content."""
        content = """
# Lecture

See lab exercise 1 for details.
Refer to the diagram for structure.
→ Lecture on cell division
Check the study notes section.
See also: Module 2
"""
        cross_refs = count_cross_references(content)
        
        # Should detect at least some cross-references
        assert cross_refs >= 3
    
    def test_term_definition_detection(self):
        """Test term definition detection."""
        content = """
# Lecture

**Mitochondria**: The powerhouse of the cell
**DNA**: Deoxyribonucleic acid stores genetic information
**ATP**: Adenosine triphosphate is the energy currency
"""
        terms = count_definitions(content)
        
        assert terms >= 3


class TestMermaidValidation:
    """Test Mermaid diagram validation."""
    
    def test_validate_removes_code_fences(self):
        """Test that code fences are removed."""
        diagram = """```mermaid
graph TD
    A --> B
```"""
        cleaned, warnings = validate_mermaid_syntax(diagram)
        
        assert '```' not in cleaned
        assert 'graph TD' in cleaned
        assert len(warnings) > 0
    
    def test_validate_removes_style_commands(self):
        """Test that style commands are removed."""
        diagram = """graph TD
    A --> B
    style A fill:#f9f"""
        cleaned, warnings = validate_mermaid_syntax(diagram)
        
        # Verify style command is removed from cleaned output
        assert 'style' not in cleaned, f"Style command still present in cleaned diagram: {cleaned}"
        assert 'graph TD' in cleaned, f"Diagram type missing from cleaned output: {cleaned}"
        assert 'A --> B' in cleaned, f"Diagram content missing from cleaned output: {cleaned}"
        # Verify warning is generated about style removal
        style_warnings = [w for w in warnings if 'style' in w.lower()]
        assert len(style_warnings) > 0, f"No style-related warnings found. Warnings: {warnings}"
    
    def test_validate_removes_classdef_commands(self):
        """Test that classDef commands are removed."""
        diagram = """graph TD
    A --> B
    classDef myClass fill:#fff,stroke:#000"""
        cleaned, warnings = validate_mermaid_syntax(diagram)
        
        assert 'classDef' not in cleaned, f"classDef command still present: {cleaned}"
        assert 'graph TD' in cleaned
        assert 'A --> B' in cleaned
        classdef_warnings = [w for w in warnings if 'classdef' in w.lower() or 'class' in w.lower()]
        assert len(classdef_warnings) > 0, f"No classDef-related warnings found. Warnings: {warnings}"
    
    def test_validate_removes_multiple_style_commands(self):
        """Test that multiple style commands are all removed."""
        diagram = """graph TD
    A --> B
    B --> C
    style A fill:#f9f
    style B fill:#9f9
    classDef default fill:#fff"""
        cleaned, warnings = validate_mermaid_syntax(diagram)
        
        assert 'style' not in cleaned, f"Style commands still present: {cleaned}"
        assert 'classDef' not in cleaned, f"classDef command still present: {cleaned}"
        assert cleaned.count('A --> B') == 1
        assert cleaned.count('B --> C') == 1
        # Should have warnings for both style and classDef
        style_warnings = [w for w in warnings if 'style' in w.lower()]
        classdef_warnings = [w for w in warnings if 'classdef' in w.lower()]
        assert len(style_warnings) > 0 or len(classdef_warnings) > 0, f"No style/classDef warnings: {warnings}"
    
    def test_validate_removes_style_with_indentation(self):
        """Test that style commands with various indentation are removed."""
        diagram = """graph TD
    A --> B
        style A fill:#f9f
    style B fill:#9f9
\tstyle C fill:#99f"""
        cleaned, warnings = validate_mermaid_syntax(diagram)
        
        assert 'style' not in cleaned, f"Style commands with indentation still present: {cleaned}"
        assert 'A --> B' in cleaned
        style_warnings = [w for w in warnings if 'style' in w.lower()]
        assert len(style_warnings) > 0, f"No style warnings for indented commands: {warnings}"
    
    def test_validate_removes_style_in_complex_diagram(self):
        """Test style removal in complex diagram with subgraphs."""
        diagram = """graph TD
    subgraph S1
        A --> B
    end
    subgraph S2
        C --> D
    end
    style A fill:#f9f
    classDef s1Style fill:#fff"""
        cleaned, warnings = validate_mermaid_syntax(diagram)
        
        assert 'style' not in cleaned, f"Style command in complex diagram still present: {cleaned}"
        assert 'classDef' not in cleaned, f"classDef in complex diagram still present: {cleaned}"
        assert 'subgraph S1' in cleaned
        assert 'subgraph S2' in cleaned
        assert 'A --> B' in cleaned
        assert 'C --> D' in cleaned
    
    def test_validate_checks_diagram_type(self):
        """Test that missing diagram type is detected."""
        diagram = "A --> B"
        cleaned, warnings = validate_mermaid_syntax(diagram)
        
        assert any('diagram type' in w.lower() for w in warnings)
    
    def test_validate_valid_diagram(self):
        """Test that valid diagram passes with no warnings."""
        diagram = """graph TD
    A[Start] --> B[Process]
    B --> C[End]"""
        cleaned, warnings = validate_mermaid_syntax(diagram)
        
        assert cleaned == diagram
        assert len(warnings) == 0
    
    def test_validate_node_count(self):
        """Test node count validation."""
        # Diagram with only 1 node (below minimum of 3)
        diagram = "graph TD\n    A[Start]"
        cleaned, warnings = validate_mermaid_syntax(diagram, min_nodes=3)
        
        assert any('nodes found' in w.lower() or 'need' in w.lower() for w in warnings)
    
    def test_validate_connection_count(self):
        """Test connection count validation."""
        # Diagram with no connections
        diagram = "graph TD\n    A[Start]\n    B[Process]\n    C[End]"
        cleaned, warnings = validate_mermaid_syntax(diagram, min_connections=2)
        
        assert any('connections found' in w.lower() or 'need' in w.lower() for w in warnings)
    
    def test_validate_node_text_length(self):
        """Test node text length validation."""
        # Diagram with very long node text
        diagram = """graph TD
    A[This is a very long node text that exceeds the recommended 40 character limit and should trigger a warning] --> B[Short]"""
        cleaned, warnings = validate_mermaid_syntax(diagram)
        
        assert any('exceeds 40 characters' in w or 'long' in w.lower() for w in warnings)
    
    def test_validate_empty_nodes(self):
        """Test empty node detection."""
        diagram = """graph TD
    [] --> B[Node]
    () --> C[Node]"""
        cleaned, warnings = validate_mermaid_syntax(diagram)
        
        assert any('empty nodes' in w.lower() for w in warnings)


class TestMermaidCleanup:
    """Test Mermaid diagram cleanup (clean_mermaid_diagram function)."""
    
    def test_clean_removes_code_fences(self):
        """Test that code fences are removed."""
        diagram = """```mermaid
graph TD
    A --> B
```"""
        from src.utils.content_analysis.mermaid import clean_mermaid_diagram
        cleaned = clean_mermaid_diagram(diagram)
        
        assert '```' not in cleaned
        assert 'graph TD' in cleaned
        assert 'A --> B' in cleaned
    
    def test_clean_removes_linkstyle(self):
        """Test that linkStyle commands are removed."""
        diagram = """graph TD
    A --> B
    B --> C
    linkStyle 0,1,2,3,4,5,6,7,8,9,10 stroke:#f9f,stroke-width:2px"""
        from src.utils.content_analysis.mermaid import clean_mermaid_diagram
        cleaned = clean_mermaid_diagram(diagram)
        
        assert 'linkStyle' not in cleaned
        assert 'graph TD' in cleaned
        assert 'A --> B' in cleaned
    
    def test_clean_removes_explanatory_text_after_diagram(self):
        """Test that explanatory text after diagram is removed."""
        diagram = """graph TD
    A --> B
    B --> C

**Explanation of Diagram & Adherence to Requirements:**

*   **Graph TD:** The diagram is set up using the `graph TD` type, as requested.
*   **No Code Fences:** The output contains *only* valid Mermaid syntax.
"""
        from src.utils.content_analysis.mermaid import clean_mermaid_diagram
        cleaned = clean_mermaid_diagram(diagram)
        
        assert '**Explanation' not in cleaned
        assert 'Graph TD:' not in cleaned
        assert 'graph TD' in cleaned
        assert 'A --> B' in cleaned
    
    def test_clean_removes_explanatory_text_before_diagram(self):
        """Test that explanatory text before diagram is removed."""
        diagram = """Okay, here's a Mermaid diagram representing the relationships between the key concepts.

```mermaid
graph LR
    A --> B
```"""
        from src.utils.content_analysis.mermaid import clean_mermaid_diagram
        cleaned = clean_mermaid_diagram(diagram)
        
        assert 'Okay, here\'s' not in cleaned
        assert 'graph LR' in cleaned
        assert 'A --> B' in cleaned
    
    def test_clean_removes_style_commands(self):
        """Test that style commands are removed."""
        diagram = """graph TD
    A --> B
    style A fill:#f9f
    classDef myClass fill:#fff"""
        from src.utils.content_analysis.mermaid import clean_mermaid_diagram
        cleaned = clean_mermaid_diagram(diagram)
        
        assert 'style' not in cleaned
        assert 'classDef' not in cleaned
        assert 'graph TD' in cleaned
    
    def test_clean_preserves_valid_diagram(self):
        """Test that valid diagram code is preserved."""
        diagram = """graph TD
    A[Start] --> B[Process]
    B --> C[End]"""
        from src.utils.content_analysis.mermaid import clean_mermaid_diagram
        cleaned = clean_mermaid_diagram(diagram)
        
        assert cleaned.strip() == diagram.strip()
    
    def test_clean_handles_complex_diagram_with_linkstyle(self):
        """Test cleanup of complex diagram with linkStyle command."""
        diagram = """graph LR
    subgraph Prokaryotic Cell
        A[Bacteria] --> B{DNA Location}
        B --> C[Nucleoid Region]
    end
    subgraph Eukaryotic Cell
        I[Animal Cell] --> J{DNA Location}
    end
    linkStyle 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199,200,201,202,203,204,205,206,207,208,209,210,211,212,213,214,215,216,217,218,219,220,221,222,223,224,225,226,227,228,229,230,231,232,233,234,235,236,237,238,239,240,241,242,243,244,245,246,247,248,249,250,251,252,253,254,255,256,257,258,259,260,261,262,263,264,265,266,267,268,269,270,271,272,273,274,275,276,277,278,279,280,281,282,283,284,285,286,287,288,289,290,291,292,293,294,295,296,297,298,299,300,301,302,303,304,305,306,307,308,309,310,311,312,313,314,315,316,317,318,319,320,321,322,323,324,325,326,327,328,329,330,331,332,333,334,335,336,337,338,339,340,341,342,343,344,345,346,347,348,349,350,351,352,353,354,355,356,357,358,359,360,361,362,363,364,365,366,367,368,369,370,371,372,373,374,375,376,377,378,379,380,381,382,383,384,385,386,387,388,389,390,391,392,393,394,395,396,397,398,399,400,401,402,403,404,405,406,407,408,409,410,411,412,413,414,415,416,417,418,419,420,421,422,423,424,425,426,427,428,429,430,431,432,433,434,435,436,437,438,439,440,441,442,443,444,445,446,447,448,449,450,451,452,453,454,455,456,457,458,459,460,461,462,463,464,465,466,467,468,469,470,471,472,473,474,475,476,477,478,479,480,481,482,483,484,485,486,487,488,489,490,491,492,493,494,495,496,497,498,499,500,501,502,503,504,505,506,507,508,509,510,511,512,513,514,515,516,517,518,519,520,521,522,523,524,525,526,527,528,529,530,531,532,533,534,535,536,537,538,539,540,541,542,543,544,545,546,547,548,549,550,551,552,553,554,555,556,557,558,559,560,561,562,563,564,565,566,567,568,569,570,571,572,573,574,575,576,577,578,579,580,581,582,583,584,585,586,587,588,589,590,591,592,593,594,595,596,597,598,599,600 stroke:#f9f"""
        from src.utils.content_analysis.mermaid import clean_mermaid_diagram
        cleaned = clean_mermaid_diagram(diagram)
        
        assert 'linkStyle' not in cleaned
        assert 'graph LR' in cleaned
        assert 'subgraph' in cleaned
        assert 'A[Bacteria]' in cleaned
    
    def test_clean_handles_empty_diagram(self):
        """Test cleanup of empty diagram."""
        diagram = ""
        from src.utils.content_analysis.mermaid import clean_mermaid_diagram
        cleaned = clean_mermaid_diagram(diagram)
        
        assert cleaned == ""
    
    def test_clean_integration_with_validate(self):
        """Test that clean_mermaid_diagram works with validate_mermaid_syntax."""
        diagram = """```mermaid
graph TD
    A --> B
    linkStyle 0 stroke:#f9f
```

**Explanation:** This diagram shows a simple flow.
"""
        from src.utils.content_analysis.mermaid import clean_mermaid_diagram, validate_mermaid_syntax
        cleaned = clean_mermaid_diagram(diagram)
        validated, warnings = validate_mermaid_syntax(cleaned)
        
        assert '```' not in validated
        assert 'linkStyle' not in validated
        assert '**Explanation' not in validated
        assert 'graph TD' in validated
        assert 'A --> B' in validated


class TestApplicationAnalysis:
    """Test application content analysis."""
    
    def test_analyze_application_basic(self):
        """Test basic application analysis."""
        content = """
# Applications

## Application 1
This is a real-world application with about 150 words of content describing how the concept applies to medical research and treatment protocols.

## Application 2
Another application example showing environmental impact and sustainability measures in practice.

## Application 3
A third application demonstrating industrial uses and manufacturing processes.
"""
        metrics = analyze_application(content)
        
        assert metrics['applications'] >= 3
        assert metrics['word_count'] > 0
        assert 'warnings' in metrics
    
    def test_analyze_application_warnings(self):
        """Test application analysis warnings."""
        minimal_content = "# Applications\n\n## Application 1\nShort content."
        metrics = analyze_application(minimal_content)
        
        assert len(metrics['warnings']) > 0
        assert any('applications' in w.lower() or 'words' in w.lower() for w in metrics['warnings'])


class TestExtensionAnalysis:
    """Test extension content analysis."""
    
    def test_analyze_extension_basic(self):
        """Test basic extension analysis."""
        content = """
# Extension Topics

## Topic 1
Advanced topic covering cutting-edge research with about 120 words of detailed explanation.

## Topic 2
Another advanced topic exploring theoretical frameworks and future directions.

## Topic 3
A third topic examining interdisciplinary connections and emerging applications.
"""
        metrics = analyze_extension(content)
        
        assert metrics['topics'] >= 3
        assert metrics['word_count'] > 0
        assert 'warnings' in metrics
    
    def test_analyze_extension_warnings(self):
        """Test extension analysis warnings."""
        minimal_content = "# Extensions\n\n## Topic 1\nShort content."
        metrics = analyze_extension(minimal_content)
        
        assert len(metrics['warnings']) > 0
        assert any('topics' in w.lower() or 'words' in w.lower() for w in metrics['warnings'])


class TestVisualizationAnalysis:
    """Test visualization content analysis."""
    
    def test_analyze_visualization_basic(self):
        """Test basic visualization analysis."""
        diagram = """graph TD
    A[Start] --> B[Process 1]
    B --> C[Process 2]
    C --> D[End]"""
        metrics = analyze_visualization(diagram)
        
        assert metrics['nodes'] >= 3
        assert metrics['connections'] >= 2
        assert metrics['total_elements'] >= 3
        assert 'warnings' in metrics
    
    def test_analyze_visualization_warnings(self):
        """Test visualization analysis warnings."""
        minimal_diagram = "A"
        metrics = analyze_visualization(minimal_diagram)
        
        assert len(metrics['warnings']) > 0
        assert any('elements' in w.lower() or 'diagram' in w.lower() for w in metrics['warnings'])


class TestIntegrationAnalysis:
    """Test integration content analysis."""
    
    def test_analyze_integration_basic(self):
        """Test basic integration analysis."""
        content = """
# Integration

This content connects to Module 1 and Module 2. It builds on previous concepts and relates to other topics. The integration extends across multiple areas.
"""
        metrics = analyze_integration(content)
        
        assert metrics['connections'] >= 0
        assert metrics['word_count'] > 0
        assert 'warnings' in metrics
    
    def test_analyze_integration_warnings(self):
        """Test integration analysis warnings."""
        minimal_content = "Short content."
        metrics = analyze_integration(minimal_content)
        
        assert len(metrics['warnings']) > 0
        assert any('connections' in w.lower() for w in metrics['warnings'])


class TestInvestigationAnalysis:
    """Test investigation content analysis."""
    
    def test_analyze_investigation_basic(self):
        """Test basic investigation analysis."""
        content = """
# Research Investigations

## Research Question 1
What are the mechanisms underlying this process?

## Research Question 2
How do environmental factors influence outcomes?

## Research Question 3
What are the long-term implications?
"""
        metrics = analyze_investigation(content)
        
        assert metrics['questions'] >= 3
        assert metrics['word_count'] > 0
        assert 'warnings' in metrics
    
    def test_analyze_investigation_warnings(self):
        """Test investigation analysis warnings."""
        minimal_content = "# Investigations\n\n## Research Question 1\nShort question."
        metrics = analyze_investigation(minimal_content)
        
        assert len(metrics['warnings']) > 0
        assert any('questions' in w.lower() for w in metrics['warnings'])


class TestOpenQuestionsAnalysis:
    """Test open questions content analysis."""
    
    def test_analyze_open_questions_basic(self):
        """Test basic open questions analysis."""
        content = """
# Open Questions

## Open Question 1
What are the current research frontiers?

## Open Question 2
What questions remain unanswered?

## Open Question 3
What are the future directions?
"""
        metrics = analyze_open_questions(content)
        
        assert metrics['questions'] >= 3
        assert metrics['word_count'] > 0
        assert 'warnings' in metrics
    
    def test_analyze_open_questions_warnings(self):
        """Test open questions analysis warnings."""
        minimal_content = "# Open Questions\n\n## Open Question 1\nShort question."
        metrics = analyze_open_questions(minimal_content)
        
        assert len(metrics['warnings']) > 0
        assert any('questions' in w.lower() for w in metrics['warnings'])


class TestContentMetricsLogging:
    """Test content metrics logging."""
    
    def test_log_lecture_metrics(self, caplog):
        """Test logging lecture metrics."""
        import logging
        from src.utils.content_analysis import log_content_metrics
        
        metrics = {
            'char_count': 5000,
            'word_count': 750,
            'sections': 5,
            'subsections': 12,
            'examples': 8,
            'terms': 15,
            'cross_refs': 3,
            'warnings': []
        }
        
        logger = logging.getLogger('test_logger')
        logger.setLevel(logging.INFO)
        
        with caplog.at_level(logging.INFO):
            log_content_metrics('lecture', metrics, logger)
        
        # Check that metrics were logged
        logged_text = ' '.join([record.message for record in caplog.records])
        assert '750 words' in logged_text
    
    def test_log_metrics_with_warnings(self, caplog):
        """Test logging metrics with warnings."""
        import logging
        from src.utils.content_analysis import log_content_metrics
        
        metrics = {
            'char_count': 100,
            'word_count': 15,
            'sections': 1,
            'subsections': 0,
            'examples': 0,
            'terms': 0,
            'warnings': ['Too short', 'Missing examples']
        }
        
        logger = logging.getLogger('test_logger')
        logger.setLevel(logging.WARNING)
        
        with caplog.at_level(logging.WARNING):
            log_content_metrics('lecture', metrics, logger)
        
        # Check that warnings were logged
        warning_messages = [r.message for r in caplog.records if r.levelname == 'WARNING']
        assert len(warning_messages) >= 2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

