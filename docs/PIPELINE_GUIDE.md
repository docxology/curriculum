# Pipeline Guide - Staged Course Generation

Complete guide to the educational course Generator pipeline with detailed script references.

## Quick Reference Card

| Stage | Script | Purpose | Duration | Dependencies |
|-------|--------|---------|----------|--------------|
| **01** | `01_setup_environment.py` | Environment validation | <1 min | None |
| **02** | `02_run_tests.py` | Config validation + tests | 1-150s | Stage 01 |
| **03** | `03_generate_outline.py` | Generate JSON outline | 30-60s | Ollama + model |
| **04** | `04_generate_primary.py` | Generate session content | 2-4 hrs | Stage 03 output |
| **05** | `05_generate_secondary.py` | Generate module synthesis | 30-60 min | Stage 04 output |
| **06** | `06_website.py` | Generate HTML website | <1 min | Stage 03-05 output |
| **All** | `run_pipeline.py` | Full automation | 2-5 hrs | All of above |

**Quick Start**: `uv run python3 scripts/run_pipeline.py` (runs all stages)

**Read time**: 30-45 minutes | **Audience**: All users, especially operators

## Overview

The educational course Generator uses a **6-stage pipeline** for creating comprehensive course materials:

1. **Stage 01 - Environment Setup** (`scripts/01_setup_environment.py`)
2. **Stage 02 - Validation & Tests** (`scripts/02_run_tests.py`)
3. **Stage 03 - Generate Course Outline** (`scripts/03_generate_outline.py`)
4. **Stage 04 - Generate Primary Materials** (`scripts/04_generate_primary.py`)
5. **Stage 05 - Generate Secondary Materials** (`scripts/05_generate_secondary.py`)
6. **Stage 06 - Generate Website** (`scripts/06_website.py`)

All stages can be run independently or together via `scripts/run_pipeline.py` (sequential orchestration with skip flags).

## Pipeline Architecture

```
┌──────────────────────────────────────────────────────┐
│  Stage 01: Environment Setup                         │
│  Script: scripts/01_setup_environment.py             │
│  Tasks: uv check, deps install (optional), Ollama    │
│         check, config validation, output dirs        │
└──────────────────────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────┐
│  Stage 02: Validation & Tests                        │
│  Script: scripts/02_run_tests.py                     │
│  Tasks: config validation, Ollama check, pytest opt  │
└──────────────────────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────┐
│  Stage 03: Outline Generation                        │
│  Script: scripts/03_generate_outline.py              │
│  Module: src/outline_generator.py         │
│  Output: output/outlines/course_outline_*.md         │
└──────────────────────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────┐
│  Stage 04: Primary Materials                         │
│  Script: scripts/04_generate_primary.py              │
│  Module: src/generate/orchestration/pipeline.py (Stage 04)        │
│  Formats: lectures, labs, diagrams, questions, notes │
│  Output: output/{lectures,labs,diagrams,...}/*.md    │
└──────────────────────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────┐
│  Stage 05: Secondary Materials                       │
│  Script: scripts/05_generate_secondary.py            │
│  Outputs: output/{course_name}/modules/module_{id:02d}_{slug}/session_{n:02d}/[type].md │
│  Types: application, extension, visualization,       │
│         integration, investigation, open_questions   │
│  Scope: Session-level (per session, not per module)  │
└──────────────────────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────┐
│  Stage 06: Website Generation                       │
│  Script: scripts/06_website.py                        │
│  Output: output/website/index.html (single HTML)     │
│  Purpose: Browse all course materials in one place  │
└──────────────────────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────┐
│  Full Pipeline                                       │
│  Script: scripts/run_pipeline.py                     │
│  Runs: 01 → 06 sequentially (skips supported)        │
└──────────────────────────────────────────────────────┘
```

## Scripts Reference

### Stage 01: Environment Setup

**Script**: `scripts/01_setup_environment.py`

**Purpose**: Prepare environment and validate prerequisites

**Usage**:
```bash
uv run python3 scripts/01_setup_environment.py --auto-install --start-ollama
```

**Tasks**:
1. Check uv availability
2. Optional dependency install (`uv sync --extra dev`)
3. Validate configs exist and are readable YAML
4. Ensure output directories
5. Check Ollama + gemma3:4b availability

---

### Stage 02: Validation & Tests

**Script**: `scripts/02_run_tests.py`

**Purpose**: Validate configs and optionally run modular test suite with comprehensive reporting

**Usage**:
```bash
# Validation only
uv run python3 scripts/02_run_tests.py

# Validation + tests with output saving
uv run python3 scripts/02_run_tests.py

# Verbose test output
uv run python3 scripts/02_run_tests.py --verbose

# Save to custom directory
uv run python3 scripts/02_run_tests.py --output-dir ./my_reports

# Don't save output
uv run python3 scripts/02_run_tests.py --no-save-output
```

**Tasks**:
1. Validate all configuration files
2. Check Ollama connectivity
3. Optional: Run pytest on modular test suite
4. Parse and report test statistics (passed, failed, skipped, errors, warnings)
5. Extract and display warning details
6. Extract and display failure details
7. Save complete test output to timestamped log file (default: `scripts/test_reports/test_results_YYYYMMDD_HHMMSS.log`)
8. Report per-module test results
9. Calculate and display pass rate

**Output Example**:
```
======================================================================
Running modular test suite with pytest...
======================================================================
Found 8 test modules in tests
✓ Test output saved to: scripts/test_reports/test_results_20241208_143022.log
----------------------------------------------------------------------
======================================================================
TEST RESULTS BY MODULE
======================================================================
✓ test_config_loader              | Total:  15 | Passed:  15 | Failed:   0 | Skipped:   0
✓ test_llm_client                  | Total:  12 | Passed:  12 | Failed:   0 | Skipped:   0
✓ test_utils                       | Total:   8 | Passed:   8 | Failed:   0 | Skipped:   0
...
======================================================================
OVERALL TEST SUMMARY
======================================================================
Total Tests:         85
Passed:              85
Failed:               0
Skipped:              0
Errors:               0
Warnings:             2
Duration:           12.34s
Pass Rate:          100.0%
======================================================================
✓ ALL TESTS PASSED
  (but 2 warnings detected)
======================================================================
```

