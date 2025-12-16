# Pipeline Orchestration Module

Complete workflow coordination for educational course generation.

## Module Purpose

Provides `ContentGenerator` class that orchestrates the full generation pipeline: outline generation, parsing, and all content format generation (lectures, labs, diagrams, questions, study notes, secondary materials).

## Key Class: ContentGenerator

```python
from src.config.loader import ConfigLoader
from src.generate.orchestration.pipeline import ContentGenerator
```

### Initialization

```python
# Initialize with configuration
loader = ConfigLoader("config")
generator = ContentGenerator(loader)

# Initialize with explicit outline path (optional)
# If provided, this outline will be used for all operations instead of auto-discovery
outline_path = Path("output/tree_grafting/outlines/course_outline_20251216.json")
generator = ContentGenerator(loader, outline_path=outline_path)

# Automatically initializes:
# - OllamaClient (from LLM config)
# - OutlineGenerator
# - LectureGenerator
# - LabGenerator
# - StudyNotesGenerator
# - DiagramGenerator
# - QuestionGenerator
```

**Outline Path Priority**:
- If `outline_path` is provided during initialization, it takes precedence over auto-discovery
- If `outline_path` is `None` (default), the system uses course-aware auto-discovery:
  1. Course-specific directory: `output/{course_name}/outlines/`
  2. Config-specified directory
  3. Project root: `output/outlines/`
  4. Scripts directory: `scripts/output/outlines/`

### Workflow Methods

#### Stage 1: Outline Generation

```python
# Generate outline with defaults from config
outline_path = generator.stage1_generate_outline()

# Generate outline with custom parameters
outline_path = generator.stage1_generate_outline(
    num_modules=5,
    total_sessions=10,
    min_subtopics=3,
    max_subtopics=7,
    course_name="biology"  # Optional course template name
)

# Returns Path to generated outline file
# Saves to: output/{course_name}/outlines/course_outline_TIMESTAMP.{json,md}
```

#### Stage 2: Primary Content Generation (Session-Based)

```python
# Generate all content for all modules (all sessions)
results = generator.stage2_generate_content_by_session()

# Generate for specific modules only
results = generator.stage2_generate_content_by_session(module_ids=[1, 2, 3])

# Skip existing files (don't regenerate)
results = generator.stage2_generate_content_by_session(
    module_ids=[1, 2],
    skip_existing=True
)

# Results structure (list of session results):
# [
#     {
#         "module_id": 1,
#         "session_number": 1,
#         "status": "success",
#         "files": {
#             "lecture": Path(".../lecture.md"),
#             "lab": Path(".../lab.md"),
#             "study_notes": Path(".../study_notes.md"),
#             "diagrams": [Path(".../diagram_1.mmd"), ...],
#             "questions": Path(".../questions.md")
#         }
#     },
#     ...
# ]

# Saves to: output/{course_name}/modules/module_XX/session_YY/
```

#### Complete Pipeline

```python
# Run complete pipeline (Stage 1 + Stage 2)
results = generator.run(
    generate_outline=True,  # Generate new outline
    modules_to_process=[1, 2, 3]  # Optional: specific modules only
)

# Skip outline generation, use existing
results = generator.run(
    generate_outline=False,
    modules_to_process=None  # Process all modules
)

# Results structure:
# {
#     "outline_path": Path(".../course_outline_TIMESTAMP.json"),
#     "session_results": [...],  # List of session results
#     "sessions_generated": 10,
#     "modules_processed": 5
# }
```

### Utility Methods

```python
# Clear output directories (with confirmation)
generator.clear_output_directories(confirm=True)

# Clear specific course directories
generator.clear_output_directories(
    confirm=True,
    course_name="biology"  # Optional: course-specific cleanup
)

# Get output directories (internal method, but documented for reference)
dirs = generator._get_output_directories(course_name="biology")
# Returns: {"outlines": Path, "modules": Path, "logs": Path, ...}
```

## Complete Workflow Example

```python
from src.config.loader import ConfigLoader
from src.generate.orchestration.pipeline import ContentGenerator

# Step 1: Initialize
loader = ConfigLoader("config")
loader.validate_all_configs()
generator = ContentGenerator(loader)

# Step 2: Generate outline (Stage 1)
outline_path = generator.stage1_generate_outline(
    num_modules=5,
    total_sessions=10,
    course_name="biology"
)
print(f"Outline generated: {outline_path}")

# Step 3: Generate all primary content (Stage 2)
results = generator.stage2_generate_content_by_session()
print(f"Generated content for {len(results)} sessions")

# Or run complete pipeline in one call
results = generator.run(
    generate_outline=True,
    modules_to_process=None  # All modules
)
print(f"Pipeline complete: {results['sessions_generated']} sessions generated")
```

