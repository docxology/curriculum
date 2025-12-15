"""HTML template generation for website.

This module provides functions to generate the complete HTML structure
for the course website, including embedded CSS and JavaScript.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import markdown

from src.website import scripts
from src.website import styles

logger = logging.getLogger(__name__)


def markdown_to_html(markdown_text: str) -> str:
    """Convert markdown text to HTML.
    
    Args:
        markdown_text: Markdown content
        
    Returns:
        HTML content
    """
    try:
        html = markdown.markdown(
            markdown_text,
            extensions=['extra', 'codehilite', 'tables', 'fenced_code']
        )
        return html
    except Exception as e:
        logger.warning(f"Markdown conversion failed: {e}")
        # Return as preformatted text if conversion fails
        return f"<pre>{markdown_text}</pre>"


def escape_html(text: str) -> str:
    """Escape HTML special characters.
    
    Args:
        text: Text to escape
        
    Returns:
        Escaped text
    """
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#x27;"))


def generate_html(
    course_data: Dict[str, Any],
    modules_data: List[Dict[str, Any]],
    generation_timestamp: Optional[str] = None
) -> str:
    """Generate complete HTML website.
    
    Args:
        course_data: Course metadata dictionary
        modules_data: List of module data dictionaries with content
        generation_timestamp: Optional timestamp string for generation time
        
    Returns:
        Complete HTML document as string
    """
    if generation_timestamp is None:
        generation_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    course_name = course_data.get("name", "Course")
    course_level = course_data.get("level", "")
    course_description = course_data.get("description", "")
    
    # Serialize modules data for JavaScript
    modules_json = json.dumps(modules_data, indent=2)
    
    # Generate meta description for SEO
    meta_description = course_description[:160] if course_description else f"Course materials for {course_name}"
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escape_html(course_name)} - Course Materials</title>
    <meta name="description" content="{escape_html(meta_description)}">
    <meta property="og:title" content="{escape_html(course_name)} - Course Materials">
    <meta property="og:description" content="{escape_html(meta_description)}">
    <meta property="og:type" content="website">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/default.min.css">
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "Course",
        "name": "{escape_html(course_name)}",
        "description": "{escape_html(course_description)}",
        "educationalLevel": "{escape_html(course_level)}"
    }}
    </script>
    <style>
{styles.get_css()}
    </style>
</head>
<body>
    <a href="#mainContent" class="skip-link">Skip to main content</a>
    <header>
        <div class="header-content">
            <div class="header-top">
                <h1>{escape_html(course_name)}</h1>
                <div class="header-controls">
                    <div class="search-container">
                        <input type="search" id="searchInput" class="search-input" placeholder="Search (Ctrl+K)" aria-label="Search course content">
                        <button class="search-button" id="searchButton" aria-label="Search">🔍</button>
                        <div class="search-results" id="searchResults"></div>
                    </div>
                    <button class="dark-mode-toggle" id="darkModeToggle" aria-label="Toggle dark mode">🌙</button>
                    <button class="print-button" id="printButton" aria-label="Print">🖨️</button>
                </div>
            </div>
            {f'<p class="course-level">{escape_html(course_level)}</p>' if course_level else ''}
            {f'<p class="course-description">{escape_html(course_description)}</p>' if course_description else ''}
        </div>
    </header>
    
    <div class="container">
        <nav class="sidebar" id="sidebar" aria-label="Course navigation">
            <div class="nav-header">
                <h2>Modules</h2>
                <button class="nav-toggle" id="navToggle" aria-label="Toggle navigation" aria-expanded="true">
                    <span>☰</span>
                </button>
            </div>
            <ul class="module-list" id="moduleList">
{_generate_navigation_html(modules_data)}
            </ul>
        </nav>
        
        <main class="content" id="mainContent" role="main">
            <div class="welcome-screen" id="welcomeScreen">
                <h2>Welcome</h2>
                <p>Select a module and session from the sidebar to view course materials.</p>
                {f'<p class="metadata">Generated: {escape_html(generation_timestamp)}</p>' if generation_timestamp else ''}
            </div>
            
            <div class="content-view" id="contentView" style="display: none;">
                <div class="content-header">
                    <button class="back-button" id="backButton" aria-label="Go back">← Back</button>
                    <nav class="breadcrumbs" id="breadcrumbs" aria-label="Breadcrumb navigation"></nav>
                    <h2 id="contentTitle"></h2>
                    <div class="content-actions">
                        <button class="toc-toggle" id="tocToggle" aria-label="Toggle table of contents">📑 TOC</button>
                    </div>
                </div>
                <div class="content-wrapper">
                    <aside class="table-of-contents" id="tableOfContents" style="display: none;">
                        <h3>Table of Contents</h3>
                        <ul id="tocList"></ul>
                    </aside>
                    <div class="content-body" id="contentBody"></div>
                </div>
                <div class="progress-indicator" id="progressIndicator" aria-live="polite" aria-atomic="true"></div>
            </div>
        </main>
    </div>
    
    <footer>
        <p>Generated on {escape_html(generation_timestamp)}</p>
    </footer>
    
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <script>
{scripts.get_javascript(modules_json)}
    </script>
</body>
</html>"""
    
    return html