---

### Stage 03: Generate Outline

**Script**: `scripts/03_generate_outline.py`

**Purpose**: Generate a structured course outline based on `config/course_config.yaml`

**Usage**:
```bash
uv run python3 scripts/03_generate_outline.py
```

**What it does**:
1. Loads course configuration
2. Formats module list for LLM
3. Generates comprehensive outline using Ollama
4. Saves to `output/outlines/course_outline_TIMESTAMP.md`

**Modules Used**:
- `src.config.loader.ConfigLoader`
- `src.llm.client.OllamaClient` 
- `src.generate.stages.stage1_outline.OutlineGenerator`

**Output Format**:
```markdown
# Introductory Biology - Course Outline

**Level**: Undergraduate Introductory
**Duration**: 16 weeks
**Generated**: 2024-12-08 12:00:00

---

## Module 1: Cell Biology
- Cell structure
- Cell function
...
```

**Configuration**:
- Course info: `config/course_config.yaml` → `course` section
- LLM settings: `config/llm_config.yaml` → `llm` and `prompts.outline`
- Output path: `config/output_config.yaml` → `output.directories.outlines`

### Stage 04: Generate Primary Materials

**Script**: `scripts/04_generate_primary.py`

**Purpose**: Generate primary materials PER SESSION using JSON outline structure

**Usage**:
```bash
# Generate for all modules (uses latest JSON outline) - DEFAULT
uv run python3 scripts/04_generate_primary.py

# Explicitly specify all modules (same as above)
uv run python3 scripts/04_generate_primary.py --all

# Generate for specific modules only
uv run python3 scripts/04_generate_primary.py --modules 1 2 3

# Use specific outline JSON file
uv run python3 scripts/04_generate_primary.py --outline scripts/output/outlines/course_outline_20241208.json

# Use custom config directory
uv run python3 scripts/04_generate_primary.py --config-dir /path/to/config
```

**Key Features** (Updated Dec 2025):
- **JSON Outline Integration**: Loads module/session structure from dynamically-generated JSON outlines
- **Session-Based Generation**: Generates content per session (not per module) for granular organization
- **Automatic Outline Discovery**: Searches multiple locations for latest outline (output/outlines/, scripts/output/outlines/)
- **Context Preservation**: Lecture content automatically passed to lab and questions generators
- **Content Cleanup**: Automatic removal of conversational artifacts and placeholder standardization
- **Comprehensive Error Handling**: Clear messages if outline not found with actionable guidance

**Requirements**:
- **JSON Outline**: Must run Stage 03 (`03_generate_outline.py`) first to generate JSON outline
- **Outline Location**: Automatically finds most recent `course_outline_*.json` in standard locations
- **Module Structure**: Uses `module_id`, `module_name`, and `sessions` array from JSON

**What it does**:
1. Loads JSON outline with module/session structure
2. For each session within each module, generates exactly 5 primary artifact types:
   - **lecture.md** - Comprehensive session-specific instructional content
   - **lab.md** - Hands-on exercise related to session topics
   - **study_notes.md** - Concise session summary for review
   - **diagram_1.mmd, diagram_2.mmd, ...** - Mermaid diagrams (number from config, typically 1-2 per session)
   - **questions.md** - Comprehension assessment questions (MC/SA/Essay format)
3. Saves all content to session directories: `output/modules/module_XX/session_YY/`

**Modules Used**:
- `src.generate.formats.lectures.LectureGenerator`
- `src.generate.formats.labs.LabGenerator`
- `src.generate.formats.study_notes.StudyNotesGenerator`
- `src.generate.formats.diagrams.DiagramGenerator`
- `src.generate.formats.questions.QuestionGenerator`
- `src.generate.orchestration.pipeline.ContentGenerator`

**Output Files** (per session):
- `output/{course_name}/modules/module_{id:02d}_{name}/session_{n:02d}/lecture.md`
- `output/{course_name}/modules/module_{id:02d}_{name}/session_{n:02d}/lab.md`
- `output/{course_name}/modules/module_{id:02d}_{name}/session_{n:02d}/study_notes.md`
- `output/{course_name}/modules/module_{id:02d}_{name}/session_{n:02d}/diagram_1.mmd`
- `output/{course_name}/modules/module_{id:02d}_{name}/session_{n:02d}/diagram_2.mmd` (if configured)
- `output/{course_name}/modules/module_{id:02d}_{name}/session_{n:02d}/questions.md`

**Note**: `{course_name}` is the course template name (e.g., `chemistry`, `biology`). When using default config (no template), paths are `output/modules/...` (no course subdirectory).

**Configuration Per Module**:
```yaml
modules:
  - id: 1
    name: "Cell Biology"
    num_lectures: 2      # Generate 2 lectures
    num_labs: 2          # Generate 2 labs
    content_length: 3000 # Target words per lecture
    num_diagrams: 4      # Generate 4 diagrams
    num_questions: 20    # Generate 20 questions
    subtopics:
      - "Cell structure"
      - "Cell function"
    learning_objectives:
      - "Understand cell organization"
```

### Stage 05: Generate Secondary Materials

**Script**: `scripts/05_generate_secondary.py`

**Purpose**: Generate session-level secondary materials (synthesizing session context)

**Usage**:
```bash
# Generate for all modules (default behavior - uses latest JSON outline)
uv run python3 scripts/05_generate_secondary.py

# Explicitly specify all modules
uv run python3 scripts/05_generate_secondary.py --all

# Generate for specific modules only
uv run python3 scripts/05_generate_secondary.py --modules 1 2

# Limit to specific types
uv run python3 scripts/05_generate_secondary.py --all --types application visualization

# Use specific outline JSON file
uv run python3 scripts/05_generate_secondary.py --outline scripts/output/outlines/course_outline_20241208.json

# Validate content quality after generation
uv run python3 scripts/05_generate_secondary.py --all --validate

# Dry-run to preview without calling LLM
uv run python3 scripts/05_generate_secondary.py --modules 1 --dry-run
```

