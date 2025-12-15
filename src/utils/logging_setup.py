"""Centralized logging configuration for educational course generator.

This module provides utilities for setting up consistent logging across
all scripts and modules, with support for both console and file output.
"""

import logging
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any


# Clean separators (simpler, more readable)
SEPARATOR_LINE = "─" * 60  # Simple line separator

# Operation name abbreviations for compact request IDs (matches src/llm/client.py)
OPERATION_ABBREVIATIONS = {
    "outline": "out",
    "lecture": "lec",
    "lab": "lab",
    "study_notes": "stu",
    "diagram": "dia",
    "questions": "qst",
    "application": "app",
    "extension": "ext",
    "visualization": "viz",
    "integration": "int",
    "investigation": "inv",
    "open_questions": "opq",
}


def setup_logging(
    script_name: str,
    log_dir: Optional[Path] = None,
    log_level: str = "INFO",
    console_output: bool = True,
    file_output: bool = True,
    log_format: Optional[str] = None
) -> Path:
    """Configure logging with both console and file handlers.
    
    Args:
        script_name: Name of the script (used for log filename)
        log_dir: Directory for log files (default: output/logs/)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        console_output: Whether to output to console
        file_output: Whether to output to file
        log_format: Custom log format string
        
    Returns:
        Path to log file (or None if file_output is False)
    """
    # Use default format if not provided
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Get or create log directory
    if log_dir is None:
        log_dir = Path("output") / "logs"
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"{script_name}_{timestamp}.log"
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(log_format)
    
    # Add console handler if requested
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # Add file handler if requested
    if file_output:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        
        # Log the log file location
        root_logger.info(f"Logging to file: {log_file.resolve()}")
    
    return log_file if file_output else None


def log_section_header(logger: logging.Logger, title: str, major: bool = True) -> None:
    """Log a formatted section header.
    
    Args:
        logger: Logger instance
        title: Section title
        major: If True, use major separator (═), else minor (─)
    """
    separator = "═" * 80 if major else "─" * 80
    logger.info(separator)
    logger.info(title)
    logger.info(separator)


def log_section_clean(logger: logging.Logger, title: str, emoji: str = "📋") -> None:
    """Log a clean, emoji-based section header.
    
    Args:
        logger: Logger instance
        title: Section title
        emoji: Emoji to prefix the title (default: 📋)
    """
    logger.info("")
    logger.info(f"{emoji} {title}")
    logger.info(SEPARATOR_LINE)


def log_info_box(logger: logging.Logger, title: str, items: Dict[str, Any], emoji: str = "ℹ️") -> None:
    """Log information in a clean, structured box format.
    
    Args:
        logger: Logger instance
        title: Box title
        items: Dictionary of key-value pairs to display
        emoji: Emoji for the title (default: ℹ️)
    """
    logger.info("")
    logger.info(f"{emoji} {title}")
    logger.info(SEPARATOR_LINE)
    for key, value in items.items():
        logger.info(f"  • {key}: {value}")
    logger.info(SEPARATOR_LINE)


def log_status_item(logger: logging.Logger, label: str, value: Any, status: str = "info") -> None:
    """Log a single status item with appropriate emoji.
    
    Args:
        logger: Logger instance
        label: Item label
        value: Item value
        status: Status type (success, error, warning, info)
    """
    emoji_map = {
        "success": "✅",
        "error": "❌",
        "warning": "⚠️",
        "info": "ℹ️",
        "check": "✓"
    }
    emoji = emoji_map.get(status, "•")
    logger.info(f"  {emoji} {label}: {value}")


def log_parameters(
    logger: logging.Logger,
    params: Dict[str, Any],
    title: str = "Parameters"
) -> None:
    """Log parameters in a structured, readable format.
    
    Args:
        logger: Logger instance
        params: Dictionary of parameters to log
        title: Title for the parameter block
    """
    logger.info(f"{title} ({len(params)} provided):")
    
    # Calculate max key length for alignment
    max_key_len = max(len(str(k)) for k in params.keys()) if params else 0
    
    for key, value in sorted(params.items()):
        # Format value with appropriate representation
        if isinstance(value, str):
            # Truncate long strings
            if len(value) > 60:
                value_str = f'"{value[:57]}..."'
            else:
                value_str = f'"{value}"'
        elif isinstance(value, (int, float)):
            value_str = str(value)
        elif isinstance(value, bool):
            value_str = str(value)
        elif value is None:
            value_str = "None"
        else:
            value_str = str(value)[:60]
        
        # Log with checkmark and alignment
        logger.info(f"  ✓ {key:<{max_key_len}} : {value_str}")


