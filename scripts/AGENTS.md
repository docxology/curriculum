# Pipeline Scripts - For AI Agents

## Purpose

This directory contains the 6 executable Python scripts that comprise the educational course Generator pipeline. Scripts are designed for both manual execution and automated (hands-off) workflows.

## 6-Stage Pipeline Overview

```
Stage 01: Environment Setup    → 01_setup_environment.py
Stage 02: Validation & Tests    → 02_run_tests.py
Stage 03: Generate Outline      → 03_generate_outline.py
Stage 04: Generate Primary      → 04_generate_primary.py
Stage 05: Generate Secondary    → 05_generate_secondary.py
Stage 06: Generate Website      → 06_website.py

Master Orchestrator             → run_pipeline.py (runs all 6 stages)
```

## Scripts

### 01_setup_environment.py
**Stage 01: Environment Setup and Validation**

Environment validation including system information, dependencies, configuration, and Ollama service.

**What it does**:
- Reports system information (Python version, platform, disk space)
- Checks tool availability (uv, python3, git, ollama)
- Validates all YAML configurations
- Ensures output directory structure exists
- Verifies Ollama service and configured model

**Default behavior**:
- Validates environment WITHOUT making changes
- Reports missing tools/models but doesn't fail
- Creates output directories if missing
- Logs detailed system information

**Command-line options**:
- `--auto-install` - Install dependencies with uv
- `--start-ollama` - Attempt to start Ollama if not running
- `--verbose` / `-v` - Enable debug logging
- `--config-dir PATH` - Custom configuration directory

**Exit codes**:
- `0` - Environment ready
- `1` - Critical failure (missing required tools, invalid config)

**Hands-off usage**:
```bash
uv run python3 scripts/01_setup_environment.py --auto-install --start-ollama
```

### 02_run_tests.py
**Stage 02: Validation and Testing**

Validates configuration and optionally runs pytest suite with detailed reporting.

**What it does**:
- Validates all configuration files
- Tests Ollama connectivity
- Runs fast unit tests by default (NO MOCKS, ~5s)
- Optionally runs full integration tests (requires Ollama, ~150s)
- Saves complete test output to timestamped log file
- Parses and reports test statistics
- Displays per-module test results

**Default behavior**:
- Runs validation + fast unit tests by default
- Skips integration tests requiring Ollama (use `--include-ollama` to include them)
- Saves test output to `scripts/test_reports/test_results_TIMESTAMP.log`
- Shows pass rate and warnings

**Command-line options**:
- `--skip-tests` - Skip pytest tests (validation only)
- `--include-ollama` - Run all tests including integration tests
- `--skip-validation` - Skip config validation, only run tests
- `--skip-tests` - Skip tests, only validate config
- `--verbose` / `-v` - Show detailed test output
- `--no-coverage` - Disable coverage reporting
- `--no-save-output` - Don't save test output to file
- `--output-dir PATH` - Custom directory for test reports
- `--config-dir PATH` - Custom configuration directory

**Exit codes**:
- `0` - Validation and tests passed
- `1` - Validation failed
- `2` - Tests failed
- `3` - Pytest error (no tests collected)

**Hands-off usage**:
```bash
# Fast validation + unit tests (runs by default)
uv run python3 scripts/02_run_tests.py

# Full test suite including integration tests
uv run python3 scripts/02_run_tests.py --include-ollama

# Validation only (skip tests)
uv run python3 scripts/02_run_tests.py --skip-tests
```

### 03_generate_outline.py
**Stage 03: Outline Generation (Interactive by Default)**

Generates course outline with LLM. Interactive by default, allowing customization of course metadata and structure.

**What it does**:
- **Shows course template selection menu** (if templates available)
- Loads course configuration (from template or default)
- **Interactively** prompts for course metadata (name, subject, level, description, language)
- Prompts for structure (num_modules, total_sessions)
- Prompts for content bounds (subtopics, objectives, concepts per session)
- Generates outline using Ollama
- Saves both JSON and Markdown formats
- Outputs to `output/outlines/course_outline_TIMESTAMP.{json,md}`

**Default behavior**:
- **INTERACTIVE MODE** - Shows template selection, then prompts for all customizations
- Uses config defaults as initial values
- Shows current values in prompts [default]
- Validates user input
- Logs all changes made
- Generates outline with LLM