**Key Features** (Updated Dec 2025):
- **JSON Outline Integration**: Loads module structure from dynamically-generated JSON outlines
- **Session-Level Generation**: Generates secondary materials per session (not per module)
- **Session Context Synthesis**: Reads all primary materials from session folder for context
- **Automatic Outline Discovery**: Searches multiple locations for latest outline
- **Content Cleanup**: Automatic removal of conversational artifacts and placeholder standardization
- **Validation Mode** (`--validate`): Post-generation quality checking
- **Dry-Run Mode** (`--dry-run`): Preview what would be generated without making LLM calls

**Requirements**:
- **JSON Outline**: Must run Stage 03 first
- **Primary Materials**: Must run Stage 04 first (script reads from session folders)
- **Module Structure**: Uses `module_id`, `module_name`, and `sessions` array from JSON

**What it does**:
1. Loads JSON outline with module/session structure
2. For each session within each module, generates exactly 6 secondary material types:
   - **application.md** - Real-world applications and case studies
   - **extension.md** - Advanced topics beyond core curriculum
   - **visualization.mmd** - Additional diagrams and concept maps (Mermaid format)
   - **integration.md** - Cross-module connections and synthesis
   - **investigation.md** - Research questions and experiments
   - **open_questions.md** - Current scientific debates and frontiers
3. Saves all content to session directories: `output/modules/module_XX/session_YY/`

**Output Structure**:
```
output/modules/module_01_cell_biology/
  session_01/          # Primary materials (from Stage 04)
    lecture.md
    lab.md
    study_notes.md
    diagram_1.mmd
    diagram_2.mmd
    questions.md
    # Secondary materials (from Stage 05, per session):
    application.md
    extension.md
    visualization.mmd
    integration.md
    investigation.md
    open_questions.md
  session_02/
    ...
```

**Content Cleanup** (Automatic):

All content generated in Stage 04 automatically undergoes cleanup to ensure professional quality:

1. **Conversational Artifact Removal**: Removes informal phrases like:
   - "Okay, here's..."
   - "Would you like..."
   - "Let me know if..."
   - "Feel free to..."

2. **Placeholder Standardization**: Replaces specific references with placeholders:
   - Instructor names ("Dr. Smith", "Professor García") → `[INSTRUCTOR]`
   - Specific dates ("October 26, 2023") → `[DATE]`

3. **Word Count Statement Removal**: Removes LLM-generated word count statements like:
   - "Word Count: 1500 words"
   - "Total: 1200 words"

4. **Content Validation**: Checks for:
   - Missing answer keys in questions
   - Formatting issues
   - Structural completeness

Cleanup is applied automatically during generation - no manual intervention required. See `src/generate/processors/cleanup.py` for implementation details.

---

### Stage 06: Generate Website

**Script**: `scripts/06_website.py`

**Purpose**: Generate a single, self-contained HTML website for browsing all course materials

**Usage**:
```bash
# Generate website (auto-discovers latest outline and content)
uv run python3 scripts/06_website.py

# Use specific outline file
uv run python3 scripts/06_website.py --outline scripts/output/outlines/course_outline_20241208.json

# Custom output path
uv run python3 scripts/06_website.py --output custom/website.html

# Open in browser after generation
uv run python3 scripts/06_website.py --open-browser
```

**Key Features**:
- **Single HTML File**: Self-contained website with embedded CSS and JavaScript
- **Automatic Content Discovery**: Finds all generated materials (lectures, labs, diagrams, etc.)
- **Module Navigation**: Browse by module and session
- **Content Type Filtering**: View specific content types (lectures only, labs only, etc.)
- **Markdown Rendering**: Converts markdown content to HTML for display
- **Mermaid Diagram Support**: Renders Mermaid diagrams inline
- **No Server Required**: Works as a standalone file (open directly in browser)

**Requirements**:
- **JSON Outline**: Must run Stage 03 first (for course structure)
- **Content Materials**: Stages 04-05 generate the content files that website displays
- **Module Structure**: Uses module/session structure from JSON outline

**What it does**:
1. Loads JSON outline to understand course structure
2. Discovers all generated content files (lectures, labs, diagrams, questions, etc.)
3. Converts markdown content to HTML
4. Generates navigation structure (modules → sessions → content types)
5. Creates single HTML file with embedded styles and scripts
6. Saves to `output/website/index.html`

**Output File**:
- `output/website/index.html` - Single HTML file containing entire website

**Website Features**:
- **Module List**: Overview of all modules with session counts
- **Session View**: Browse content by session within each module
- **Content Type Views**: Filter by content type (all lectures, all labs, etc.)
- **Search**: Find content by keywords
- **Responsive Design**: Works on desktop and mobile devices
- **Print-Friendly**: Optimized for printing course materials

**Module**: `src.website.generator.WebsiteGenerator`

**Example Output**:
```
output/website/
  index.html  # Single HTML file (open in browser)
```

---

## Output Directory Discovery

Scripts automatically find generated content across multiple locations for maximum flexibility.

### Outline File Discovery

When scripts need the course outline (stages 04 and 05), they search multiple locations in order:

1. **Course-specific directory** (if course template used): `output/{course_name}/outlines/`
2. **Config-specified directory**: `config/output_config.yaml` → `output.base_directory/outlines/`
3. **Project root**: `output/outlines/`
4. **Scripts directory**: `scripts/output/outlines/`

The **most recent outline by modification time** is automatically selected across all locations.

**Note**: When using course templates (e.g., `chemistry.yaml`), outlines are stored in course-specific directories like `output/chemistry/outlines/`. The system automatically searches both course-specific and default locations for backward compatibility.

### Why Multiple Locations?

- **Flexibility**: Scripts work regardless of where you run them from
- **Development vs Production**: Separate output locations for testing
- **Workspace Organization**: Support different project structures

### Explicit Outline Path

Override automatic discovery with explicit path:

```bash
# Stage 04 - Use specific JSON outline
uv run python3 scripts/04_generate_primary.py --outline custom/outline.json

# Stage 05 - Use specific markdown outline
uv run python3 scripts/05_generate_secondary.py --outline custom/outline.md
```

### How It Works

1. **Script 04** looks for `course_outline_*.json` files
2. **Script 05** looks for `course_outline_*.md` files
3. Both search all configured locations
4. Most recent file (by modification time) is used
5. Clear logging shows which file was selected

### Example Output