## Session-Based Generation

The pipeline generates content **per session** (not per module). Each session gets all primary materials:

```python
# Generate all sessions for all modules
results = generator.stage2_generate_content_by_session()

# Each result contains:
for result in results:
    module_id = result['module_id']
    session_num = result['session_number']
    status = result['status']
    files = result['files']  # Dict with lecture, lab, study_notes, diagrams, questions
    
    print(f"Module {module_id} Session {session_num}: {status}")
    print(f"  Files: {list(files.keys())}")
```

## Error Handling

The pipeline implements "safe-to-fail" error handling:

```python
results = generator.generate_content_for_all_modules()

# Errors are collected, not raised
# Check for errors in results
failed_modules = [
    mid for mid, content in results.items()
    if "error" in content
]

if failed_modules:
    logger.warning(f"Failed modules: {failed_modules}")
    for mid in failed_modules:
        logger.error(f"Module {mid}: {results[mid]['error']}")
```

## Integration Points

### With Configuration
```python
# Loads from ConfigLoader:
# - Course structure
# - LLM settings
# - Prompt templates
# - Output paths
# - Generation parameters
```

### With Generators
```python
# Uses all format generators:
generator.outline_generator     # OutlineGenerator
generator.lecture_generator     # LectureGenerator
generator.lab_generator         # LabGenerator
generator.study_notes_generator # StudyNotesGenerator
generator.diagram_generator     # DiagramGenerator
generator.question_generator    # QuestionGenerator
```

### With File System
```python
# Output structure:
# output/
# ├── outlines/
# │   ├── course_outline_TIMESTAMP.md
# │   └── course_outline_TIMESTAMP.json
# ├── lectures/
# │   └── module_01_cell_biology_lecture.md
# ├── labs/
# │   ├── module_01_cell_biology_lab1.md
# │   └── module_01_cell_biology_lab2.md
# ├── study_notes/
# │   └── module_01_cell_biology_study_notes.md
# ├── diagrams/
# │   ├── diagram_01_1_cell_structure.mmd
# │   └── diagram_01_2_organelles.mmd
# ├── questions/
# │   └── module_01_cell_biology_questions.md
# └── modules/
#     └── module_01_cell_biology/
#         ├── session_01/
#         │   ├── lecture.md
#         │   ├── lab.md
#         │   ├── study_notes.md
#         │   ├── diagram_1.mmd
#         │   └── questions.md
#         # Secondary materials (session-level):
#         # session_01/application.md
#         # session_01/extension.md
#         # session_01/visualization.mmd
#         # session_01/integration.md
#         # session_01/investigation.md
#         # session_01/open_questions.md
```

## Performance Considerations

- **Sequential processing**: Modules processed one at a time
- **LLM timeout**: 120s default per generation
- **Caching**: Outline cached after first generation
- **Progress logging**: INFO-level logs for each module/session

Typical timing:
- Outline generation: 30-60s
- Lecture generation: 60-120s per module
- Lab generation: 30-60s per lab
- Full module: 5-10 minutes
- Full course (20 modules): 2-3 hours

## Testing

Comprehensive tests in `tests/test_pipeline.py`:
- Full pipeline execution
- Individual module generation
- Error handling
- Output file creation

Run tests:
```bash
uv run pytest tests/test_pipeline.py -v
```

## Complete Method Reference

### ContentGenerator Class

```python
class ContentGenerator:
    def __init__(self, config_loader: ConfigLoader) -> None
        """Initialize with ConfigLoader. Auto-initializes all generators."""
    
    def stage1_generate_outline(
        self,
        num_modules: Optional[int] = None,
        total_sessions: Optional[int] = None,
        min_subtopics: Optional[int] = None,
        max_subtopics: Optional[int] = None,
        min_objectives: Optional[int] = None,
        max_objectives: Optional[int] = None,
        min_concepts: Optional[int] = None,
        max_concepts: Optional[int] = None,
        course_name: Optional[str] = None
    ) -> Path
        """Stage 1: Generate course outline (JSON + Markdown). Returns path to outline file."""
    
    def stage2_generate_content_by_session(
        self,
        module_ids: Optional[List[int]] = None,
        skip_existing: bool = False
    ) -> List[Dict[str, Any]]
        """Stage 2: Generate primary content per session (not per module). Returns list of session results."""
    
    def run(
        self,
        generate_outline: bool = True,
        modules_to_process: Optional[List[int]] = None
    ) -> Dict[str, Any]
        """Run the complete pipeline (Stage 1 + Stage 2). Returns dictionary with pipeline results."""
    
    def clear_output_directories(
        self,
        confirm: bool = True,
        course_name: Optional[str] = None
    ) -> None
        """Clear all output directories with optional confirmation."""
```