**Command-line options**:
- `--no-interactive` - **Disable interactive prompts**, use config defaults
- `--course NAME` - **Use specific course template** from `config/courses/` (e.g., `--course biology`)
- `--config-dir PATH` - Custom configuration directory
- `--output PATH` - Custom output path for outline
- `--output-dir PATH` - Override base output directory
- `--clear-output` - Clear output directory before generation

**Exit codes**:
- `0` - Outline generated successfully
- `1` - Generation failed

**Hands-off usage** (critical for automation):
```bash
# Non-interactive mode (uses all config defaults)
uv run python3 scripts/03_generate_outline.py --no-interactive

# Use specific course template
uv run python3 scripts/03_generate_outline.py --no-interactive --course biology
```

**Interactive prompts** (when `--no-interactive` NOT used):
1. **Course template selection** (if templates available in `config/courses/`)
   - Shows numbered menu of available templates
   - Option to use default `course_config.yaml`
   - **Option to generate all courses** - Processes all available course templates sequentially
2. Course name [default from config/template]
3. Subject/Expertise area [default from config/template]
4. Course level [default from config/template]
5. Language for course content generation [default from config, typically "English"]
6. Number of modules [default from config/template]
7. Total sessions [default from config/template]
8. Minimum subtopics per session [default from llm_config]
9. Maximum subtopics per session [default from llm_config]
10. Minimum learning objectives per session [default from llm_config]
11. Maximum learning objectives per session [default from llm_config]
12. Minimum key concepts per session [default from llm_config]
13. Maximum key concepts per session [default from llm_config]
14. Course description [default from config/template]
15. Additional constraints [optional, press Enter to skip]
16. Output base directory [default from config]
17. Clear output directory? (y/n) [n]

### 04_generate_primary.py
**Stage 04: Primary Materials Generation (Session-Based)**

Generates primary materials for each session: lectures, labs, study notes, diagrams, questions.

**What it does**:
- Loads module/session structure from JSON outline
- **Automatically finds latest outline** if not specified
- Generates content **per session** (not per module)
- Creates session-based folder structure
- Generates 5 primary material types per session:
  1. `lecture.md` - Instructional content
  2. `lab.md` - Laboratory exercise with procedures
  3. `study_notes.md` - Concise session summary
  4. `diagram_1.mmd`, `diagram_2.mmd`, ... - Mermaid diagrams (number from config, typically 1-2)
  5. `questions.md` - Comprehension assessment questions
- Saves to `output/{course_name}/modules/module_XX/session_YY/` (course-specific directory)

**Default behavior**:
- **Searches for JSON outline** in multiple locations (in order):
  1. Course-specific: `output/{course_name}/outlines/course_outline_*.json` (if course_name known)
  2. Config-specified: `{base_directory}/outlines/course_outline_*.json`
  3. Project root: `output/outlines/course_outline_*.json`
  4. Scripts directory: `scripts/output/outlines/course_outline_*.json`
  5. All course-specific directories: `output/{course}/outlines/` (when batch processing)
- **Selects most recent** by modification time
- **Processes ALL modules** if no `--modules` specified
- Logs which outline file is used
- Shows progress per session

**Command-line options**:
- `--all` - Generate for all modules (default if no --modules)
- `--modules ID [ID ...]` - Generate for specific module IDs only
- `--outline PATH` - Use specific outline JSON (overrides auto-discovery)
- `--sessions N` - Override number of sessions per module
- `--config-dir PATH` - Custom configuration directory

**Exit codes**:
- `0` - All sessions generated successfully
- `1` - One or more sessions failed OR no outline found

**Outline discovery**:
```python
# Priority 1: Explicit path (if --outline provided)
# The specified outline path is passed to ContentGenerator and takes precedence
--outline path/to/specific_outline.json

# Priority 2: Automatic discovery (if --outline not provided)
# Searches multiple locations in order:
# 1. Course-specific: output/{course_name}/outlines/
# 2. Config-specified: {base_directory}/outlines/
# 3. Project root: output/outlines/
# 4. Scripts: scripts/output/outlines/
# 5. All course dirs: output/{course}/outlines/ (batch mode)
# Selects: Most recent course_outline_*.json by modification time
```