```
2024-12-08 14:17:13 - INFO - Using most recent outline from output/outlines/
2024-12-08 14:17:13 - INFO - Loading most recent outline JSON from: /Users/user/biology/scripts/output/outlines/course_outline_20241208_141121.json
```

---

### Full Pipeline

**Script**: `scripts/run_pipeline.py`

**Purpose**: Execute complete 6-stage pipeline

**Usage**:
```bash
# Run full pipeline
uv run python3 scripts/run_pipeline.py

# Skip outline generation (Stage 03)
uv run python3 scripts/run_pipeline.py --skip-outline

# Process only specific modules
uv run python3 scripts/run_pipeline.py --modules 1 2 3

# Set log level
uv run python3 scripts/run_pipeline.py --log-level DEBUG

# Custom config directory
uv run python3 scripts/run_pipeline.py --config-dir /path/to/config
```

**What it does**:
1. Runs Stage 01: Environment setup and validation
2. Runs Stage 02: Configuration validation and optional tests
3. Runs Stage 03: Generates course outline (JSON + Markdown)
4. Runs Stage 04: Generates primary materials (lectures, labs, diagrams, questions, study notes)
5. Runs Stage 05: Generates secondary materials (application, extension, visualization, etc.)
6. Runs Stage 06: Generates HTML website for browsing all materials

**Skip Options**:
- `--skip-setup` - Skip Stage 01
- `--skip-validation` - Skip Stage 02
- `--skip-outline` - Skip Stage 03
- `--skip-primary` - Skip Stage 04
- `--skip-secondary` - Skip Stage 05
- `--skip-website` - Skip Stage 06

**Example Output**:
```
================================================================================
                    educational course GENERATOR
                         Full Pipeline
================================================================================

Configuration directory: /Users/user/biology/config

Course: Introductory Biology
Level: Undergraduate Introductory
Duration: 16 weeks
Total modules: 20

Initializing pipeline...
✓ Pipeline initialized

STAGE 1: Generating Course Outline
...
Stage 03 complete. Outline saved to: output/outlines/course_outline_20241208.md

STAGE 2: Generating Module Content
Processing Module 1/20: Cell Biology
...
✓ Module Cell Biology completed

================================================================================
PIPELINE EXECUTION COMPLETE
================================================================================
Outline: output/outlines/course_outline_20241208.md
Modules generated: 20
✓ All modules generated successfully!
================================================================================
```

## Workflow Examples

### Workflow 1: Full Automation

```bash
# Generate everything with one command
uv run python3 scripts/run_pipeline.py
```

**Result**: Complete course with outline + all modules

### Workflow 2: Staged Generation

```bash
# Step 1: Generate outline first
uv run python3 scripts/03_generate_outline.py

# Review the outline
cat output/outlines/course_outline_*.md

# Edit if needed
vim output/outlines/course_outline_*.md

# Step 2: Generate content (automatically finds latest outline)
uv run python3 scripts/04_generate_primary.py
```

**Result**: Human review between stages

### Workflow 3: Selective Module Generation

```bash
# Generate outline
uv run python3 scripts/03_generate_outline.py

# Generate only modules 1, 5, and 10
uv run python3 scripts/04_generate_primary.py --modules 1 5 10

# Review and decide on more
uv run python3 scripts/04_generate_primary.py --modules 2 3 4
```

**Result**: Incremental, reviewed content generation

### Workflow 4: Regenerate Content Only

```bash
# Skip outline, regenerate all content
uv run python3 scripts/run_pipeline.py --skip-outline

# Or just specific modules
uv run python3 scripts/04_generate_primary.py --modules 1
```

**Result**: Refresh content without regenerating outline

---

### Workflow 5: Iterative Outline Refinement

**Use Case**: Generate multiple outlines, pick the best one

```bash
# Generate 3 different outlines
for i in {1..3}; do
  uv run python3 scripts/03_generate_outline.py --no-interactive
  sleep 2  # Brief pause between generations
done

# Review all generated outlines
ls -lt output/outlines/course_outline_*.json | head -3

# Preview outlines as human-readable markdown
cat output/outlines/course_outline_*.md | less

# Select best outline for content generation
uv run python3 scripts/04_generate_primary.py --outline output/outlines/course_outline_20241209_120000.json
```

**Result**: Multiple outline options, select best one

---

### Workflow 6: Module-by-Module Review

**Use Case**: Generate and review one module at a time

```bash
# Step 1: Generate outline
uv run python3 scripts/03_generate_outline.py

# Step 2: Generate Module 1 only
uv run python3 scripts/04_generate_primary.py --modules 1

# Step 3: Review Module 1 content
ls -la output/modules/module_01_*/session_01/
cat output/modules/module_01_*/session_01/lecture.md

# Step 4: If satisfied, continue with Module 2
uv run python3 scripts/04_generate_primary.py --modules 2

# Step 5: Repeat for each module
uv run python3 scripts/04_generate_primary.py --modules 3 4 5
```

**Result**: Careful, incremental content generation with review points

---

### Workflow 7: High School Course (Simplified)

**Use Case**: Generate simplified content for high school level

```bash
# Step 1: Edit config for high school
# In course_config.yaml:
#   num_modules: 3
#   total_sessions: 9
#   level: "High School"
# In llm_config.yaml:
#   outline_generation.items_per_field: {min: 2, max: 4}

# Step 2: Generate outline
uv run python3 scripts/03_generate_outline.py

# Step 3: Generate all content
uv run python3 scripts/04_generate_primary.py --all
uv run python3 scripts/05_generate_secondary.py --all
```

**Result**: Complete high school educational course with simplified structure

---

### Workflow 8: University Research Course (Advanced)

**Use Case**: Generate comprehensive, research-focused content

```bash
# Step 1: Edit config for university
# In course_config.yaml:
#   num_modules: 8
#   total_sessions: 24
#   level: "Undergraduate Advanced"
# In llm_config.yaml:
#   outline_generation.items_per_field: {min: 5, max: 10}

# Step 2: Generate outline
uv run python3 scripts/03_generate_outline.py

# Step 3: Generate primary materials
uv run python3 scripts/04_generate_primary.py --all

# Step 4: Generate secondary materials (all types)
uv run python3 scripts/05_generate_secondary.py --all --types application extension visualization integration investigation open_questions
```

