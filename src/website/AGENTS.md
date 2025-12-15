# Website Generation Module - For AI Agents

## Module Purpose

Generates a single, self-contained HTML website that serves as an entry point to browse all course materials (modules, sessions, and content types). The website provides an intuitive, accessible GUI for navigating course content.

## Module Structure

```
src/website/
├── __init__.py          # Module exports
├── generator.py         # WebsiteGenerator class (main orchestrator)
├── content_loader.py    # Content discovery and loading
├── templates.py         # HTML template generation (main HTML structure)
├── styles.py           # CSS styles (embedded stylesheet)
├── scripts.py          # JavaScript code (embedded interactivity)
└── AGENTS.md           # This file
```

## Key Classes

### WebsiteGenerator

Main class that orchestrates website generation.

**Location**: `generator.py`

**Key Methods**:
- `generate(outline_path, output_path)` - Generate HTML website from course outline

**Usage**:
```python
from src.config.loader import ConfigLoader
from src.website.generator import WebsiteGenerator

config_loader = ConfigLoader("config")
generator = WebsiteGenerator(config_loader)
output_path = generator.generate()
```

## Content Discovery

**`content_loader.py`** provides functions to discover and load course content:

- `scan_module_content(module_dir)` - Scans session directories for available files
- `load_markdown_content(filepath)` - Loads markdown content
- `load_mermaid_content(filepath)` - Loads Mermaid diagram content
- `get_content_types()` - Returns list of all content types

**Content Types**:
- Primary: lecture, lab, study_notes, questions, diagrams (diagram_1.mmd, diagram_2.mmd, etc.)
- Secondary: application, extension, visualization, integration, investigation, open_questions

## HTML Generation

**`templates.py`** provides HTML template generation:

- `generate_html(course_data, modules_data)` - Generates complete HTML document
- `markdown_to_html(markdown_text)` - Converts markdown to HTML using Python markdown library
- `escape_html(text)` - Escapes HTML special characters
- `_generate_navigation_html(modules_data)` - Generates navigation HTML structure

**`styles.py`** provides CSS styles:

- `get_css()` - Returns embedded CSS stylesheet with:
  - Responsive design (mobile-friendly)
  - Dark mode support
  - Print styles
  - Accessibility features

**`scripts.py`** provides JavaScript code:

- `get_javascript(modules_json)` - Returns embedded JavaScript with:
  - **Unified event delegation** for all sidebar navigation (module/session/content buttons)
  - Navigation (module/session/content type selection with proper event handling order)
  - Mermaid.js initialization and rendering
  - Search functionality
  - Dark mode toggle
  - Progress tracking
  - Table of contents generation
  - Breadcrumb navigation
  - Content loading and display

## Output Structure

The website is generated as a single HTML file:

```
output/website/index.html
```

The HTML file is self-contained with:
- Embedded CSS (responsive design, accessible)
- Embedded JavaScript (navigation, Mermaid.js integration)
- All course content embedded (markdown converted to HTML, Mermaid diagrams as text)

## Features

- **Single HTML file**: Self-contained, no external dependencies except Mermaid.js and Highlight.js CDNs
- **Responsive design**: Mobile-friendly CSS with hamburger menu
- **Accessible**: Semantic HTML5, ARIA labels, keyboard navigation, skip links, screen reader support
- **Hierarchical navigation**: Course → Module → Session → Content Type
- **Search functionality**: Client-side search across all content with highlighting (Ctrl/Cmd+K shortcut)
- **Dark mode**: Toggle with localStorage persistence, respects system preference
- **Breadcrumb navigation**: Shows current location with clickable navigation
- **Table of Contents**: Auto-generated TOC for long content with sticky sidebar
- **Progress tracking**: Tracks viewed sessions with localStorage, shows completion percentage
- **Print/Export**: Print-friendly CSS and print button for PDF export
- **Code highlighting**: Syntax highlighting with Highlight.js, copy-to-clipboard buttons
- **Loading states**: Spinners for Mermaid diagrams, graceful error handling
- **Mermaid.js integration**: Client-side diagram rendering with error handling
- **Markdown rendering**: Server-side conversion using Python markdown library
- **Graceful degradation**: Shows placeholders for missing content
- **SEO optimized**: Meta tags, Open Graph tags, structured data (JSON-LD)

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

