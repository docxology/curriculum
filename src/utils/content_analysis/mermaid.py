"""Mermaid diagram validation and cleaning utilities."""

import logging
import re
from typing import Tuple, List

logger = logging.getLogger(__name__)


def clean_mermaid_diagram(diagram: str) -> str:
    """Clean Mermaid diagram by removing code fences, style commands, linkStyle, and explanatory text.
    
    This function extracts only the actual Mermaid diagram code, removing:
    - Markdown code fences (```mermaid ... ```)
    - Style commands (style, classDef)
    - linkStyle commands (not supported in all renderers)
    - Explanatory text after the diagram code
    
    Args:
        diagram: Raw Mermaid diagram code (may include code fences, explanatory text, etc.)
        
    Returns:
        Cleaned Mermaid diagram code containing only valid diagram syntax
    """
    if not diagram:
        return ""
    
    lines = diagram.strip().split('\n')
    cleaned_lines = []
    
    # Remove code fences at start and end
    if lines and lines[0].strip().startswith('```'):
        lines = lines[1:]
    if lines and lines[-1].strip().startswith('```'):
        lines = lines[:-1]
    
    # Track if we've found the diagram start
    found_diagram_start = False
    # Track if we're in a valid Mermaid section
    in_diagram = False
    
    # Valid Mermaid diagram type declarations
    diagram_types = ('graph', 'flowchart', 'sequenceDiagram', 'classDiagram', 
                     'stateDiagram', 'erDiagram', 'gantt', 'pie', 'gitgraph')
    
    for line in lines:
        stripped = line.strip()
        
        # Skip empty lines at the start
        if not stripped and not found_diagram_start:
            continue
        
        # Check if this is a diagram type declaration
        if any(stripped.startswith(dt) for dt in diagram_types):
            found_diagram_start = True
            in_diagram = True
            cleaned_lines.append(line)
            continue
        
        # If we haven't found diagram start yet, skip non-diagram lines
        if not found_diagram_start:
            # Skip explanatory text before diagram
            if any(keyword in stripped.lower() for keyword in [
                'explanation', 'here\'s', 'here is', 'diagram', 'mermaid',
                'okay', 'alright', 'following', 'adhering'
            ]):
                continue
            # If it looks like it might be diagram code, include it
            if any(char in stripped for char in ['[', ']', '(', ')', '-->', '---', '{', '}']):
                found_diagram_start = True
                in_diagram = True
                cleaned_lines.append(line)
            continue
        
        # Once we're in the diagram, check for end markers
        if in_diagram:
            # Stop at explanatory text markers
            if stripped.startswith('**') and any(keyword in stripped.lower() for keyword in [
                'explanation', 'adherence', 'requirements', 'note', 'description'
            ]):
                break
            
            # Stop at lines that look like explanatory text (not Mermaid syntax)
            if stripped and not any([
                # Valid Mermaid syntax patterns
                any(stripped.startswith(dt) for dt in diagram_types),
                any(char in stripped for char in ['[', ']', '(', ')', '-->', '---', '==>', '{', '}']),
                stripped.startswith('    '),  # Indented (likely part of diagram)
                stripped.startswith('\t'),  # Tab-indented
                stripped.startswith('subgraph'),
                stripped.startswith('end'),
                stripped.startswith('class'),
                stripped.startswith('linkStyle'),
                stripped.startswith('style'),
                stripped.startswith('classDef'),
                # Empty lines are OK
                not stripped,
            ]):
                # This looks like explanatory text, stop here
                break
            
            # Remove style commands (case-insensitive check for robustness)
            stripped_lower = stripped.lower()
            if stripped_lower.startswith('style ') or stripped_lower.startswith('classdef '):
                continue
            
            # Remove linkStyle commands (not supported in all renderers)
            if stripped.startswith('linkStyle'):
                continue
            
            # Include valid diagram lines
            cleaned_lines.append(line)
    
    # Join and clean up
    cleaned = '\n'.join(cleaned_lines)
    
    # Remove trailing empty lines
    cleaned = cleaned.rstrip()
    
    return cleaned