**Result**: Comprehensive university course with extensive supplementary materials

---

### Workflow 9: Lab-Heavy Course

**Use Case**: Focus on practical, hands-on content

```bash
# Step 1: Edit course_config.yaml
# Add constraints to guide LLM toward practical skills:
#   additional_constraints: "Focus on laboratory techniques, experimental design, and data analysis"

# Step 2: Generate outline with lab focus
uv run python3 scripts/03_generate_outline.py

# Step 3: Generate all content
uv run python3 scripts/04_generate_primary.py --all

# Step 4: Generate investigation-focused secondary materials
uv run python3 scripts/05_generate_secondary.py --all --types investigation application
```

**Result**: Course emphasizing laboratory work and practical applications

---

### Workflow 10: Dry Run and Validation

**Use Case**: Preview what will be generated without LLM calls

```bash
# Step 1: Validate environment
uv run python3 scripts/01_setup_environment.py

# Step 2: Run configuration validation
uv run python3 scripts/02_run_tests.py

# Step 3: Generate outline
uv run python3 scripts/03_generate_outline.py

# Step 4: Dry run primary materials (preview only, no LLM)
# Note: Not directly supported, but can preview outline structure
cat output/outlines/course_outline_*.json | jq '.modules[] | {module_id, module_name, sessions: (.sessions | length)}'

# Step 5: Generate one module as test
uv run python3 scripts/04_generate_primary.py --modules 1

# Step 6: Validate content quality
uv run python3 scripts/05_generate_secondary.py --modules 1 --validate
```

**Result**: Validated setup with sample content before full generation

## Configuration for Pipelines

### Course Configuration (`config/course_config.yaml`)

Controls what gets generated:

```yaml
course:
  name: "Introductory Biology"
  description: "Comprehensive educational course"
  level: "Undergraduate Introductory"
  estimated_duration_weeks: 16

modules:
  - id: 1
    name: "Cell Biology"
    
    # Content amounts (configurable per module)
    num_lectures: 2       # Multiple lectures per module
    num_labs: 2           # Multiple labs per module
    content_length: 3000  # Words per lecture
    num_diagrams: 4       # Number of diagrams
    num_questions: 20     # Number of questions
    
    # Content details
    subtopics:
      - "Cell structure and organization"
      - "Membrane dynamics"
      - "Organelle functions"
      
    learning_objectives:
      - "Describe cell structure"
      - "Explain organelle functions"
```

### LLM Configuration (`config/llm_config.yaml`)

Controls how content is generated:

```yaml
llm:
  provider: "ollama"
  model: "gemma3:4b"
  api_url: "http://localhost:11434/api/generate"
  timeout: 120
  
  parameters:
    temperature: 0.7
    top_p: 0.9
    num_predict: 64000   # 64K max output tokens (128K context window)

outline_generation:
  items_per_field:
    subtopics: {min: 3, max: 7}
    learning_objectives: {min: 3, max: 7}
    key_concepts: {min: 3, max: 7}

prompts:
  outline:
    system: "You are an expert {subject} educator."
    template: "Create a detailed course outline..."
  
  lecture:
    system: "You are an expert {subject} professor."
    template: "Write a comprehensive lecture..."
    
  lab:
    system: "You are an experienced biology lab instructor."
    template: "Create a laboratory exercise..."
  
  # ... more prompts for each format
```

**Outline Generation Settings**: The `outline_generation` section controls the number of items in each field of generated outlines:
- `subtopics`: Min-max subtopics per session (default: 3-7)
- `learning_objectives`: Min-max objectives per session (default: 3-7)
- `key_concepts`: Min-max concepts per session (default: 3-7)

Adjust these bounds based on course complexity and detail level needed. See [CONFIGURATION.md](CONFIGURATION.md) for complete details.

### Output Configuration (`config/output_config.yaml`)

Controls where content is saved:

```yaml
output:
  base_directory: "output"
  
  directories:
    outlines: "outlines"
    lectures: "lectures"
    labs: "labs"
    diagrams: "diagrams"
    questions: "questions"
    study_notes: "study_notes"
  
  logging:
    level: "INFO"
    console: true
```

## Batch Processing: Generate All Courses

The pipeline supports batch processing to generate all available course templates sequentially. This is useful when you have multiple course templates in `config/courses/` and want to generate complete materials for all of them.

### How It Works

When running `03_generate_outline.py` or `run_pipeline.py` in interactive mode, you'll see a course template selection menu. The last option allows you to "Generate all courses", which processes all available course templates sequentially.

### Usage

**Interactive Mode**:
```bash
# Run outline generation
uv run python3 scripts/03_generate_outline.py
# Select "Generate all courses" from the menu

# Or run full pipeline
uv run python3 scripts/run_pipeline.py
# Select "Generate all courses" from the menu
```

**What Happens**:
1. System lists all course templates in `config/courses/`
2. For each course:
   - Runs complete 6-stage pipeline (or just outline generation if using script 03)
   - Uses `--no-interactive` flag automatically (no prompts)
   - Uses `--course <course_name>` flag for course-specific output
   - Continues to next course even if current course fails
3. Displays summary of successes and failures

### Output Organization

Each course's output is automatically organized into course-specific directories:
- `output/{course_name}/outlines/` - Course outlines
- `output/{course_name}/modules/` - Generated modules
- `output/{course_name}/website/` - Generated website
- `output/{course_name}/logs/` - Log files

### Error Handling

The batch processor implements graceful error handling:
- **Continues processing**: Failures in one course don't stop other courses
- **Detailed logging**: Each course's progress is logged separately
- **Comprehensive summary**: Final summary shows which courses succeeded/failed with error messages

### Example Output

```
BATCH PROCESSING: Full Pipeline for 3 Courses
================================================================================
Course 1/3: Introductory Biology
Template: biology
================================================================================
🔧 STAGE 01: Environment Setup (Introductory Biology)
✅ Stage 01 complete
...
✅ Successfully completed full pipeline for: Introductory Biology

Course 2/3: Introductory Chemistry
Template: chemistry
...
✅ Successfully completed full pipeline for: Introductory Chemistry

Course 3/3: Introductory Physics
Template: physics
...
❌ Course Introductory Physics completed with errors: Failed stages: Outline Generation

================================================================================
BATCH PROCESSING SUMMARY
================================================================================
  • Total Courses: 3
  • Successful: 2
  • Failed: 1
✅ Successful courses: biology, chemistry
❌ Failed courses:
  • physics: Failed stages: Outline Generation
```