def _generate_navigation_html(modules_data: List[Dict[str, Any]]) -> str:
    """Generate navigation HTML for modules and sessions.
    
    Args:
        modules_data: List of module data dictionaries
        
    Returns:
        HTML string for navigation
    """
    html_parts = []
    
    for module in modules_data:
        module_id = module.get("module_id", 0)
        module_name = module.get("module_name", f"Module {module_id}")
        sessions = module.get("sessions", [])
        
        html_parts.append('                <li class="module-item">')
        html_parts.append(f'                    <button class="module-button" data-module-id="{module_id}" aria-expanded="false">')
        html_parts.append(f'                        <span class="module-name">{escape_html(module_name)}</span>')
        html_parts.append('                        <span class="expand-icon">▼</span>')
        html_parts.append('                    </button>')
        html_parts.append('                    <ul class="session-list" style="display: none;">')
        
        for session in sessions:
            session_num = session.get("session_number", 0)
            session_title = session.get("session_title", f"Session {session_num}")
            session_key = f"session_{session_num:02d}"
            
            html_parts.append('                        <li class="session-item">')
            html_parts.append(f'                            <button class="session-button" data-module-id="{module_id}" data-session="{session_key}" aria-expanded="false">')
            html_parts.append(f'                                <span class="session-name">{escape_html(session_title)}</span>')
            html_parts.append('                                <span class="expand-icon">▼</span>')
            html_parts.append('                            </button>')
            html_parts.append('                            <ul class="content-list" style="display: none;">')
            
            # Add content type buttons
            content_types = [
                ("lecture", "Lecture"),
                ("lab", "Lab"),
                ("study_notes", "Study Notes"),
                ("questions", "Questions"),
                ("application", "Application"),
                ("extension", "Extension"),
                ("visualization", "Visualization"),
                ("integration", "Integration"),
                ("investigation", "Investigation"),
                ("open_questions", "Open Questions"),
            ]
            
            # Check which content types are available
            session_content = session.get("content", {})
            for content_type, display_name in content_types:
                # Check for diagrams separately
                if content_type == "visualization":
                    # Check for visualization.mmd
                    has_content = session_content.get("visualization") is not None
                elif content_type.startswith("diagram"):
                    continue  # Handle diagrams separately
                else:
                    has_content = session_content.get(content_type) is not None
                
                if has_content:
                    html_parts.append('                                <li>')
                    html_parts.append(f'                                    <button class="content-button" data-module-id="{module_id}" data-session="{session_key}" data-content-type="{content_type}">')
                    html_parts.append(f'                                        {escape_html(display_name)}')
                    html_parts.append('                                    </button>')
                    html_parts.append('                                </li>')
            
            # Add diagram buttons
            diagram_count = 0
            for key in sorted(session_content.keys()):
                if key.startswith("diagram_"):
                    diagram_count += 1
                    html_parts.append('                                <li>')
                    html_parts.append(f'                                    <button class="content-button" data-module-id="{module_id}" data-session="{session_key}" data-content-type="{key}">')
                    html_parts.append(f'                                        Diagram {diagram_count}')
                    html_parts.append('                                    </button>')
                    html_parts.append('                                </li>')
            
            html_parts.append('                            </ul>')
            html_parts.append('                        </li>')
        
        html_parts.append('                    </ul>')
        html_parts.append('                </li>')
    
    return "\n".join(html_parts)