**Note**: When `--outline` is provided, it is passed to `ContentGenerator` during initialization and takes precedence over auto-discovery. This ensures consistent outline usage throughout the generation process.

**Hands-off usage**:
```bash
# Generate all modules (auto-finds latest outline)
uv run python3 scripts/04_generate_primary.py

# Generate specific modules
uv run python3 scripts/04_generate_primary.py --modules 1 2 3
```

**Output structure** (course-specific):
```
output/{course_name}/modules/
  module_01_molecular_foundations/
    session_01/
      lecture.md
      lab.md
      study_notes.md
      diagram_1.mmd
      diagram_2.mmd
      questions.md
    session_02/
      ...
```

**Note**: Output is saved to course-specific directories: `output/{course_name}/modules/` where `{course_name}` is derived from the outline metadata or default course config.

### 05_generate_secondary.py
**Stage 05: Secondary Materials Generation (Session-Level)**

Generates secondary materials per session, synthesizing session context: application, extension, visualization, integration, investigation, open_questions.

**What it does**:
- Loads module structure from JSON outline
- **Automatically finds latest outline** if not specified
- Reads primary materials from session folders
- Generates 6 types of secondary materials per session:
  1. `application.md` - Real-world applications and case studies
  2. `extension.md` - Advanced topics beyond core curriculum
  3. `visualization.mmd` - Additional diagrams and concept maps (Mermaid format)
  4. `integration.md` - Cross-module connections and synthesis
  5. `investigation.md` - Research questions and experiments
  6. `open_questions.md` - Current scientific debates and frontiers
- Saves to `output/{course_name}/modules/module_XX/session_YY/[type].md` (or `.mmd` for visualization) (course-specific directory)

**Default behavior**:
- **Searches for JSON outline** (same as Stage 04)
- **Processes ALL modules** if no `--modules` specified
- **Generates ALL 6 types** if no `--types` specified
- Reads all primary materials for context
- Logs outline file used

**Command-line options**:
- `--all` - Generate for all modules (default if no --modules)
- `--modules ID [ID ...]` - Generate for specific module IDs
- `--types TYPE [TYPE ...]` - Specific types to generate
  - Available: application, extension, visualization, integration, investigation, open_questions
- `--outline PATH` - Use specific outline JSON
- `--validate` - Validate generated content for quality
- `--dry-run` - Show what would be generated without calling LLM
- `--config-dir PATH` - Custom configuration directory

**Exit codes**:
- `0` - All modules generated successfully
- `1` - One or more modules failed OR no outline found

**Hands-off usage**:
```bash
# Generate all secondary materials for all modules
uv run python3 scripts/05_generate_secondary.py

# Generate specific types for specific modules
uv run python3 scripts/05_generate_secondary.py --modules 1 2 --types application visualization
```

**Output structure** (course-specific):
```
output/{course_name}/modules/
  module_01_molecular_foundations/
    session_01/        # From Stage 04
      lecture.md
      lab.md
      study_notes.md
      diagram_1.mmd
      diagram_2.mmd
      questions.md
      # From Stage 05 (per session):
      application.md
      extension.md
      visualization.mmd
      integration.md
      investigation.md
      open_questions.md
    session_02/
      ...
```

**Note**: Output is saved to course-specific directories: `output/{course_name}/modules/` where `{course_name}` is derived from the outline metadata or default course config.

### 06_website.py
**Stage 06: Website Generation**

Generates a single, self-contained HTML website that serves as an entry point to browse all course materials.

**What it does**:
- Loads module structure from JSON outline
- **Automatically finds latest outline** if not specified
- Scans output directory for all available content files
- Converts markdown content to HTML
- Generates single HTML file with embedded CSS and JavaScript
- Includes Mermaid.js for client-side diagram rendering
- Creates intuitive navigation (Course → Module → Session → Content Type)
- Saves to `output/{course_name}/website/index.html` or `output/website/index.html` (course-specific if course_name available, otherwise default)

**Default behavior**:
- **Searches for JSON outline** (same as Stages 04/05)
- **Processes ALL modules** from outline
- **Includes ALL content types** (primary + secondary)
- Logs outline file used
- Shows file path for opening in browser