## Usage Example

```python
from src.config.loader import ConfigLoader
from src.website.generator import WebsiteGenerator

# Initialize
config_loader = ConfigLoader("config")
generator = WebsiteGenerator(config_loader)

# Generate website (auto-discovers latest outline)
output_path = generator.generate()

# Or specify outline and output paths
output_path = generator.generate(
    outline_path=Path("output/outlines/course_outline_20241208.json"),
    output_path=Path("custom/website.html")
)
```

## Script Integration

The website generation is available as script 06:

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

## Complete API Reference

### WebsiteGenerator Class

```python
class WebsiteGenerator:
    def __init__(self, config_loader: ConfigLoader) -> None
        """Initialize with ConfigLoader."""
    
    def generate(
        self,
        outline_path: Optional[Path] = None,
        output_path: Optional[Path] = None
    ) -> Path
        """
        Generate single HTML website.
        
        Args:
            outline_path: Optional specific outline JSON path.
                        If None, auto-discovers latest outline.
            output_path: Optional output HTML file path.
                        If None, uses config default.
        
        Returns:
            Path to generated HTML file
        """
```

### Content Discovery Functions (content_loader.py)

```python
def scan_module_content(module_dir: Path) -> Dict[str, List[Path]]
    """Scan session directories for available content files."""
    # Returns: {"lecture": [Path, ...], "lab": [Path, ...], ...}

def load_markdown_content(filepath: Path) -> str
    """Load markdown content from file."""

def load_mermaid_content(filepath: Path) -> str
    """Load Mermaid diagram content from file."""

def get_content_types() -> List[str]
    """Get list of all content types."""
    # Returns: ["lecture", "lab", "study_notes", "questions", ...]
```

### HTML Generation Functions (templates.py)

```python
def generate_html(
    course_data: Dict[str, Any],
    modules_data: List[Dict[str, Any]]
) -> str
    """Generate complete HTML document."""

def markdown_to_html(markdown_text: str) -> str
    """Convert markdown to HTML using Python markdown library."""

def escape_html(text: str) -> str
    """Escape HTML special characters."""
```

### CSS Generation (styles.py)

```python
def get_css() -> str
    """Get embedded CSS stylesheet."""
    # Includes: responsive design, dark mode, print styles, accessibility
```

### JavaScript Generation (scripts.py)

```python
def get_javascript(modules_json: str) -> str
    """Get embedded JavaScript code."""
    # Includes: navigation, Mermaid.js, search, dark mode, progress tracking
```

## Content Discovery Patterns

**Primary materials** (per session):
- `lecture.md`, `lab.md`, `study_notes.md`, `questions.md`
- `diagram_1.mmd`, `diagram_2.mmd`, ... (number from config)

**Secondary materials** (per module):
- `application.md`, `extension.md`, `visualization.mmd`
- `integration.md`, `investigation.md`, `open_questions.md`

**Discovery algorithm**:
1. Load JSON outline to get module/session structure
2. For each module: scan `output/modules/module_XX_name/`
3. For each session: scan `session_YY/` directory
4. Collect all available content files
5. Generate navigation structure from discovered content

## See Also

- **README**: [README.md](README.md) - Human-readable guide with examples
- **Script Documentation**: [../../scripts/AGENTS.md](../../scripts/AGENTS.md) - Script 06 usage and CLI options
- **Configuration**: [../../config/AGENTS.md](../../config/AGENTS.md) - Output configuration
- **Root Documentation**: [../../AGENTS.md](../../AGENTS.md) - Complete repository overview
- **Test Files**: [../../tests/test_website_*.py](../../tests/) - Website generation tests