### Session-Based Generation Details

**Session structure**:
- Primary materials generated **per session** (not per module)
- Each session gets: lecture, lab, study_notes, diagrams, questions
- Secondary materials generated **per session** (application, extension, etc.) - saved directly in session folders

**Output paths**:
```
output/modules/module_XX_name/
├── session_01/
│   ├── lecture.md
│   ├── lab.md
│   ├── study_notes.md
│   ├── diagram_1.mmd
│   ├── diagram_2.mmd
│   └── questions.md
├── session_02/
│   └── ...
    # Secondary materials (session-level, saved directly in session folders):
    # session_01/application.md
    # session_01/extension.md
    # session_01/visualization.mmd
    # session_01/integration.md
    # session_01/investigation.md
    # session_01/open_questions.md
```

## Batch Processing: BatchCourseProcessor

The `BatchCourseProcessor` class provides functionality to process multiple course templates sequentially through the complete generation pipeline.

### Initialization

```python
from src.generate.orchestration.batch import BatchCourseProcessor
from pathlib import Path

# Initialize with config directory
processor = BatchCourseProcessor(
    config_dir=Path("config"),
    project_root=Path(".")  # Optional, defaults to config_dir.parent
)
```

### Methods

#### List Available Courses

```python
courses = processor.list_available_courses()
# Returns: [
#     {"name": "biology", "filename": "biology.yaml", "course_info": {...}},
#     {"name": "chemistry", "filename": "chemistry.yaml", "course_info": {...}},
#     ...
# ]
```

#### Process All Courses for Outline

```python
import argparse

args = argparse.Namespace()
args.config_dir = Path("config")
args.no_interactive = True
args.modules = None
args.types = None
args.run_tests = False

summary = processor.process_all_courses_for_outline(args)
# Returns:
# {
#     'total': 3,
#     'successful': ['biology', 'chemistry'],
#     'failed': [{'name': 'physics', 'error': 'Exit code 1'}],
#     'summary': 'Processed 3 course(s) for outline generation. 2 successful. 1 failed.'
# }
```

#### Process All Courses Full Pipeline

```python
args.skip_setup = False
args.skip_validation = False
args.skip_outline = False
args.skip_primary = False
args.skip_secondary = False
args.skip_website = False

summary = processor.process_all_courses_full_pipeline(args)
# Processes all courses through all 6 stages sequentially
# Returns same summary structure as above
```

### Error Handling

The batch processor implements graceful error handling:
- Each course is processed independently
- Failures in one course don't stop processing of other courses
- All errors are collected and reported in the summary
- Detailed error messages are logged for each failure

### Usage Example

```python
from src.generate.orchestration.batch import BatchCourseProcessor
from pathlib import Path
import argparse

# Setup
config_dir = Path("config")
project_root = Path(".")
processor = BatchCourseProcessor(config_dir, project_root)

# Create args namespace
args = argparse.Namespace()
args.config_dir = config_dir
args.no_interactive = True
args.skip_setup = False
args.skip_validation = False
args.skip_outline = False
args.skip_primary = False
args.skip_secondary = False
args.skip_website = False
args.modules = None
args.types = None
args.run_tests = False

# Process all courses
summary = processor.process_all_courses_full_pipeline(args)

# Check results
print(f"Total: {summary['total']}")
print(f"Successful: {len(summary['successful'])}")
print(f"Failed: {len(summary['failed'])}")

if summary['failed']:
    for failure in summary['failed']:
        print(f"  {failure['name']}: {failure['error']}")
```

### Output Organization

Each course's output is automatically organized into course-specific directories:
- `output/{course_name}/outlines/` - Course outlines
- `output/{course_name}/modules/` - Generated modules
- `output/{course_name}/website/` - Generated website
- `output/{course_name}/logs/` - Log files

This is handled automatically when using the `--course` flag in subprocess calls.

## See Also

- **For Humans**: [README.md](README.md) - Human-readable guide with examples
- **Outline Generator**: [../stages/AGENTS.md](../stages/AGENTS.md) - Outline generation
- **Format Generators**: [../formats/AGENTS.md](../formats/AGENTS.md) - Content format generators
- **Pipeline Guide**: [../../../docs/PIPELINE_GUIDE.md](../../../docs/PIPELINE_GUIDE.md) - Complete pipeline documentation
- **Scripts**: [../../../scripts/AGENTS.md](../../../scripts/AGENTS.md) - Script usage and CLI options
- **JSON Outline**: [../../../docs/JSON_OUTLINE.md](../../../docs/JSON_OUTLINE.md) - Outline format and lifecycle


