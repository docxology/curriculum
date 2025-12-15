"""Content discovery and loading for website generation.

This module provides functions to discover and load course content files
from the output directory structure.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Primary content types (per session)
PRIMARY_CONTENT_TYPES = [
    "lecture",
    "lab",
    "study_notes",
    "questions",
]

# Secondary content types (per session)
SECONDARY_CONTENT_TYPES = [
    "application",
    "extension",
    "visualization",
    "integration",
    "investigation",
    "open_questions",
]

# All content types
ALL_CONTENT_TYPES = PRIMARY_CONTENT_TYPES + SECONDARY_CONTENT_TYPES


def get_content_types() -> List[str]:
    """Get list of all content types.
    
    Returns:
        List of content type names (primary + secondary)
    """
    return ALL_CONTENT_TYPES.copy()


def scan_module_content(module_dir: Path) -> Dict[str, Dict[str, Optional[Path]]]:
    """Scan a module directory for available content files.
    
    Scans session directories within a module and identifies which
    content files are available for each session.
    
    Args:
        module_dir: Path to module directory (e.g., output/modules/module_01_name/)
        
    Returns:
        Dictionary mapping session numbers to content file paths:
        {
            "session_01": {
                "lecture": Path(...),
                "lab": Path(...),
                "diagram_1": Path(...),
                ...
            },
            ...
        }
    """
    content_map: Dict[str, Dict[str, Optional[Path]]] = {}
    
    if not module_dir.exists():
        logger.warning(f"Module directory does not exist: {module_dir}")
        return content_map
    
    # Find all session directories
    session_dirs = sorted(module_dir.glob("session_*"))
    
    for session_dir in session_dirs:
        if not session_dir.is_dir():
            continue
        
        session_name = session_dir.name
        session_content: Dict[str, Optional[Path]] = {}
        
        # Scan for primary content types (markdown files)
        for content_type in PRIMARY_CONTENT_TYPES:
            file_path = session_dir / f"{content_type}.md"
            if file_path.exists():
                session_content[content_type] = file_path
            else:
                session_content[content_type] = None
        
        # Scan for diagram files (diagram_1.mmd, diagram_2.mmd, etc.)
        diagram_files = sorted(session_dir.glob("diagram_*.mmd"))
        for i, diagram_path in enumerate(diagram_files, start=1):
            session_content[f"diagram_{i}"] = diagram_path
        
        # If no diagrams found, set None
        if not diagram_files:
            session_content["diagram_1"] = None
        
        # Scan for secondary content types
        for content_type in SECONDARY_CONTENT_TYPES:
            # visualization is .mmd, others are .md
            ext = ".mmd" if content_type == "visualization" else ".md"
            file_path = session_dir / f"{content_type}{ext}"
            if file_path.exists():
                session_content[content_type] = file_path
            else:
                session_content[content_type] = None
        
        content_map[session_name] = session_content
    
    return content_map


def load_markdown_content(filepath: Path) -> str:
    """Load markdown content from a file.
    
    Args:
        filepath: Path to markdown file
        
    Returns:
        Markdown content as string
        
    Raises:
        FileNotFoundError: If file doesn't exist
        IOError: If file cannot be read
    """
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    try:
        content = filepath.read_text(encoding='utf-8')
        logger.debug(f"Loaded markdown content from: {filepath}")
        return content
    except Exception as e:
        raise IOError(f"Failed to read file {filepath}: {e}")


def load_mermaid_content(filepath: Path) -> str:
    """Load Mermaid diagram content from a file.
    
    Args:
        filepath: Path to .mmd file
        
    Returns:
        Mermaid diagram content as string
        
    Raises:
        FileNotFoundError: If file doesn't exist
        IOError: If file cannot be read
    """
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    try:
        content = filepath.read_text(encoding='utf-8')
        logger.debug(f"Loaded Mermaid content from: {filepath}")
        return content
    except Exception as e:
        raise IOError(f"Failed to read file {filepath}: {e}")







