"""Utility functions for the educational course generator.

This module provides common utility functions for file I/O, text processing,
system checks, and other helper operations.
"""

import logging
import re
import subprocess
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union

import requests


logger = logging.getLogger(__name__)


def ensure_directory(path: Union[str, Path]) -> Path:
    """Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Directory path
        
    Returns:
        Path object for the directory
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Ensured directory exists: {path}")
    return path


def slugify(text: str) -> str:
    """Convert text to a URL-friendly slug.
    
    Normalizes Unicode characters to ASCII equivalents (e.g., é→e, ü→u)
    and replaces non-alphanumeric characters with underscores.
    
    Args:
        text: Text to slugify
        
    Returns:
        Slugified text (lowercase, underscores, no special chars)
    """
    # Normalize Unicode characters to ASCII equivalents
    # NFD = decompose accented characters (é → e + ´)
    # Then encode to ASCII, ignoring non-ASCII characters
    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    
    # Convert to lowercase
    text = text.lower()
    
    # Replace non-alphanumeric characters with underscores
    text = re.sub(r'[^a-z0-9]+', '_', text)
    
    # Remove leading/trailing underscores
    text = text.strip('_')
    
    return text


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename by removing/replacing invalid characters.
    
    Prevents directory traversal attacks and removes filesystem-unsafe characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename safe for filesystem use
    """
    # Replace path separators and invalid filename characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Replace dots to prevent path traversal (..)
    # Allow dots before file extensions but not consecutive dots
    filename = re.sub(r'\.\.+', '_', filename)
    
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    
    # Remove multiple consecutive underscores
    filename = re.sub(r'_+', '_', filename)
    
    return filename


def save_markdown(filepath: Union[str, Path], content: str) -> None:
    """Save markdown content to a file.
    
    Args:
        filepath: Path to save the file
        content: Markdown content to save
    """
    filepath = Path(filepath)
    
    # Ensure parent directory exists
    ensure_directory(filepath.parent)
    
    # Write content
    filepath.write_text(content, encoding='utf-8')
    logger.info(f"Saved markdown file: {filepath}")