### Implementation Details

The batch processing functionality is implemented in `src/generate/orchestration/batch.py` with the `BatchCourseProcessor` class. Scripts remain thin orchestrators that call this module.

**Key Methods**:
- `process_all_courses_for_outline()` - Processes all courses for outline generation only
- `process_all_courses_full_pipeline()` - Processes all courses through complete 6-stage pipeline

See [src/generate/orchestration/AGENTS.md](../src/generate/orchestration/AGENTS.md) for complete API documentation.

## Exit Codes and Status Reporting

### Exit Code Meanings

All pipeline scripts return exit codes to indicate success or failure:

- **Exit Code 0 (Success)**: Script completed successfully
  - All sessions processed without errors
  - No critical issues found
  - Warnings may exist but do not cause failure

- **Exit Code 1 (Failure)**: Script encountered errors
  - One or more sessions failed during generation
  - Critical issues found requiring attention
  - Script exceptions occurred

### Exit Code Behavior

**Important**: Warnings (validation issues marked as [NEEDS REVIEW]) do **not** cause exit code 1. Only the following cause failure:

1. **Failed Sessions**: Sessions that threw exceptions during generation
2. **Critical Issues**: Validation problems that indicate serious content issues:
   - Missing required elements (no questions, no applications, etc.)
   - Structural failures (invalid syntax, parsing errors)
   - Complete generation failures

**Examples**:
- Exit code 0: 10 sessions processed, 2 have word count warnings → Success
- Exit code 1: 10 sessions processed, 1 session failed with exception → Failure
- Exit code 1: 10 sessions processed, 3 have critical "no questions detected" issues → Failure

### Batch Processing Exit Codes

When running batch processing (`run_pipeline.py` with multiple courses):

- Each stage script's exit code is checked
- If any stage returns exit code 1, the course is marked as failed
- Batch processing continues with remaining courses even if one fails
- Final summary shows successful vs failed courses

**Example Output**:
```
❌ Course Introductory Physics completed with errors: Failed stages: Primary Materials
```

This indicates that the "Primary Materials" stage returned exit code 1 for this course.

## Understanding Log Output

The pipeline generates detailed logs during execution. Understanding these logs helps monitor progress and identify issues.

### Log File Location

All scripts write logs to timestamped files:
- Location: `output/logs/`
- Format: `{script_name}_{YYYYMMDD}_{HHMMSS}.log`
- Example: `04_generate_primary_20251209_091827.log`

### Validation Status Indicators

Content generation logs include validation status for each generated item:

**COMPLIANT** ✓ - Content meets all quality requirements:
```
✓ Lecture generated: [COMPLIANT]
  - Length: 7002 chars, 1022 words
  - Requirements: 1000-1500 words, 5-15 examples, 4-8 sections
  - Structure: 7 sections, 0 subsections
  - Content: 11 examples, 11 terms defined
```

**NEEDS REVIEW** ⚠️ - Content has validation warnings:
```
⚠️ Lecture generated: [NEEDS REVIEW]
  - Length: 6256 chars, 899 words
  - Requirements: 1000-1500 words, 5-15 examples, 4-8 sections
  - Structure: 6 sections, 0 subsections
  - Content: 10 examples, 16 terms defined
  ⚠️  Word count (899) below minimum 1000
```

### Common Log Patterns

#### Stage 04: Primary Materials Generation

**Successful Generation**:
```
[1/6] Session 1: Bioch. & Biomolecules
  → Generating lecture...
✓ Lecture generated: [COMPLIANT]
  → Generating lab...
✓ Lab generated: [COMPLIANT]
  → Generating study notes...
✓ Study notes generated: [COMPLIANT]
  → Generating diagrams...
  → Generating questions...
✓ Questions generated: [COMPLIANT]
  ✓ Session 1 completed
```

**With Warnings**:
```
[2/6] Session 2: Cell Structure & Organelles
  → Generating lecture...
⚠️ Lecture generated: [NEEDS REVIEW]
  ⚠️  Word count (899) below minimum 1000
  → Generating study notes...
⚠️ Study notes generated: [NEEDS REVIEW]
  ⚠️  Too many key concepts (11, maximum 10)
  ✓ Session 2 completed
```

#### Stage 05: Secondary Materials Generation

**Successful Generation (All Compliant)**:
```
Session 1/6: Bioch. & Biomolecules
Generating application for session 1: Bioch. & Biomolecules...
  ✓ Application generated: [COMPLIANT]
    - Length: 4523 chars, 678 words
    - Requirements: 3-5 applications, 150-200 words each, max 1000 total words
    - Applications: 4
    - Avg words per application: 169
  → Saved to: output/modules/module_01_.../session_01/application.md

Generating extension for session 1: Bioch. & Biomolecules...
  ✓ Extension generated: [COMPLIANT]
    - Length: 3245 chars, 487 words
    - Requirements: 3-4 topics, 100-150 words each, max 600 total words
    - Topics: 3
    - Avg words per topic: 162
  → Saved to: output/modules/module_01_.../session_01/extension.md

Generating visualization for session 1: Bioch. & Biomolecules...
  ✓ Visualization generated: [COMPLIANT]
    - Length: 234 chars
    - Requirements: min 3 diagram elements
    - Elements: 8 (nodes: 5, connections: 3)
  → Saved to: output/modules/module_01_.../session_01/visualization.mmd

  ✓ Generated 6 secondary materials
```

**With Validation Warnings**:
```
Session 2/6: Cell Structure & Organelles
Generating application for session 2: Cell Structure & Organelles...
  ⚠️ Application generated: [NEEDS REVIEW]
    - Length: 3124 chars, 468 words
    - Requirements: 3-5 applications, 150-200 words each, max 1000 total words
    - Applications: 2
    ⚠️  Only 2 applications found (require 3-5, need 1 more - add ## Application N sections)
    ⚠️  Application 1 has 120 words (require 150-200, need 30 more words)
    💡 Tip: See docs/FORMATS.md → Validation and Quality Checks for guidance
    💡 Tip: Consider regenerating if issues are significant (validation is conservative)
  → Saved to: output/modules/module_02_.../session_02/application.md
```