**Command-line options**:
- `--outline PATH` - Use specific outline JSON (default: auto-discover)
- `--output PATH` - Custom output path for HTML file (default: `output/{course_name}/website/index.html` or `output/website/index.html`)
- `--config-dir PATH` - Custom configuration directory
- `--open-browser` - Open generated website in default browser after generation

**Exit codes**:
- `0` - Website generated successfully
- `1` - Generation failed OR no outline found

**Hands-off usage**:
```bash
# Generate website (auto-finds latest outline)
uv run python3 scripts/06_website.py

# Use specific outline
uv run python3 scripts/06_website.py --outline path/to/outline.json

# Open in browser after generation
uv run python3 scripts/06_website.py --open-browser
```

**Output structure**:
```
output/{course_name}/website/
  index.html       # Single self-contained HTML file (course-specific if course_name available)
# OR
output/website/
  index.html       # Default location if course_name not available
```

**Website features**:
- Responsive design (mobile-friendly)
- Accessible (semantic HTML, ARIA labels, keyboard navigation)
- Hierarchical navigation (Module → Session → Content Type)
- Mermaid.js integration for diagram rendering
- Markdown content converted to HTML
- Graceful handling of missing content

### run_pipeline.py
**Master Orchestrator: Execute All 6 Stages**

Runs all pipeline stages sequentially with logging and error handling.

**What it does**:
- Executes stages 01→06 in order
- Forwards command-line arguments to appropriate stages
- Logs each stage's progress
- Reports summary at end
- Allows skipping specific stages
- Supports module/type filtering for stages 04 and 05

**Default behavior**:
- Runs ALL 6 stages (01→06)
- **Stage 03 is INTERACTIVE by default** (prompts user)
- Stops on critical failure (stages 01-03)
- Continues on partial failure (stages 04-06)
- Logs to file + console

**Command-line options**:
- `--skip-setup` - Skip Stage 01
- `--skip-validation` - Skip Stage 02
- `--skip-outline` - Skip Stage 03
- `--skip-primary` - Skip Stage 04
- `--skip-secondary` - Skip Stage 05
- `--skip-website` - Skip Stage 06
- `--modules ID [ID ...]` - Pass to stages 04 and 05
- `--types TYPE [TYPE ...]` - Pass to stage 05
- `--config-dir PATH` - Pass to all stages
- `--no-interactive` - **CRITICAL FOR AUTOMATION** - Pass to stage 03
- `--course NAME` - **Course template name** - Pass to stage 03 (e.g., `--course biology`)
- `--language LANGUAGE` - Language for course content generation (e.g., "English", "Spanish", "French"). Defaults to config value or prompts for input
- `--run-tests` - (Deprecated - tests run by default) Pass to stage 02 (no effect, tests run automatically)
- `--log-level LEVEL` - Set logging level (DEBUG, INFO, WARNING, ERROR)

**Exit codes**:
- `0` - All stages completed successfully
- `1+` - One or more stages failed

**Hands-off usage** (fully automated):
```bash
# Complete hands-off execution (NO USER INTERACTION)
uv run python3 scripts/run_pipeline.py --no-interactive

# Use specific course template
uv run python3 scripts/run_pipeline.py --no-interactive --course biology

# Skip setup/validation, generate content only
uv run python3 scripts/run_pipeline.py --no-interactive --skip-setup --skip-validation

# Generate specific modules only
uv run python3 scripts/run_pipeline.py --no-interactive --modules 1 2 3

# Use specific language
uv run python3 scripts/run_pipeline.py --no-interactive --language Spanish
```

**Batch processing** (generate all courses):
```bash
# Interactive mode: Select "Generate all courses" from menu
uv run python3 scripts/run_pipeline.py

# The system will:
# 1. Show course template selection menu
# 2. If "Generate all courses" is selected, process all courses sequentially
# 3. Run complete 6-stage pipeline for each course
# 4. Use non-interactive mode for all courses
# 5. Continue with next course if one fails
# 6. Display summary of successes and failures
```

**Batch processing behavior**:
- Processes all course templates found in `config/courses/`
- Runs all 6 stages for each course sequentially
- Uses `--no-interactive` flag automatically (no prompts during batch)
- Each course's output goes to `output/{course_name}/` directory
- Errors in one course don't stop processing of other courses
- Final summary shows which courses succeeded/failed

