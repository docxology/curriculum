# Agentic Generation Workflows

## Soft Constraint

**SHOULD support hybrid AI/human workflows for content generation and review.**

## Workflow Modes

The system supports three workflow modes:

1. **Programmatic** (Full automation): `uv run python3 scripts/run_pipeline.py`
2. **Agentic** (AI + human review): Generate → Review → Edit → Commit
3. **Manual** (Human-controlled): Edit YAML and markdown files directly

## Agentic Workflow Pattern

### Generate → Review → Edit → Commit

```python
# ✅ CORRECT: Generate with review points
# Step 1: Generate outline
outline_path = generate_outline()

# Step 2: Human review (manual step)
# Review outline_path, edit if needed

# Step 3: Generate primary materials
primary_results = generate_primary_materials(outline_path)

# Step 4: Human review (manual step)
# Review generated content, edit if needed

# Step 5: Generate secondary materials
secondary_results = generate_secondary_materials(outline_path)

# Step 6: Final review and commit
# Review all content, commit to version control
```

## Interactive vs Non-Interactive

**SOFT**: Support both interactive and non-interactive modes:

```python
# ✅ CORRECT: Support both modes
def generate_outline(interactive: bool = True):
    if interactive:
        # Show menu, allow selection
        course_template = select_course_template()
    else:
        # Use defaults or command-line args
        course_template = get_default_template()
    
    return generate_outline_for_template(course_template)
```

## Review Points

**SOFT**: Provide natural review points in workflow:

1. **After outline generation**: Review course structure
2. **After primary materials**: Review core content
3. **After secondary materials**: Review supplementary content
4. **Before website generation**: Final review of all content

## Human-in-the-Loop

**SOFT**: Support human editing between stages:

```python
# ✅ CORRECT: Allow manual edits between stages
# Stage 1: Generate outline
outline = generate_outline()
save_outline(outline)

# Human edits outline file manually

# Stage 2: Load edited outline
outline = load_outline()  # Loads edited version
generate_content(outline)
```

## Validation and Review

**SOFT**: Provide validation status for review:

```python
# ✅ CORRECT: Show validation status for review
metrics = analyze_content(content)
if metrics['status'] == 'NEEDS REVIEW':
    logger.warning(f"Content needs review: {metrics['warnings']}")
    # Human reviews and decides: accept, regenerate, or edit
```

## See Also

- **[../docs/PIPELINE_GUIDE.md](../docs/PIPELINE_GUIDE.md)** - Pipeline workflows
- **[../docs/EXTENSION.md](../docs/EXTENSION.md)** - Custom workflow patterns
- **[09-safe-to-fail.md](09-safe-to-fail.md)** - Error handling in workflows