#### Stage 06: Website Generation

**Successful Generation**:
```
Loading course outline from: output/outlines/course_outline_20241208.json
Found 1 modules with 4 total sessions
Discovering content files...
  ✓ Found 4 lectures
  ✓ Found 4 labs
  ✓ Found 4 study notes
  ✓ Found 8 diagrams
  ✓ Found 4 question sets
  ✓ Found 24 secondary materials

Generating website...
  ✓ Converted 44 markdown files to HTML
  ✓ Generated navigation structure
  ✓ Embedded styles and scripts
  ✓ Website saved to: output/website/index.html
  ✓ Website size: 2.3 MB (self-contained)

Opening in browser...
```

**Website Features**:
- Single HTML file (no server required)
- Module and session navigation
- Content type filtering
- Search functionality
- Responsive design

Generating integration for session 2: Cell Structure & Organelles...
  ⚠️ Integration generated: [NEEDS REVIEW]
    - Length: 5234 chars, 784 words
    - Requirements: min 3 connections, max 1000 words
    - Connections: 1
    ⚠️  Only 1 connections found (require at least 3, need 2 more - add references to other modules/topics)
    💡 Tip: See docs/FORMATS.md → Validation and Quality Checks for guidance
  → Saved to: output/modules/module_02_.../session_02/integration.md
```

### Validation Warning Messages

**Lectures**:
- `⚠️ Word count (899) below minimum 1000` - Content too short
- `⚠️ Word count (1600) exceeds maximum 1500` - Content too long
- `⚠️ Too many examples (16, maximum 15)` - Exceeds example limit
- `⚠️ Too few sections (3, minimum 4)` - Insufficient structure

**Study Notes**:
- `⚠️ Too many key concepts (11, maximum 10)` - Exceeds concept limit
- `⚠️ Only 0 key concepts highlighted (require 3-10)` - Missing formatting
- `⚠️ Word count (1500) exceeds maximum 1200` - Content too long

**Questions**:
- `⚠️ No questions detected - check question format` - Format parsing issue
- `⚠️ Missing answers: 2 questions lack answers` - Incomplete content
- `⚠️ Missing explanations: 3 MC questions lack explanations` - Missing explanations

**Secondary Materials**:
- `⚠️ Only 2 applications found (require 3-5, need 1 more)` - Too few applications
- `⚠️ Application 1 has 100 words (require 150-200, need 50 more words)` - Application too short
- `⚠️ Only 1 connections found (require at least 3, need 2 more)` - Too few integration connections
- `⚠️ Only 2 research questions found (require at least 3, need 1 more)` - Too few investigation questions
- `⚠️ Only 2 diagram elements found (require at least 3)` - Visualization too simple

### Actions for "[NEEDS REVIEW]" Items

When content shows "[NEEDS REVIEW]" status:

1. **Review the Content**: Check if quality is acceptable despite warnings
2. **Check Warning Details**: Read specific warning messages
3. **Decide Action**:
   - **Accept**: If content quality is good, warnings can be ignored
   - **Regenerate**: Run generation again (may produce different results)
   - **Edit Manually**: Fix issues directly in generated markdown files
   - **Adjust Config**: Modify validation criteria in `llm_config.yaml` if too strict

**Example Decision Tree**:
```
⚠️ Word count (899) below minimum 1000
  → Is content comprehensive? 
    → Yes: Accept (validation is conservative)
    → No: Regenerate or manually expand
```

### Progress Indicators

**Module Processing**:
```
============================================================
Module 1: Molecular & Cellular Foundations (2 sessions)
============================================================

[1/6] Session 1: Bioch. & Biomolecules
  → Generating lecture...
  → Generating lab...
  ...
  ✓ Session 1 completed

[2/6] Session 2: Cell Structure & Organelles
  ...
  ✓ Session 2 completed
```

**Summary Statistics**:
```
================================================================================
PRIMARY MATERIALS COMPLETE
================================================================================
Total sessions processed: 6
Successful: 6
Failed: 0
================================================================================
```

### Error Messages

**Configuration Errors**:
```
ERROR: Configuration error: Missing required field: model
  → Fix: Check llm_config.yaml has 'model' field
```

**Outline Not Found**:
```
ERROR: No outline JSON found. Generate one first:
  uv run python3 scripts/03_generate_outline.py
```

**LLM Connection Errors**:
```
ERROR: Ollama connection failed: Connection refused
  → Fix: Start Ollama service: ollama serve
```

### Log Analysis Tips

1. **Search for Warnings**: `grep "⚠️" log_file.log` to find all warnings
2. **Check Completion**: Look for "COMPLETE" sections to verify successful runs
3. **Review Failures**: Search for "ERROR" or "Failed" to identify issues
4. **Validation Summary**: Count "[COMPLIANT]" vs "[NEEDS REVIEW]" to assess quality

### Log Verbosity

**INFO Level** (default): Shows progress, validation status, warnings
**DEBUG Level**: Includes detailed LLM prompts, full responses, internal state

Enable debug logging:
```bash
uv run python3 scripts/run_pipeline.py --log-level DEBUG
```

## Error Handling

All scripts implement **safe-to-fail** principles:

1. **Configuration Errors**: Fail fast with clear messages
2. **LLM Errors**: Retry with exponential backoff
3. **Module Failures**: Continue with other modules, report at end
4. **Partial Success**: Save what was generated successfully

**Example**:
```
Processing Module 5/20: Evolution
✗ Error processing module Evolution: Connection timeout

Processing Module 6/20: Ecology
✓ Module Ecology completed successfully

...

SUMMARY: 19 succeeded, 1 failed out of 20
Failed:
  - Evolution: Connection timeout
```

## Monitoring Progress

### Log Levels

```bash
# Normal operation (INFO level)
uv run python3 scripts/run_pipeline.py

# Detailed debugging (DEBUG level)
uv run python3 scripts/run_pipeline.py --log-level DEBUG