## Configuration Discovery

All scripts use consistent configuration discovery:

**Default search pattern**:
1. Command-line `--config-dir` argument (if provided)
2. `Path(__file__).parent.parent / "config"` (../config relative to script)
3. Raises error if not found

**Override example**:
```bash
uv run python3 scripts/run_pipeline.py --config-dir /custom/path/to/config
```

## Outline Discovery (Stages 04 & 05)

Both primary and secondary generation scripts automatically find outlines:

**Search order**:
1. Explicit `--outline PATH` (if provided)
2. Course-specific directory (if course_name known): `output/{course_name}/outlines/course_outline_*.json`
3. Config-specified: `{base_directory}/outlines/course_outline_*.json`
4. Project root: `output/outlines/course_outline_*.json`
5. Scripts directory: `scripts/output/outlines/course_outline_*.json`
6. All course-specific directories: `output/{course}/outlines/course_outline_*.json` (when batch processing, searches all courses)

**Selection logic**:
- Finds all matching `course_outline_*.json` files
- Selects **most recent by modification time**
- Logs selected file path for transparency

**Why multiple locations?**:
- Workspace flexibility (run from any directory)
- Development vs production separation

## Script Interdependencies

```
01_setup_environment.py
  ↓ (validates environment)
02_run_tests.py
  ↓ (ensures code quality)
03_generate_outline.py
  ↓ (creates JSON outline)
04_generate_primary.py (reads JSON outline)
  ↓ (generates session materials)
05_generate_secondary.py (reads JSON outline + primary materials)
  ↓ (synthesizes session materials)
06_website.py (reads JSON outline + all generated materials)
  ↓ (generates single HTML website)
```

**Key dependencies**:
- Stages 04, 05 & 06 **require** JSON outline from Stage 03
- Stage 05 **requires** primary materials from Stage 04
- Stage 06 **requires** primary and secondary materials from Stages 04 & 05
- All stages require valid configurations

## Error Handling

All scripts implement consistent error handling:

✅ **Clear error messages** with context  
✅ **Actionable guidance** (what to do next)  
✅ **Non-zero exit codes** on failure  
✅ **Logging to file** (in addition to console)  
✅ **Graceful degradation** where possible  
✅ **Progress tracking** for long operations  

**Common error scenarios**:

**"No outline JSON found"**:
```bash
# Solution: Generate outline first
uv run python3 scripts/03_generate_outline.py
```

**"Config directory not found"**:
```bash
# Solution: Use --config-dir or ensure config/ exists
uv run python3 scripts/run_pipeline.py --config-dir path/to/config
```

**"Ollama not running"**:
```bash
# Solution: Start Ollama or use --start-ollama
ollama serve
# OR
uv run python3 scripts/01_setup_environment.py --start-ollama
```

## Logging

All scripts use unified logging setup from `src.utils.logging_setup`:

**Features**:
- Timestamped log files in `output/logs/`
- Console output with color/formatting
- Structured log format
- Log level control via command-line
- Section headers for readability

**Log file naming**:
```
output/logs/01_setup_environment_YYYYMMDD_HHMMSS.log
output/logs/02_run_tests_YYYYMMDD_HHMMSS.log
output/logs/03_generate_outline_YYYYMMDD_HHMMSS.log
output/logs/04_generate_primary_YYYYMMDD_HHMMSS.log
output/logs/05_generate_secondary_YYYYMMDD_HHMMSS.log
output/logs/06_website_YYYYMMDD_HHMMSS.log
output/logs/run_pipeline_YYYYMMDD_HHMMSS.log
```

## Hands-Off Execution Patterns

### Pattern 1: Complete Automation
```bash
# Zero user interaction, full pipeline
uv run python3 scripts/run_pipeline.py --no-interactive

# With stage 01 options (run stage 01 separately first):
uv run python3 scripts/01_setup_environment.py --auto-install --start-ollama
uv run python3 scripts/run_pipeline.py --no-interactive --skip-setup
```

