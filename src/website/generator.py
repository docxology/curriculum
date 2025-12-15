"""Website generator for educational course materials.

This module provides the WebsiteGenerator class that orchestrates the
generation of a single HTML website from course content.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.config.loader import ConfigLoader
from src.utils.helpers import ensure_directory, slugify
from src.website import content_loader
from src.website import templates

logger = logging.getLogger(__name__)


class WebsiteGenerator:
    """Generates a single HTML website from course materials.
    
    This class loads course outlines, discovers content files, converts
    markdown to HTML, and generates a self-contained HTML website.
    """
    
    def __init__(self, config_loader: ConfigLoader):
        """Initialize the website generator.
        
        Args:
            config_loader: Configuration loader instance
        """
        self.config_loader = config_loader
        logger.debug("Initialized WebsiteGenerator")
    
    def generate(
        self,
        outline_path: Optional[Path] = None,
        output_path: Optional[Path] = None
    ) -> Path:
        """Generate the website HTML file.
        
        Args:
            outline_path: Optional path to specific outline JSON file
            output_path: Optional path for output HTML file
            
        Returns:
            Path to generated HTML file
            
        Raises:
            FileNotFoundError: If outline not found
            ValueError: If no modules found in outline
        """
        # Find outline if not provided
        if outline_path is None:
            outline_path = self.config_loader._find_latest_outline_json()
            if not outline_path:
                raise FileNotFoundError(
                    "No outline JSON found. Generate an outline first: "
                    "uv run python3 scripts/03_generate_outline.py"
                )
        
        logger.info(f"Loading outline from: {outline_path}")
        
        # Load outline JSON
        with open(outline_path, 'r', encoding='utf-8') as f:
            outline_data = json.load(f)
        
        course_metadata = outline_data.get("course_metadata", {})
        modules = outline_data.get("modules", [])
        
        if not modules:
            raise ValueError("No modules found in outline")
        
        logger.info(f"Found {len(modules)} modules in outline")
        
        # Extract course name from outline metadata
        course_metadata = outline_data.get('course_metadata', {})
        course_name = course_metadata.get('course_template')
        
        # Get output directory from config (always uses course-specific subfolder structure)
        # If course_name is None, get_output_paths() derives it from default course config
        output_config = self.config_loader.get_output_paths(course_name)
        # Get the actual course name used (may be derived from default config)
        actual_course_name = output_config.get('course_name', 'default')
        logger.info(f"Using course-specific output directory: output/{actual_course_name}/")
        base_dir = Path(output_config.get('base_directory', 'output'))
        directories = output_config.get('directories', {})
        website_dir = Path(directories.get('website', 'website'))
        
        # Determine output path
        if output_path is None:
            output_path = website_dir / "index.html"
        
        # Ensure output directory exists
        ensure_directory(output_path.parent)
        
        # Get base modules directory
        modules_dir = Path(directories.get('modules', 'modules'))
        
        # Process modules and load content
        modules_data = []
        for module in modules:
            module_data = self._process_module(module, modules_dir)
            modules_data.append(module_data)
        
        # Generate HTML
        logger.info("Generating HTML website...")
        html_content = templates.generate_html(
            course_data=course_metadata,
            modules_data=modules_data
        )
        
        # Write HTML file
        output_path.write_text(html_content, encoding='utf-8')
        logger.info(f"Website generated: {output_path.resolve()}")
        
        return output_path
    
    def _process_module(
        self,
        module: Dict[str, Any],
        modules_dir: Path
    ) -> Dict[str, Any]:
        """Process a single module and load its content.
        
        Args:
            module: Module dictionary from outline
            modules_dir: Base directory for modules
            
        Returns:
            Module data dictionary with loaded content
        """
        module_id = module.get("module_id", 0)
        module_name = module.get("module_name", f"Module {module_id}")
        sessions = module.get("sessions", [])
        
        logger.debug(f"Processing module {module_id}: {module_name}")
        
        # Create module slug for directory name
        module_slug = slugify(f"module_{module_id:02d}_{module_name}")
        module_dir = modules_dir / module_slug
        
        # Scan module content
        module_content_map = content_loader.scan_module_content(module_dir)
        
        # Process sessions
        processed_sessions = []
        for session in sessions:
            session_num = session.get("session_number", 0)
            session_key = f"session_{session_num:02d}"
            
            # Get content for this session
            session_content_map = module_content_map.get(session_key, {})
            
            # Load and convert content
            session_content = {}
            for content_type, file_path in session_content_map.items():
                if file_path is None:
                    continue
                
                try:
                    if content_type.startswith("diagram_") or content_type == "visualization":
                        # Mermaid diagram - keep as raw text for client-side rendering
                        mermaid_content = content_loader.load_mermaid_content(file_path)
                        session_content[content_type] = mermaid_content
                    else:
                        # Markdown content - convert to HTML
                        markdown_content = content_loader.load_markdown_content(file_path)
                        html_content = templates.markdown_to_html(markdown_content)
                        session_content[content_type] = html_content
                except Exception as e:
                    logger.warning(
                        f"Failed to load {content_type} for module {module_id}, "
                        f"session {session_num}: {e}"
                    )
                    session_content[content_type] = None
            
            # Create processed session data
            processed_session = {
                "session_number": session_num,
                "session_title": session.get("session_title", f"Session {session_num}"),
                "subtopics": session.get("subtopics", []),
                "learning_objectives": session.get("learning_objectives", []),
                "key_concepts": session.get("key_concepts", []),
                "content": session_content
            }
            processed_sessions.append(processed_session)
        
        # Create processed module data
        processed_module = {
            "module_id": module_id,
            "module_name": module_name,
            "module_description": module.get("module_description", ""),
            "sessions": processed_sessions
        }
        
        return processed_module