def log_validation_results(
    logger: logging.Logger,
    required_vars: set,
    provided_vars: set,
    missing_vars: set,
    extra_vars: set
) -> None:
    """Log template variable validation results.
    
    Args:
        logger: Logger instance
        required_vars: Set of required variable names
        provided_vars: Set of provided variable names
        missing_vars: Set of missing variable names
        extra_vars: Set of extra variable names
    """
    logger.info("Template Validation:")
    
    if not missing_vars and not extra_vars:
        logger.info(f"  ✓ All {len(required_vars)} required variables provided")
        logger.info("  ✓ No missing variables")
        logger.info("  ✓ No extra variables")
    else:
        if missing_vars:
            logger.error(f"  ✗ Missing {len(missing_vars)} required variables:")
            for var in sorted(missing_vars):
                logger.error(f"      - {var}")
        else:
            logger.info(f"  ✓ All {len(required_vars)} required variables provided")
        
        if extra_vars:
            logger.warning(f"  ⚠️  Extra {len(extra_vars)} variables provided (will be ignored):")
            for var in sorted(extra_vars):
                logger.warning(f"      - {var}")
        else:
            logger.info("  ✓ No extra variables")


def log_summary_box(
    logger: logging.Logger,
    title: str,
    items: Dict[str, Any],
    status: str = "success"
) -> None:
    """Log a summary box with results.
    
    Args:
        logger: Logger instance
        title: Box title
        items: Dictionary of items to display
        status: Status indicator (success, warning, error)
    """
    # Determine status emoji
    status_emoji = {
        "success": "✅",
        "warning": "⚠️",
        "error": "✗",
        "info": "📊"
    }.get(status, "")
    
    logger.info("═" * 80)
    logger.info(f"{status_emoji} {title}")
    logger.info("═" * 80)
    
    for key, value in items.items():
        if isinstance(value, (int, float)):
            logger.info(f"  • {key}: {value:,}")
        else:
            logger.info(f"  • {key}: {value}")
    
    logger.info("═" * 80)


def log_operation_context(
    logger: logging.Logger,
    module: str,
    session: Optional[str] = None
) -> None:
    """Log operation context for better traceability.
    
    Args:
        logger: Logger instance
        module: Module name or identifier
        session: Optional session identifier
    """
    if session:
        context = f"{module} (Session {session})"
    else:
        context = module
    logger.debug(f"Operation context: {context}")


def log_llm_request_summary(
    logger: logging.Logger,
    request_id: str,
    operation: str,
    model: str,
    prompt_len: int,
    level: str = "INFO"
) -> None:
    """Log LLM request summary with appropriate level.
    
    Args:
        logger: Logger instance
        request_id: Request identifier
        operation: Operation name (e.g., "lecture", "lab")
        model: Model name
        prompt_len: Prompt length in characters
        level: Log level (INFO or DEBUG)
    """
    log_func = getattr(logger, level.lower(), logger.info)
    log_func(
        f"[{request_id}] LLM Request: {operation} | "
        f"model={model} | prompt={prompt_len} chars"
    )


def log_status_with_text(
    logger: logging.Logger,
    status: str,
    message: str,
    emoji: Optional[str] = None,
    level: str = "INFO"
) -> None:
    """Log a status message with text label and optional emoji for accessibility.
    
    Always includes text label in format: [STATUS] message (optional emoji)
    This ensures screen readers can understand the status without emoji.
    
    Args:
        logger: Logger instance
        status: Status text label (e.g., "CRITICAL", "WARNING", "COMPLIANT", "OK")
        message: Message text
        emoji: Optional emoji to append after text label
        level: Log level (INFO, WARNING, ERROR, DEBUG)
    """
    # Format: [STATUS] message (emoji)
    if emoji:
        formatted_message = f"[{status}] {message} {emoji}"
    else:
        formatted_message = f"[{status}] {message}"
    
    log_func = getattr(logger, level.lower(), logger.info)
    log_func(formatted_message)