def load_markdown(filepath: Union[str, Path]) -> str:
    """Load markdown content from a file.
    
    Args:
        filepath: Path to the markdown file
        
    Returns:
        Markdown content as string
        
    Raises:
        FileNotFoundError: If file doesn't exist
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
        
    content = filepath.read_text(encoding='utf-8')
    logger.debug(f"Loaded markdown file: {filepath}")
    return content


def format_timestamp(dt: datetime = None) -> str:
    """Format a datetime as a timestamp string.
    
    Args:
        dt: Datetime to format (defaults to current time)
        
    Returns:
        Formatted timestamp string (YYYYMMDD_HHMMSS)
    """
    if dt is None:
        dt = datetime.now()
        
    return dt.strftime("%Y%m%d_%H%M%S")


def format_module_filename(module_id: int, module_name: str, suffix: str = "") -> str:
    """Format a standardized filename for a module.
    
    Args:
        module_id: Module ID number
        module_name: Module name
        suffix: Optional suffix (e.g., '_lecture', '_questions')
        
    Returns:
        Formatted filename
    """
    slug = slugify(module_name)
    filename = f"module_{module_id:02d}_{slug}{suffix}.md"
    return sanitize_filename(filename)


def count_words(text: str) -> int:
    """Count words in text.
    
    Args:
        text: Text to count words in
        
    Returns:
        Number of words
    """
    # Split on whitespace and filter empty strings
    words = [w for w in text.split() if w]
    return len(words)


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length (including suffix)
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
        
    return text[:max_length - len(suffix)] + suffix


# System and environment utilities

def run_cmd_capture(cmd: Sequence[str], cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
    """Run a command and capture output.
    
    Args:
        cmd: Command and arguments as sequence
        cwd: Optional working directory
        
    Returns:
        CompletedProcess with returncode, stdout, stderr
    """
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        check=False,
        capture_output=True,
        text=True,
    )


def ollama_is_running(api_url: str = "http://localhost:11434/api/version") -> bool:
    """Check if Ollama service is reachable.
    
    Args:
        api_url: Ollama API endpoint to check
        
    Returns:
        True if Ollama is running and responding, False otherwise
    """
    try:
        resp = requests.get(api_url, timeout=5)
        return resp.status_code == 200
    except Exception:
        return False


def ensure_model_available(model_name: str) -> bool:
    """Check if a specific Ollama model is available.
    
    Args:
        model_name: Name of the model to check (e.g., 'ministral-3:3b', 'llama3')
        
    Returns:
        True if model is available, False otherwise
    """
    result = run_cmd_capture(["ollama", "list"])
    if result.returncode != 0:
        return False
    return model_name in (result.stdout or "")


def ensure_uv_available() -> bool:
    """Check if uv package manager is installed.
    
    Returns:
        True if uv is available, False otherwise
    """
    result = run_cmd_capture(["uv", "--version"])
    return result.returncode == 0


def check_ollama_gpu_usage() -> Dict[str, Any]:
    """Check if Ollama is using GPU acceleration.
    
    Parses the output of `ollama ps` to determine if models are loaded
    and whether they're using GPU (Metal on macOS) or CPU.
    
    Returns:
        Dict with keys:
        - using_gpu: bool (True if any model using GPU)
        - processor_info: str (e.g., "100% GPU", "100% CPU", "48%/52% CPU/GPU")
        - models_loaded: List[str] (list of loaded model names)
        - details: List[Dict] (per-model processor info with 'model' and 'processor' keys)
    """
    
    result = run_cmd_capture(["ollama", "ps"])
    if result.returncode != 0:
        return {
            "using_gpu": False,
            "processor_info": "Unknown (ollama ps failed)",
            "models_loaded": [],
            "details": []
        }
    
    # Parse output: NAME, ID, SIZE, PROCESSOR, UNTIL
    lines = result.stdout.strip().split("\n") if result.stdout else []
    if len(lines) <= 1:
        return {
            "using_gpu": False,
            "processor_info": "No models loaded",
            "models_loaded": [],
            "details": []
        }
    
    models_loaded: List[str] = []
    details: List[Dict[str, str]] = []
    has_gpu = False
    
    for line in lines[1:]:  # Skip header
        parts = line.split()
        if len(parts) >= 4:
            model_name = parts[0]
            # Format: NAME, ID, SIZE (may be "4.2 GB"), PROCESSOR (may be "100% GPU"), CONTEXT, UNTIL
            # Processor column contains percentage and GPU/CPU, find it by looking for "%" followed by "GPU" or "CPU"
            processor = "Unknown"
            processor_parts = []
            found_percent = False
            
            for i, part in enumerate(parts):
                if "%" in part:
                    found_percent = True
                    processor_parts.append(part)
                    # Next part should be GPU/CPU or CPU/GPU
                    if i + 1 < len(parts):
                        next_part = parts[i + 1]
                        if "GPU" in next_part or "CPU" in next_part:
                            processor_parts.append(next_part)
                            # Check for mixed format (e.g., "48%/52% CPU/GPU")
                            if i + 2 < len(parts) and "/" in parts[i + 2]:
                                processor_parts.append(parts[i + 2])
                    break
            
            if processor_parts:
                processor = " ".join(processor_parts)
            elif len(parts) >= 5:
                # Fallback: try to find GPU/CPU in the line
                line_lower = line.lower()
                if "gpu" in line_lower or "cpu" in line_lower:
                    # Try to extract processor info from the line
                    proc_match = re.search(r'(\d+%/?\d*%?\s*(?:CPU/)?GPU|CPU)', line, re.IGNORECASE)
                    if proc_match:
                        processor = proc_match.group(1)
            
            models_loaded.append(model_name)
            details.append({"model": model_name, "processor": processor})
            
            # Check if GPU is mentioned and has a percentage > 0
            if "GPU" in processor.upper():
                # Extract GPU percentage: look for patterns like "100% GPU" or "48%/52% CPU/GPU"
                gpu_match = re.search(r'(\d+)%\s*GPU', processor, re.IGNORECASE)
                if gpu_match:
                    gpu_pct = int(gpu_match.group(1))
                    if gpu_pct > 0:
                        has_gpu = True
                # Also check for mixed format like "48%/52% CPU/GPU"
                mixed_match = re.search(r'(\d+)%/(\d+)%\s*CPU/GPU', processor, re.IGNORECASE)
                if mixed_match:
                    cpu_pct = int(mixed_match.group(1))
                    gpu_pct = int(mixed_match.group(2))
                    if gpu_pct > 0:
                        has_gpu = True
    
    processor_info = details[0]["processor"] if details else "No models loaded"
    
    return {
        "using_gpu": has_gpu,
        "processor_info": processor_info,
        "models_loaded": models_loaded,
        "details": details
    }