### Pattern 2: Content Generation Only
```bash
# Skip validation, just generate
uv run python3 scripts/run_pipeline.py \
  --no-interactive \
  --skip-setup \
  --skip-validation
```

### Pattern 3: Specific Modules
```bash
# Generate only modules 1-3
uv run python3 scripts/run_pipeline.py \
  --no-interactive \
  --modules 1 2 3
```

### Pattern 4: Secondary Materials Only
```bash
# Assumes outline and primary materials exist
uv run python3 scripts/05_generate_secondary.py \
  --modules 1 2 3 \
  --types application visualization
```

### Pattern 5: CI/CD Integration
```bash
# Suitable for continuous integration
uv run python3 scripts/01_setup_environment.py --auto-install
uv run python3 scripts/02_run_tests.py --no-save-output
# Only run generation if tests pass
if [ $? -eq 0 ]; then
  uv run python3 scripts/run_pipeline.py --no-interactive --skip-setup --skip-validation
fi
```

## Testing and Validation

### Quick Validation (no generation)
```bash
uv run python3 scripts/01_setup_environment.py
uv run python3 scripts/02_run_tests.py
```

### Test Generation (small scale)
```bash
# Edit config/course_config.yaml: set num_modules: 1
uv run python3 scripts/03_generate_outline.py --no-interactive
uv run python3 scripts/04_generate_primary.py --modules 1
uv run python3 scripts/05_generate_secondary.py --modules 1 --types application
```

### Dry Run (no LLM calls)
```bash
# See what would be generated without calling LLM
uv run python3 scripts/05_generate_secondary.py --modules 1 --dry-run
```

## Best Practices

✅ **Always validate first** - Run stages 01 and 02 before generation  
✅ **Use --no-interactive for automation** - Critical for hands-off execution  
✅ **Check logs for errors** - Review `output/logs/` for detailed information  
✅ **Test with small modules first** - Use `--modules 1` to test changes  
✅ **Specify outline explicitly when needed** - Use `--outline` to avoid ambiguity  
✅ **Save test outputs** - Default behavior saves to `scripts/test_reports/`  
✅ **Use --dry-run for preview** - See what would be generated  

## Complete CLI Option Reference

### All Scripts Support

| Option | Description | Example |
|--------|-------------|---------|
| `--config-dir PATH` | Custom configuration directory | `--config-dir /custom/config` |
| `--verbose` / `-v` | Enable debug logging | `--verbose` |
| `--log-level LEVEL` | Set logging level | `--log-level DEBUG` |

### Script-Specific Options

#### 01_setup_environment.py
| Option | Description | Default |
|--------|-------------|---------|
| `--auto-install` | Install dependencies with uv | No |
| `--start-ollama` | Attempt to start Ollama if not running | No |

#### 02_run_tests.py
| Option | Description | Default |
|--------|-------------|---------|
| `--skip-tests` | Skip pytest tests (validation only) | No (tests run by default) |
| `--include-ollama` | Run all tests including integration tests | No |
| `--skip-validation` | Skip config validation, only run tests | No |
| `--skip-tests` | Skip tests, only validate config | No |
| `--no-coverage` | Disable coverage reporting | Coverage enabled |
| `--no-save-output` | Don't save test output to file | Save enabled |
| `--output-dir PATH` | Custom directory for test reports | `scripts/test_reports/` |
| `--tests-path PATH` | Path to tests directory | `../tests` |
| `--stream-output` | Stream pytest output in real-time | Yes |
| `--no-stream-output` | Don't stream output, capture all at once | No |
| `--json-results` | Save structured JSON test results file | No |
| `--show-slow-tests N` | Show slowest N tests | 10 |
| `--slow-threshold SECONDS` | Threshold in seconds for 'slow' test warning | 1.0 |

#### 03_generate_outline.py
| Option | Description | Default |
|--------|-------------|---------|
| `--no-interactive` | **CRITICAL FOR AUTOMATION** - Disable interactive prompts | Interactive |
| `--course NAME` | Use specific course template from `config/courses/` | Default config |
| `--output PATH` | Custom output path for outline | Auto-generated |
| `--output-dir PATH` | Override base output directory | From config |
| `--clear-output` | Clear output directory before generation | No |

