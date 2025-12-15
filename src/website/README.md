# Website Generation

Single HTML website generation for browsing all course materials.

## Files

- `generator.py` - `WebsiteGenerator` class (main orchestrator)
- `content_loader.py` - Content discovery and loading functions
- `templates.py` - HTML template generation
- `styles.py` - CSS stylesheet generation
- `scripts.py` - JavaScript code generation

## Overview

This module generates a single, self-contained HTML website that serves as an entry point to browse all course materials. The website provides an intuitive, accessible GUI for navigating course content organized by module, session, and content type.

## Key Features

- **Single HTML file**: Self-contained, no external dependencies except CDN resources
- **Responsive design**: Mobile-friendly with hamburger menu
- **Accessible**: Semantic HTML5, ARIA labels, keyboard navigation
- **Hierarchical navigation**: Course → Module → Session → Content Type
- **Search functionality**: Client-side search with highlighting (Ctrl/Cmd+K)
- **Dark mode**: Toggle with localStorage persistence
- **Mermaid.js integration**: Client-side diagram rendering
- **Markdown rendering**: Server-side conversion to HTML
- **Progress tracking**: Tracks viewed sessions with localStorage

## Usage

### Basic Usage

```python
from src.config.loader import ConfigLoader
from src.website.generator import WebsiteGenerator

# Initialize
config_loader = ConfigLoader("config")
generator = WebsiteGenerator(config_loader)

# Generate website (auto-discovers latest outline)
output_path = generator.generate()

# Opens at: output/website/index.html
```

### With Specific Outline

```python
from pathlib import Path

# Use specific outline file
output_path = generator.generate(
    outline_path=Path("output/outlines/course_outline_20241208.json"),
    output_path=Path("custom/website.html")
)
```

### Via Script

```bash
# Generate website (auto-discovers latest outline)
uv run python3 scripts/06_website.py

# Use specific outline
uv run python3 scripts/06_website.py --outline path/to/outline.json

# Custom output path
uv run python3 scripts/06_website.py --output custom/website.html

# Open in browser after generation
uv run python3 scripts/06_website.py --open-browser
```

## WebsiteGenerator Class

Main orchestrator for website generation.

### Methods

**generate(outline_path, output_path)**
Generate HTML website from course outline.

- `outline_path`: Optional specific outline JSON path (auto-discovers if None)
- `output_path`: Optional output HTML file path (uses config default if None)
- Returns: Path to generated HTML file

## Content Discovery

The website automatically discovers all available content:

**Primary Materials** (per session):
- `lecture.md` - Comprehensive lectures
- `lab.md` - Laboratory exercises
- `study_notes.md` - Concise summaries
- `questions.md` - Assessment questions
- `diagram_1.mmd`, `diagram_2.mmd`, ... - Mermaid diagrams

**Secondary Materials** (per module):
- `application.md` - Real-world applications
- `extension.md` - Advanced topics
- `visualization.mmd` - Additional diagrams
- `integration.md` - Cross-module connections
- `investigation.md` - Research questions
- `open_questions.md` - Scientific debates

## Output Structure

```
output/website/
  index.html       # Single self-contained HTML file
```

The HTML file includes:
- Embedded CSS (responsive, accessible, dark mode)
- Embedded JavaScript (navigation, search, Mermaid.js integration)
- All course content (markdown converted to HTML, diagrams as text)
- Mermaid.js and Highlight.js via CDN

## Integration

**Uses existing infrastructure**:
- `ConfigLoader` for outline discovery (same pattern as scripts 04/05)
- `output_config.yaml` for output directory configuration
- Same outline discovery logic (multiple locations, most recent)
- Same logging setup (`src.utils.logging_setup`)

**Dependencies**:
- Python `markdown` package (for markdown-to-HTML conversion)
- Mermaid.js CDN (for client-side diagram rendering)
- Highlight.js CDN (for code syntax highlighting)

## Features in Detail

### Navigation

- **Sidebar navigation**: Module → Session → Content Type hierarchy
- **Breadcrumb navigation**: Shows current location with clickable path
- **Table of Contents**: Auto-generated TOC for long content with sticky sidebar
- **Keyboard shortcuts**: Ctrl/Cmd+K for search, arrow keys for navigation

### Search

- **Client-side search**: Searches across all content
- **Highlighting**: Highlights search terms in results
- **Keyboard shortcut**: Ctrl/Cmd+K to open search
- **Real-time filtering**: Filters navigation as you type

### Accessibility

- **Semantic HTML5**: Proper heading hierarchy, landmarks
- **ARIA labels**: Screen reader support
- **Keyboard navigation**: Full keyboard accessibility
- **Skip links**: Skip to main content
- **Focus indicators**: Clear focus states

### Responsive Design

- **Mobile-friendly**: Hamburger menu for mobile
- **Flexible layout**: Adapts to screen size
- **Touch-friendly**: Large touch targets
- **Print styles**: Print-friendly CSS included

### Dark Mode

- **Toggle button**: Easy dark/light mode switching
- **Persistence**: Remembers preference in localStorage
- **System preference**: Respects system dark mode setting
- **Smooth transitions**: Animated theme changes

## Troubleshooting

### "No outline JSON found"

Generate outline first:
```bash
uv run python3 scripts/03_generate_outline.py --no-interactive
```

### "No modules found"

Ensure outline contains modules. Check outline JSON structure.

### Missing content

Run stages 04 and 05 to generate content:
```bash
uv run python3 scripts/04_generate_primary.py
uv run python3 scripts/05_generate_secondary.py
```

### Diagrams not rendering

- Check browser console for Mermaid.js errors
- Verify Mermaid syntax in diagram files
- Ensure internet connection (Mermaid.js loads from CDN)

### Search not working

- Check browser console for JavaScript errors
- Verify all content loaded correctly
- Try refreshing the page

## Testing

Tests in `tests/test_website_*.py`:
- `test_website_generator.py` - WebsiteGenerator class
- `test_website_content_loader.py` - Content discovery
- `test_website_templates.py` - HTML template generation
- `test_website_scripts.py` - JavaScript code
- `test_website_scripts_interaction.py` - JavaScript interactions
- `test_website_styles.py` - CSS styles

Run tests:
```bash
uv run pytest tests/test_website_*.py -v
```

## See Also

- **For AI Agents**: [AGENTS.md](AGENTS.md) - Complete API reference
- **Script Documentation**: [../../scripts/AGENTS.md](../../scripts/AGENTS.md) - Script 06 usage
- **Configuration**: [../../config/AGENTS.md](../../config/AGENTS.md) - Output configuration
- **Pipeline Guide**: [../../docs/PIPELINE_GUIDE.md](../../docs/PIPELINE_GUIDE.md) - Complete pipeline documentation
- **Root Documentation**: [../../AGENTS.md](../../AGENTS.md) - Complete repository overview





