# Course Templates

Pre-configured course templates for different subjects.

## Overview

This directory contains YAML template files that provide ready-to-use course configurations. Templates can be selected interactively during outline generation or specified via command-line flags.

## Available Templates

Templates are automatically discovered from `.yaml` files in this directory. Current templates include:

- `biology.yaml` - Introductory Biology
- `chemistry.yaml` - Introductory Chemistry
- `physics.yaml` - Introductory Physics
- `active_inference.yaml` - Active Inference: Theory and Applications (Graduate/Advanced)
- `active_inference_ai_short.yaml` - Active Inference for Generative AI (Short Course, 3 sessions)
- `active_inference_college.yaml` - Active Inference and Probabilistic Dynamical Systems (Undergraduate)
- `free_energy_principle.yaml` - Free Energy Principle: From Physics to Mind
- `tree_grafting.yaml` - Tree Grafting: Fundamentals to Advanced Techniques

## Using Templates

### Interactive Selection

When running scripts in interactive mode, you'll see a menu:

```
Available course templates:
1. biology
2. chemistry
3. physics
...
Select course template (or press Enter for default):
```

### Command-Line Selection

```bash
# Use specific template
uv run python3 scripts/03_generate_outline.py --course biology

# Full pipeline with template
uv run python3 scripts/run_pipeline.py --course chemistry
```

### Programmatic Usage

```python
from src.config.loader import ConfigLoader

loader = ConfigLoader("config")

# List available templates
courses = loader.list_available_courses()

# Load specific template
template = loader.load_course_template("biology")
```

## Template Structure

Each template follows the same structure as `course_config.yaml`:

```yaml
course:
  name: "Course Name"
  subject: "Subject Area"
  description: "Course description..."
  level: "Undergraduate Introductory"
  estimated_duration_weeks: 16
  defaults:
    num_modules: 5
    total_sessions: 15
  additional_constraints: "Optional constraints"
```

## Creating New Templates

1. Create a new `.yaml` file in this directory
2. Use a descriptive filename (e.g., `mathematics.yaml`)
3. Follow the template structure above
4. The template will be automatically discovered

## Output Organization

When using templates, generated content is organized into course-specific directories:

```
output/
├── biology/
│   ├── outlines/
│   ├── modules/
│   └── website/
├── chemistry/
│   ├── outlines/
│   ├── modules/
│   └── website/
└── ...
```

## See Also

- **[../README.md](../README.md)** - Configuration files overview
- **[../../docs/CONFIGURATION.md](../../docs/CONFIGURATION.md)** - Complete configuration guide
- **[../../src/config/README.md](../../src/config/README.md)** - ConfigLoader usage
