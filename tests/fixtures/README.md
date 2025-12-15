# Test Fixtures

This directory contains sample data files for testing the educational course Generator.

## Files

### Configuration Files
- **`sample_course_config.yaml`** - Sample course configuration for testing config loader
- **`sample_module_info.json`** - Sample module information structure

### Outline Files
- **`sample_outline.json`** - Sample JSON course outline with 2 modules and 6 sessions
- **`sample_markdown_outline.md`** - Sample markdown outline for parser testing

### Content Samples
- **`sample_lecture.md`** - Example generated lecture content
- **`sample_lab.md`** - Example generated lab exercise
- **`sample_study_notes.md`** - Example generated study notes
- **`sample_questions.md`** - Example generated questions with answers
- **`sample_diagram.mmd`** - Example Mermaid diagram

## Usage

These fixtures are used across multiple test files:

- `test_config_loader.py` - Uses configuration files
- `test_parser.py` - Uses markdown outline
- `test_outline_generator.py` - Uses JSON outline structure
- `test_content_generators.py` - Uses module info and sample content
- `test_pipeline.py` - Uses complete outline structures

## Creating New Fixtures

When adding new test scenarios, create fixture files that:

1. Are realistic but minimal
2. Cover edge cases (unicode, special characters, etc.)
3. Include comments explaining unusual scenarios
4. Follow the project's data structure conventions
5. Are git-friendly (text-based, readable diffs)

## Maintenance

- Update fixtures when data structures change
- Keep fixtures in sync with actual config/llm_config.yaml structure
- Document any deviations from production formats









