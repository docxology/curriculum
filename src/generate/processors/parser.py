"""Parser for course outlines.

This module provides functionality to parse generated course outlines
into structured data for further processing.
"""

import logging
import re
from typing import Dict, List, Any, Optional


logger = logging.getLogger(__name__)


class OutlineParser:
    """Parse course outlines into structured data.
    
    This class takes a markdown outline and extracts modules, subtopics,
    learning objectives, and metadata.
    
    Attributes:
        outline_text: Raw outline text to parse
    """
    
    def __init__(self, outline_text: str):
        """Initialize the parser.
        
        Args:
            outline_text: Markdown outline text
        """
        self.outline_text = outline_text
        self._modules: Optional[List[Dict[str, Any]]] = None
        self._metadata: Optional[Dict[str, str]] = None
        
        logger.debug(f"Initialized OutlineParser with {len(outline_text)} characters")
        
    def parse_modules(self) -> List[Dict[str, Any]]:
        """Parse modules from the outline.
        
        Returns:
            List of module dictionaries with title and content
        """
        if self._modules is not None:
            return self._modules
            
        modules = []
        
        # Split outline by level-2 headings (## Module)
        # Match lines starting with ## 
        pattern = r'^##\s+(.+)$'
        lines = self.outline_text.split('\n')
        
        current_module = None
        current_content = []
        
        for line in lines:
            match = re.match(pattern, line)
            if match:
                # Save previous module if exists
                if current_module:
                    modules.append({
                        'title': current_module,
                        'content': '\n'.join(current_content).strip()
                    })
                    
                # Start new module
                current_module = match.group(1).strip()
                current_content = []
            elif current_module:
                # Add to current module content
                current_content.append(line)
                
        # Don't forget the last module
        if current_module:
            modules.append({
                'title': current_module,
                'content': '\n'.join(current_content).strip()
            })
            
        self._modules = modules
        logger.info(f"Parsed {len(modules)} modules from outline")
        return modules
        
    def extract_metadata(self) -> Dict[str, str]:
        """Extract metadata from outline header.
        
        Returns:
            Dictionary of metadata key-value pairs
        """
        if self._metadata is not None:
            return self._metadata
            
        metadata = {}
        lines = self.outline_text.split('\n')
        
        # Look for **Key**: Value patterns
        pattern = r'\*\*(.+?)\*\*:\s*(.+?)$'
        
        for line in lines[:20]:  # Only check first 20 lines
            match = re.match(pattern, line.strip())
            if match:
                key = match.group(1).strip().lower()
                value = match.group(2).strip()
                metadata[key] = value
                
        self._metadata = metadata
        logger.debug(f"Extracted metadata: {metadata}")
        return metadata
        
    def extract_subtopics(self, module_content: str) -> List[str]:
        """Extract subtopics from module content.
        
        Args:
            module_content: Content text of a module
            
        Returns:
            List of subtopics
        """
        subtopics = []
        
        # Look for lines starting with - or * (bullet points)
        lines = module_content.split('\n')
        in_subtopics_section = False
        
        for line in lines:
            line = line.strip()
            
            # Check if we're in the subtopics section
            if 'subtopic' in line.lower():
                in_subtopics_section = True
                continue
            elif 'objective' in line.lower() or 'learning' in line.lower():
                in_subtopics_section = False
                continue
                
            # Extract bullet points when in subtopics section
            if in_subtopics_section and (line.startswith('-') or line.startswith('*')):
                topic = line.lstrip('-*').strip()
                if topic:
                    subtopics.append(topic)
                    
        return subtopics
        
    def extract_objectives(self, module_content: str) -> List[str]:
        """Extract learning objectives from module content.
        
        Args:
            module_content: Content text of a module
            
        Returns:
            List of learning objectives
        """
        objectives = []
        
        lines = module_content.split('\n')
        in_objectives_section = False
        
        for line in lines:
            line = line.strip()
            
            # Check if we're in the objectives section
            if 'objective' in line.lower() or 'learning' in line.lower():
                in_objectives_section = True
                continue
            elif in_objectives_section and line.startswith('#'):
                # Hit another section
                in_objectives_section = False
                continue
                
            # Extract bullet points when in objectives section
            if in_objectives_section and (line.startswith('-') or line.startswith('*')):
                objective = line.lstrip('-*').strip()
                if objective:
                    objectives.append(objective)
                    
        return objectives
        
    def get_module_count(self) -> int:
        """Get the number of modules in the outline.
        
        Returns:
            Number of modules
        """
        modules = self.parse_modules()
        return len(modules)
        
    def get_module_by_index(self, index: int) -> Dict[str, Any]:
        """Get a specific module by index.
        
        Args:
            index: Module index (0-based)
            
        Returns:
            Module dictionary
            
        Raises:
            IndexError: If index is out of range
        """
        modules = self.parse_modules()
        if index < 0 or index >= len(modules):
            raise IndexError(f"Module index {index} out of range (0-{len(modules)-1})")
        return modules[index]
        
    def get_course_title(self) -> Optional[str]:
        """Extract course title from outline.
        
        Returns:
            Course title or None if not found
        """
        lines = self.outline_text.split('\n')
        
        # Look for level-1 heading
        for line in lines[:10]:  # Check first 10 lines
            if line.startswith('# '):
                title = line.lstrip('#').strip()
                # Remove "- Course Outline" suffix if present
                title = re.sub(r'\s*-\s*Course Outline\s*$', '', title)
                return title
                
        return None
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert parsed outline to dictionary.
        
        Returns:
            Dictionary with metadata and modules
        """
        modules = self.parse_modules()
        
        # Enhance modules with extracted subtopics and objectives
        enhanced_modules = []
        for module in modules:
            enhanced = {
                'title': module['title'],
                'content': module['content'],
                'subtopics': self.extract_subtopics(module['content']),
                'objectives': self.extract_objectives(module['content'])
            }
            enhanced_modules.append(enhanced)
            
        result = {
            'title': self.get_course_title(),
            'metadata': self.extract_metadata(),
            'modules': enhanced_modules
        }
        
        return result