# Minimal output (WARNING level)
uv run python3 scripts/run_pipeline.py --log-level WARNING
```

### Progress Indicators

- `[1/20]` - Module being processed
- `✓` - Success indicator
- `✗` - Failure indicator
- `Generating lecture 1/2...` - Sub-task progress

## Performance Considerations

### Sequential Processing

Current implementation processes modules **sequentially**:
- Safer (one LLM call at a time)
- Predictable resource usage
- Easy to debug

### Estimated Times

Approximate generation times (with gemma3:4b):

- **Outline**: 30-60 seconds
- **Lecture**: 60-120 seconds each
- **Lab**: 45-90 seconds each
- **Diagram**: 20-40 seconds each
- **Questions**: 40-80 seconds
- **Study Notes**: 30-60 seconds

**Full 20-module course**: ~2-4 hours (depends on configuration)

## Troubleshooting

For troubleshooting information, see **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)**.

**Common issues**:
- **Ollama connection errors**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md#llm-issues)
- **Configuration errors**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md#configuration-issues)
- **Generation failures**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md#generation-issues)
- **Import errors**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md#import-errors)

**Quick fixes**:
- **Ollama not running**: `ollama serve`
- **Config files missing**: Run `01_setup_environment.py`
- **Outline not found**: Run `03_generate_outline.py` first

### Troubleshooting Batch Processing Failures

When batch processing reports "Failed stages", follow these steps:

1. **Check the error message**: The batch processor now includes detailed error context:
   ```
   ❌ Course Introductory Physics completed with errors: Failed stages: Primary Materials
   Script 04_generate_primary.py exited with code 1
   Script stderr (first 500 chars): ...
   Last 10 lines from log file (04_generate_primary_20251210_140023.log): ...
   ```

2. **Review the log file**: Check the most recent log file in `output/logs/`:
   ```bash
   # Find most recent log for failed stage
   ls -lt output/logs/04_generate_primary_*.log | head -1
   
   # Check exit code reason
   tail -50 <log_file> | grep "EXIT CODE"
   ```

3. **Common failure reasons**:
   - **Failed sessions**: Check log for "Failed sessions:" section
   - **Critical issues**: Check log for "[CRITICAL]" section
   - **Exceptions**: Check log for stack traces

4. **Understanding exit codes**:
   - Exit code 0: Success (warnings may exist but don't cause failure)
   - Exit code 1: Failure (failed sessions or critical issues)

5. **Action items**:
   - If sessions failed: Review error messages, regenerate specific sessions
   - If critical issues: Review validation warnings, fix content or regenerate
   - If exceptions: Check system resources, Ollama connection, file permissions

**Example diagnostic workflow**:
```bash
# 1. Check batch summary
grep "Failed courses" <batch_log>

# 2. Check specific stage log
tail -100 output/logs/04_generate_primary_*.log | grep -A 20 "EXIT CODE"

# 3. Check for failed sessions
grep "Failed sessions" output/logs/04_generate_primary_*.log

# 4. Check for critical issues
grep "CRITICAL" output/logs/04_generate_primary_*.log
```
- **Module generation failed**: Regenerate with `--modules <id>`

## Next Steps

- See [FORMATS.md](FORMATS.md) for detailed content format documentation
- See [CONFIGURATION.md](CONFIGURATION.md) for complete configuration reference
- See [ARCHITECTURE.md](ARCHITECTURE.md) for system design details

## Summary

**Six scripts, infinite possibilities:**

1. `01_setup_environment.py` - Environment validation
2. `02_run_tests.py` - Configuration and testing
3. `03_generate_outline.py` - Course structure
4. `04_generate_primary.py` - Primary materials  
5. `05_generate_secondary.py` - Secondary materials
6. `run_pipeline.py` - Complete automation

All configurable, all modular, all text-based for full manual control.

---

## Related Documentation

### Essential Reading (Before Running Pipeline)
- **[CONFIGURATION.md](CONFIGURATION.md)** - Configure all YAML files before running
- **[JSON_OUTLINE.md](JSON_OUTLINE.md)** - Understand JSON outlines (Stage 03 output, Stages 04-05 input)
- **[../SETUP.md](../SETUP.md)** - Initial setup before Stage 01

### Stage-Specific References
| Stage | Script | Key Documentation |
|-------|--------|-------------------|
| **01** | `01_setup_environment.py` | [../SETUP.md](../SETUP.md), [CONFIGURATION.md](CONFIGURATION.md) |
| **02** | `02_run_tests.py` | [TESTING_COVERAGE.md](TESTING_COVERAGE.md) |
| **03** | `03_generate_outline.py` | [JSON_OUTLINE.md](JSON_OUTLINE.md), [CONFIGURATION.md](CONFIGURATION.md) |
| **04** | `04_generate_primary.py` | [FORMATS.md](FORMATS.md), [JSON_OUTLINE.md](JSON_OUTLINE.md) |
| **05** | `05_generate_secondary.py` | [FORMATS.md](FORMATS.md), [JSON_OUTLINE.md](JSON_OUTLINE.md) |
| **All** | `run_pipeline.py` | All of the above |

### Technical Details
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Pipeline orchestration architecture
- **[API.md](API.md)** - `ContentGenerator` and generator APIs
- **[FORMATS.md](FORMATS.md)** - Detailed format specifications

### Troubleshooting & Examples
| Issue | Reference |
|-------|-----------|
| **Outline not found** | [JSON_OUTLINE.md](JSON_OUTLINE.md) → Troubleshooting |
| **Config errors** | [CONFIGURATION.md](CONFIGURATION.md) → Troubleshooting |
| **LLM connection errors** | This document → Troubleshooting |
| **Custom workflows** | [API.md](API.md) → Custom Workflow Examples |
| **Test failures** | [TESTING_COVERAGE.md](TESTING_COVERAGE.md) |

### Workflow Examples
| Workflow | Reference |
|----------|-----------|
| **Full automation** | This document → Workflow 1 |
| **Staged generation** | This document → Workflow 2 |
| **Selective modules** | This document → Workflow 3 |
| **Regenerate content** | This document → Workflow 4 |
| **Custom workflow** | [API.md](API.md) → Complete Example |