def log_error_summary(
    logger: logging.Logger,
    title: str,
    errors: list,
    max_items: int = 10,
    show_context: bool = True
) -> None:
    """Log a structured error summary.
    
    Args:
        logger: Logger instance
        title: Summary title
        errors: List of error entries (ErrorEntry objects or dicts with message, context, etc.)
        max_items: Maximum number of errors to display
        show_context: Whether to show context information
    """
    logger.info("")
    logger.info("═" * 80)
    logger.info(f"[ERROR SUMMARY] {title}")
    logger.info("═" * 80)
    
    if not errors:
        logger.info("  [OK] No errors found")
        logger.info("═" * 80)
        return
    
    total = len(errors)
    displayed = min(total, max_items)
    
    logger.info(f"  Total errors: {total}")
    if total > max_items:
        logger.info(f"  Showing first {max_items} errors")
    logger.info("")
    
    for i, error in enumerate(errors[:max_items], 1):
        # Handle both ErrorEntry objects and dicts
        if hasattr(error, 'message'):
            message = error.message
            severity = getattr(error, 'severity', 'UNKNOWN')
            context = getattr(error, 'context', None)
            content_type = getattr(error, 'content_type', None)
        else:
            message = error.get('message', str(error))
            severity = error.get('severity', 'UNKNOWN')
            context = error.get('context')
            content_type = error.get('content_type')
        
        # Log severity and message
        logger.warning(f"  [{i}/{displayed}] [{severity}] {message}")
        
        # Log context if available and requested
        if show_context:
            if context:
                logger.warning(f"         Context: {context}")
            if content_type:
                logger.warning(f"         Content Type: {content_type}")
    
    if total > max_items:
        logger.info(f"  ... and {total - max_items} more errors (see full log for details)")
    
    logger.info("═" * 80)


def format_request_id(operation: Optional[str], uuid_str: Optional[str] = None) -> str:
    """Format request ID with operation abbreviation.
    
    Args:
        operation: Optional operation name (e.g., "lecture", "lab")
        uuid_str: Optional UUID string (defaults to generating new 6-char UUID)
        
    Returns:
        Formatted request ID in format [op:uuid] or [req:uuid]
    """
    if uuid_str is None:
        uuid_short = uuid.uuid4().hex[:6]
    else:
        uuid_short = uuid_str[:6] if len(uuid_str) >= 6 else uuid_str
    
    if operation:
        abbrev = OPERATION_ABBREVIATIONS.get(operation, operation[:3])
        return f"{abbrev}:{uuid_short}"
    return f"req:{uuid_short}"


def log_llm_request_compact(
    logger: logging.Logger,
    request_id: str,
    operation: Optional[str],
    model: str,
    prompt_len: int,
    timeout: Optional[int] = None,
    level: str = "INFO"
) -> None:
    """Log LLM request in compact format with emoji.
    
    Args:
        logger: Logger instance
        request_id: Request identifier
        operation: Optional operation name (e.g., "lecture", "lab")
        model: Model name
        prompt_len: Prompt length in characters
        timeout: Optional timeout in seconds
        level: Log level (INFO or DEBUG)
    """
    op_abbrev = OPERATION_ABBREVIATIONS.get(operation, operation[:3] if operation else "req")
    timeout_info = f" | t={timeout}s" if timeout else ""
    log_func = getattr(logger, level.lower(), logger.info)
    log_func(
        f"[{request_id}] 🚀 {op_abbrev} | m={model} | p={prompt_len}c{timeout_info}"
    )


def log_stream_progress_compact(
    logger: logging.Logger,
    request_id: str,
    elapsed: float,
    chunks: int,
    text_len: int,
    tokens_est: int,
    chars_per_sec: float,
    tokens_per_sec: float,
    level: str = "INFO"
) -> None:
    """Log stream progress in compact format with emoji.
    
    Args:
        logger: Logger instance
        request_id: Request identifier
        elapsed: Elapsed time in seconds
        chunks: Number of chunks received
        text_len: Length of generated text in characters
        tokens_est: Estimated number of tokens
        chars_per_sec: Characters per second
        tokens_per_sec: Tokens per second
        level: Log level (INFO or DEBUG)
    """
    log_func = getattr(logger, level.lower(), logger.info)
    log_func(
        f"[{request_id}] 📊 {elapsed:.1f}s: {text_len}c @{chars_per_sec:.0f}c/s "
        f"({chunks}ch, ~{tokens_est:.0f}t @{tokens_per_sec:.0f}t/s)"
    )


def get_logging_config(config_loader) -> Dict[str, Any]:
    """Extract logging configuration from ConfigLoader.
    
    Args:
        config_loader: ConfigLoader instance
        
    Returns:
        Dictionary with logging configuration
    """
    try:
        output_config = config_loader.load_output_config()
        logging_config = output_config.get('output', {}).get('logging', {})
        
        return {
            'level': logging_config.get('level', 'INFO'),
            'format': logging_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            'console': logging_config.get('console', True),
            'file': logging_config.get('file', 'output/logs/generation.log')
        }
    except Exception:
        # Return defaults if config loading fails
        return {
            'level': 'INFO',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'console': True,
            'file': 'output/logs/generation.log'
        }

