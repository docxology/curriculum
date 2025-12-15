# Content Generation Patterns

## Soft Constraint

**SHOULD follow established patterns for content generation.**

## Generation Workflow

### Standard Pattern

```python
# ✅ CORRECT: Standard generation pattern
from src.generate.formats.lectures import LectureGenerator

generator = LectureGenerator(config_loader, llm_client)

# Generate content
lecture = generator.generate_lecture(
    module_info=module,
    session_number=1,
    total_sessions=3,
    session_title="Cell Structure"
)

# Save content (session-based structure)
session_dir = Path("output/modules/module_01_cell_biology/session_01")
session_dir.mkdir(parents=True, exist_ok=True)
output_path = generator.save_lecture(
    lecture=lecture,
    module_info=module,
    output_dir=session_dir,
    session_number=1
)
```

## Context Preservation

**SOFT**: Pass context between generators:

```python
# ✅ CORRECT: Pass lecture content to questions generator
lecture = lecture_gen.generate_lecture(module, session_num)
questions = question_gen.generate_questions(
    module,
    lecture_summary=lecture[:500]  # Pass context
)
```

## Content Cleanup

**SOFT**: Apply cleanup automatically:

```python
# ✅ CORRECT: Clean content after generation
from src.generate.processors.cleanup import clean_content

raw_content = llm_client.generate(prompt)
cleaned_content = clean_content(raw_content)
# Removes conversational artifacts, standardizes placeholders
```

## Validation

**SOFT**: Validate generated content:

```python
# ✅ CORRECT: Validate after generation
from src.utils.content_analysis import analyze_lecture, log_content_metrics

metrics = analyze_lecture(lecture, requirements=requirements)
log_content_metrics("lecture", metrics, logger)
# Logs [COMPLIANT] or [NEEDS REVIEW] status
```

## Error Handling

**SOFT**: Handle generation errors gracefully:

```python
# ✅ CORRECT: Collect errors, continue processing
errors = []
for module in modules:
    try:
        generate_content(module)
    except ContentGenerationError as e:
        errors.append({"module": module['id'], "error": str(e)})
        logger.error(f"Failed module {module['id']}: {e}")

if errors:
    logger.warning(f"Completed with {len(errors)} errors")
```

## Session-Based Generation

**SOFT**: Generate content per session (not per module):

```python
# ✅ CORRECT: Session-based generation
for module in modules:
    for session in module['sessions']:
        generate_session_content(
            module_id=module['module_id'],
            session_number=session['session_number'],
            session_title=session['session_title']
        )
```

## See Also

- **[../docs/FORMATS.md](../docs/FORMATS.md)** - Content format specifications
- **[../docs/PIPELINE_GUIDE.md](../docs/PIPELINE_GUIDE.md)** - Pipeline workflows
- **[09-safe-to-fail.md](09-safe-to-fail.md)** - Error handling patterns