#### 04_generate_primary.py
| Option | Description | Default |
|--------|-------------|---------|
| `--all` | Generate for all modules | Yes (if no --modules) |
| `--modules ID [ID ...]` | Generate for specific module IDs | All modules |
| `--outline PATH` | Use specific outline JSON | Auto-discover latest |
| `--sessions N` | Override number of sessions per module | From outline |

#### 05_generate_secondary.py
| Option | Description | Default |
|--------|-------------|---------|
| `--all` | Generate for all modules | Yes (if no --modules) |
| `--modules ID [ID ...]` | Generate for specific module IDs | All modules |
| `--types TYPE [TYPE ...]` | Specific types to generate | All types |
| `--outline PATH` | Use specific outline JSON | Auto-discover latest |
| `--validate` | Validate generated content for quality | No |
| `--dry-run` | Show what would be generated without LLM calls | No |

#### 06_website.py
| Option | Description | Default |
|--------|-------------|---------|
| `--outline PATH` | Use specific outline JSON | Auto-discover latest |
| `--output PATH` | Custom output path for HTML file | `output/{course_name}/website/index.html` or `output/website/index.html` |
| `--open-browser` | Open generated website in default browser | No |

#### run_pipeline.py
| Option | Description | Default |
|--------|-------------|---------|
| `--skip-setup` | Skip Stage 01 | No |
| `--skip-validation` | Skip Stage 02 | No |
| `--skip-outline` | Skip Stage 03 | No |
| `--skip-primary` | Skip Stage 04 | No |
| `--skip-secondary` | Skip Stage 05 | No |
| `--skip-website` | Skip Stage 06 | No |
| `--no-interactive` | **CRITICAL FOR AUTOMATION** - Pass to stage 03 | Interactive |
| `--run-tests` | (Deprecated - no effect) Tests run automatically in stage 02 | No |
| `--modules ID [ID ...]` | Pass to stages 04 and 05 | All modules |
| `--types TYPE [TYPE ...]` | Pass to stage 05 | All types |
| `--language LANGUAGE` | Language for course content (e.g., "English", "Spanish") | From config or prompts |

## Exit Code Reference

| Script | Exit 0 | Exit 1 | Exit 2 | Exit 3 |
|--------|--------|--------|--------|--------|
| **01_setup_environment.py** | Environment ready | Critical failure | - | - |
| **02_run_tests.py** | Validation + tests passed | Validation failed | Tests failed | Pytest error |
| **03_generate_outline.py** | Outline generated | Generation failed | - | - |
| **04_generate_primary.py** | All sessions generated | One or more failed OR no outline | - | - |
| **05_generate_secondary.py** | All modules generated | One or more failed OR no outline | - | - |
| **06_website.py** | Website generated | Generation failed OR no outline | - | - |
| **run_pipeline.py** | All stages completed | One or more stages failed | - | - |

## Error Scenario Solutions

### "No outline JSON found"

**Error**: Scripts 04, 05, 06 report: "No course outline JSON found"

**Solution**:
```bash
# Generate outline first
uv run python3 scripts/03_generate_outline.py --no-interactive
```

### "Ollama not running"

**Error**: LLM generation fails with connection error

**Solution**:
```bash
# Start Ollama
ollama serve

# Or use script option
uv run python3 scripts/01_setup_environment.py --start-ollama
```

### "Config directory not found"

**Error**: `ConfigurationError: Config directory not found`

**Solution**:
```bash
# Use --config-dir to specify path
uv run python3 scripts/run_pipeline.py --config-dir /path/to/config
```

### "Tests skipped"

**Error**: All integration tests skipped

**Solution**:
```bash
# Ensure Ollama is running and model is available
ollama serve
ollama pull gemma3:4b

# Run with --include-ollama (tests run by default)
uv run python3 scripts/02_run_tests.py --include-ollama
```

## See Also

- **Complete Guide**: [../docs/PIPELINE_GUIDE.md](../docs/PIPELINE_GUIDE.md) - Pipeline documentation
- **README**: [README.md](README.md) - Human-readable script reference
- **Configuration**: [../config/AGENTS.md](../config/AGENTS.md) - How scripts use configs
- **Architecture**: [../docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) - System design
- **Formats**: [../docs/FORMATS.md](../docs/FORMATS.md) - Generated content formats