def validate_mermaid_syntax(diagram: str, min_nodes: int = 3, min_connections: int = 2) -> Tuple[str, List[str]]:
    """Validate and clean Mermaid diagram syntax.
    
    Args:
        diagram: Mermaid diagram code
        min_nodes: Minimum number of nodes required (default: 3)
        min_connections: Minimum number of connections required for flowcharts (default: 2)
        
    Returns:
        Tuple of (cleaned_diagram, list_of_warnings)
    """
    warnings = []
    
    # First apply comprehensive cleaning
    cleaned = clean_mermaid_diagram(diagram)
    
    # Check if code fences were removed
    if diagram.strip().startswith('```') and not cleaned.strip().startswith('```'):
        warnings.append("Removed markdown code fence")
    
    # Check if linkStyle was removed
    if 'linkStyle' in diagram and 'linkStyle' not in cleaned:
        warnings.append("Removed linkStyle command (not supported in all renderers)")
    
    # Check if style commands were removed (check for various formats)
    # Pattern: "style" followed by whitespace and node name, or "style" at start of line
    style_pattern = re.compile(r'^\s*style\s+', re.MULTILINE | re.IGNORECASE)
    has_style_in_original = bool(style_pattern.search(diagram))
    has_style_in_cleaned = bool(style_pattern.search(cleaned))
    if has_style_in_original and not has_style_in_cleaned:
        warnings.append("Removed style command (not supported in all renderers)")
        logger.debug(f"Removed style command from diagram (original had {diagram.count('style')} style commands)")
    
    # Check if classDef commands were removed (check for various formats)
    # Pattern: "classDef" followed by whitespace, or "classDef" at start of line
    classdef_pattern = re.compile(r'^\s*classDef\s+', re.MULTILINE | re.IGNORECASE)
    has_classdef_in_original = bool(classdef_pattern.search(diagram))
    has_classdef_in_cleaned = bool(classdef_pattern.search(cleaned))
    if has_classdef_in_original and not has_classdef_in_cleaned:
        warnings.append("Removed classDef command (not supported in all renderers)")
        logger.debug(f"Removed classDef command from diagram (original had {diagram.count('classDef')} classDef commands)")
    
    # Check if explanatory text was removed
    original_lines = len([l for l in diagram.split('\n') if l.strip()])
    cleaned_lines = len([l for l in cleaned.split('\n') if l.strip()])
    if original_lines > cleaned_lines + 2:  # Allow for code fences
        warnings.append("Removed explanatory text after diagram code")
    
    lines = cleaned.strip().split('\n')
    cleaned_lines = []
    
    # Remove any remaining unsupported style commands (shouldn't be any after clean_mermaid_diagram)
    # Use case-insensitive matching to catch variations
    for line in lines:
        stripped = line.strip()
        stripped_lower = stripped.lower()
        if stripped_lower.startswith('style '):
            warnings.append(f"Removed style command: {stripped[:50]}...")
            logger.debug(f"Removed remaining style command: {stripped[:50]}")
            continue
        if stripped_lower.startswith('classdef '):
            warnings.append(f"Removed classDef command: {stripped[:50]}...")
            logger.debug(f"Removed remaining classDef command: {stripped[:50]}")
            continue
        cleaned_lines.append(line)
    
    # Check for basic syntax
    has_graph_type = any(
        line.strip().startswith(('graph', 'flowchart', 'sequenceDiagram', 'classDiagram', 'stateDiagram'))
        for line in cleaned_lines
    )
    if not has_graph_type:
        warnings.append("Missing diagram type declaration (graph/flowchart/etc.) - add 'graph TD' or 'graph LR' at the start")
    
    # Count nodes and connections
    cleaned_text = '\n'.join(cleaned_lines)
    
    # Count nodes: [NodeName], (NodeName), NodeName{...}, etc.
    node_patterns = [
        r'\[[^\]]+\]',  # [Node]
        r'\([^\)]+\)',  # (Node)
        r'\w+\s*\{',    # Node{
        r'class\s+\w+',  # class NodeName
    ]
    nodes = []
    for pattern in node_patterns:
        nodes.extend(re.findall(pattern, cleaned_text))
    
    node_count = len(nodes)
    
    # Count connections: -->, ---, ==>, etc.
    connection_patterns = [
        r'-->',  # Standard arrow
        r'==>',  # Thick arrow
        r'---',  # Line
        r'--',   # Line (shorter)
        r'==',   # Thick line
    ]
    connections = []
    for pattern in connection_patterns:
        connections.extend(re.findall(pattern, cleaned_text))
    
    connection_count = len(connections)
    
    # Check for nodes and connections
    has_connections = connection_count > 0
    if not has_connections and has_graph_type:
        warnings.append(f"No connections found in diagram (require at least {min_connections} for flowcharts - add arrows like '-->' or '==>')")
    
    # Validate node count
    if node_count < min_nodes:
        needed = min_nodes - node_count
        warnings.append(f"Only {node_count} nodes found (require at least {min_nodes}, need {needed} more - add more nodes to the diagram)")
    
    # Validate connection count (for flowcharts/graphs)
    if has_graph_type and connection_count < min_connections:
        needed = min_connections - connection_count
        warnings.append(f"Only {connection_count} connections found (require at least {min_connections}, need {needed} more - add more arrows/connections)")
    
    # Check for node text length (warn if any node text is too long)
    long_nodes = []
    for node_match in re.finditer(r'\[([^\]]+)\]|\(([^\)]+)\)', cleaned_text):
        node_text = node_match.group(1) or node_match.group(2)
        if node_text and len(node_text) > 40:
            long_nodes.append(node_text[:30] + "...")
    
    if long_nodes:
        warnings.append(f"Some node text exceeds 40 characters (keep node labels concise - found {len(long_nodes)} long nodes)")
    
    # Check for empty nodes
    empty_nodes = re.findall(r'\[\s*\]|\(\s*\)', cleaned_text)
    if empty_nodes:
        warnings.append(f"Found {len(empty_nodes)} empty nodes (add text inside brackets/parentheses)")
    
    cleaned = '\n'.join(cleaned_lines)
    return cleaned, warnings






