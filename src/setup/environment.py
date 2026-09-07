"""Environment setup and validation logic (Stage 01).

Moved verbatim from ``scripts/01_setup_environment.py`` so the script stays a
thin orchestrator (argparse + path bootstrap + logging + one delegated call).
"""

from __future__ import annotations

import argparse
import logging
import platform
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml

from src.config.loader import ConfigLoader
from src.utils.helpers import (
    ensure_model_available,
    ollama_is_running,
    run_cmd_capture,
)
from src.utils.logging_setup import (
    log_info_box,
)


def report_system_info(logger: logging.Logger, project_root: Path) -> Dict[str, str]:
    """Report comprehensive system information.

    Args:
        logger: Logger instance for output
        project_root: Repository root directory (reported as "Repository Root")

    Returns:
        Dictionary of system information
    """
    system_info = {
        "Python Version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "Python Executable": sys.executable,
        "Platform": platform.platform(),
        "OS": platform.system(),
        "Architecture": platform.machine(),
        "Hostname": platform.node(),
        "Repository Root": str(project_root),
    }

    # Add disk space info
    try:
        usage = shutil.disk_usage(Path.cwd())
        system_info["Disk Free"] = f"{usage.free / (1024**3):.1f} GB"
        system_info["Disk Usage"] = f"{(usage.used / usage.total * 100):.1f}%"
    except Exception as exc:
        logger.debug(f"Could not get disk usage: {exc}")

    log_info_box(logger, "System Information", system_info, emoji="💻")

    return system_info


def check_tool_availability(logger: logging.Logger) -> Tuple[bool, Dict[str, str]]:
    """Check availability of required and optional tools.

    Args:
        logger: Logger instance for output

    Returns:
        Tuple of (all_required_available, tool_versions)
    """
    tools = {
        "uv": {"required": True, "cmd": ["uv", "--version"]},
        "python3": {"required": True, "cmd": ["python3", "--version"]},
        "git": {"required": False, "cmd": ["git", "--version"]},
        "ollama": {"required": False, "cmd": ["ollama", "--version"]},
    }

    tool_versions = {}
    all_required_available = True

    logger.info("")
    logger.info("🔧 Tool Availability")
    logger.info("─" * 60)

    for tool_name, info in tools.items():
        result = run_cmd_capture(info["cmd"])
        available = result.returncode == 0

        if available:
            version = result.stdout.strip().split("\n")[0] if result.stdout else "available"
            tool_versions[tool_name] = version
            logger.info(f"  ✅ {tool_name:.<18} {version}")
        else:
            tool_versions[tool_name] = "NOT FOUND"
            if info["required"]:
                logger.error(f"  ❌ {tool_name:.<18} NOT FOUND (required)")
                all_required_available = False
            else:
                logger.warning(f"  ⚠️  {tool_name:.<18} NOT FOUND (optional)")

    logger.info("─" * 60)
    return all_required_available, tool_versions


def validate_configurations(
    config_dir: Path,
    logger: logging.Logger
) -> Tuple[bool, Optional[ConfigLoader], Dict[str, int]]:
    """Validate all configuration files and report details.

    Args:
        config_dir: Path to configuration directory
        logger: Logger instance for output

    Returns:
        Tuple of (success, config_loader, config_stats)
    """
    logger.info("")
    logger.info("⚙️  Configuration Validation")
    logger.info("─" * 60)
    logger.info(f"  📁 Config directory: {config_dir}")
    logger.info("")

    config_stats = {}

    try:
        # Check configuration files exist
        config_files = {
            "course_config.yaml": "Course structure",
            "llm_config.yaml": "LLM settings",
            "output_config.yaml": "Output paths",
        }

        logger.info("  📄 Configuration Files:")
        for filename, description in config_files.items():
            filepath = config_dir / filename
            if filepath.exists():
                size = filepath.stat().st_size
                logger.info(f"    ✅ {filename:.<25} {description:.<15} ({size:>5,} bytes)")
            else:
                logger.error(f"    ❌ {filename:.<25} NOT FOUND")
                logger.info("─" * 60)
                return False, None, config_stats

        # Load and validate
        config_loader = ConfigLoader(config_dir)
        config_loader.validate_all_configs()
        logger.info("  ✅ All configurations validated")
        logger.info("")

        # Report configuration details
        course_info = config_loader.get_course_info()
        modules = config_loader.get_modules()
        config_stats["module_count"] = len(modules) if modules else 0

        # Report course info (concise)
        logger.info("  📚 Course Information:")
        logger.info(f"    • Course: {course_info.get('name', 'Unknown')}")
        logger.info(f"    • Level:  {course_info.get('level', 'Unknown')}")
        logger.info(f"    • Modules loaded: {len(modules) if modules else 0}")
        logger.info("")

        # LLM configuration
        llm_params = config_loader.get_llm_parameters()
        config_stats["llm_model"] = llm_params.get("model", "unknown")
        config_stats["llm_temperature"] = llm_params.get("temperature", 0.0)
        # Get num_predict from parameters (Ollama uses num_predict, not max_tokens)
        parameters = llm_params.get("parameters", {})
        config_stats["llm_max_tokens"] = parameters.get("num_predict", 0)

        logger.info("  🤖 LLM Configuration:")
        logger.info(f"    • Model: {llm_params.get('model', 'not specified')}")
        temp = parameters.get('temperature', 'default')
        tokens = parameters.get('num_predict', 'default')
        logger.info(f"    • Temperature: {temp}, Max Tokens: {tokens}")
        logger.info("")

        # Output configuration (summary only)
        output_config = config_loader.get_output_paths()
        base_dir = output_config.get("base_directory", "output")
        directories = output_config.get("directories", {})
        config_stats["output_directory_count"] = len(directories)
        logger.info(f"  📂 Output base: {base_dir} ({len(directories)} directories)")

        logger.info("─" * 60)
        return True, config_loader, config_stats

    except Exception as exc:
        logger.error(f"  ❌ Configuration validation failed: {exc}")
        logger.info("─" * 60)
        return False, None, config_stats


def setup_output_structure(
    config_dir: Path,
    logger: logging.Logger,
    course_name: Optional[str] = None
) -> Tuple[bool, List[Path]]:
    """Ensure output directory structure exists.

    Args:
        config_dir: Path to configuration directory
        logger: Logger instance for output
        course_name: Optional course template name for course-specific directories

    Returns:
        Tuple of (success, created_directories)
    """
    logger.info("")
    logger.info("📂 Output Directory Structure")
    logger.info("─" * 60)

    try:
        with open(config_dir / "output_config.yaml", "r", encoding="utf-8") as f:
            output_config = yaml.safe_load(f).get("output", {})
        base = Path(output_config.get("base_directory", "output"))
        directories = output_config.get("directories", {})

        created_dirs = []

        # Create base directory
        if not base.exists():
            base.mkdir(parents=True, exist_ok=True)
            logger.info(f"  ✅ Created base: {base}")
            created_dirs.append(base)
        else:
            logger.info(f"  ✅ Base exists: {base}")

        # Determine target directory (course-specific or default)
        if course_name:
            target_base = base / course_name
            logger.info(f"  📁 Course-specific directory: {course_name}/")
        else:
            target_base = base
            logger.info(f"  📁 Default directory structure")

        # Create subdirectories (compact view)
        for name, subdir in sorted(directories.items()):
            if course_name:
                # Course-specific: output/{course_name}/{subdir}
                dir_path = target_base / subdir
            else:
                # Default: output/{subdir}
                dir_path = base / subdir

            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                display_path = f"{course_name}/{subdir}" if course_name else subdir
                logger.info(f"  ✅ Created: {name:.<18} → {display_path}")
                created_dirs.append(dir_path)
            else:
                # Count existing files
                file_count = len(list(dir_path.glob("*")))
                display_path = f"{course_name}/{subdir}" if course_name else subdir
                if file_count > 0:
                    logger.info(f"  ✅ Exists:  {name:.<18} → {display_path} ({file_count} files)")
                else:
                    logger.info(f"  ✅ Exists:  {name:.<18} → {display_path}")

        logger.info("")
        logger.info(f"  📊 Total directories: {len(directories) + 1} (created: {len(created_dirs)})")
        logger.info("─" * 60)

        return True, created_dirs

    except Exception as exc:
        logger.error(f"  ❌ Failed to setup output structure: {exc}")
        logger.info("─" * 60)
        return False, []


def check_ollama_status(
    config_loader: ConfigLoader,
    logger: logging.Logger,
    start_if_needed: bool = False,
) -> Tuple[bool, Dict[str, any]]:
    """Check Ollama service status and model availability.

    Args:
        config_loader: ConfigLoader instance
        logger: Logger instance for output
        start_if_needed: Whether to attempt starting Ollama if not running

    Returns:
        Tuple of (ollama_ready, status_info)
    """
    logger.info("")
    logger.info("🤖 Ollama Service Status")
    logger.info("─" * 60)

    status_info = {
        "running": False,
        "configured_model_available": False,
        "available_models": [],
    }

    # Check if Ollama is running
    if ollama_is_running():
        logger.info("  ✅ Service is running")
        status_info["running"] = True
    else:
        logger.warning("  ❌ Service is NOT running")

        if start_if_needed:
            logger.info("  🔄 Attempting to start Ollama service...")
            run_cmd_capture(["ollama", "serve"])

            if ollama_is_running():
                logger.info("  ✅ Service started successfully")
                status_info["running"] = True
            else:
                logger.error("  ❌ Failed to start service")
                logger.error("  💡 Please start manually: ollama serve")
                logger.info("─" * 60)
                return False, status_info
        else:
            logger.warning("  💡 Run with --start-ollama to attempt auto-start")
            logger.warning("  💡 Or start manually: ollama serve")
            logger.info("─" * 60)
            return False, status_info

    # List available models
    logger.info("  📋 Checking available models...")
    list_result = run_cmd_capture(["ollama", "list"])

    if list_result.returncode == 0 and list_result.stdout:
        lines = list_result.stdout.strip().split("\n")
        if len(lines) > 1:  # Skip header
            models = []
            for line in lines[1:]:
                parts = line.split()
                if parts:
                    model_name = parts[0]
                    models.append(model_name)
                    logger.info(f"    • {model_name}")
            status_info["available_models"] = models
            logger.info(f"  📊 Total models: {len(models)}")
        else:
            logger.warning("  ⚠️  No models found")
    else:
        logger.warning("  ⚠️  Could not list models")

    logger.info("")
    # Check configured model
    configured_model = config_loader.get_llm_parameters().get("model", "llama3")
    logger.info(f"  🎯 Configured model: {configured_model}")

    if ensure_model_available(configured_model):
        logger.info(f"  ✅ Model '{configured_model}' is available")
        status_info["configured_model_available"] = True
    else:
        logger.warning(f"  ❌ Model '{configured_model}' NOT FOUND")
        logger.warning(f"  💡 Run: ollama pull {configured_model}")
        status_info["configured_model_available"] = False

    # Check GPU usage
    logger.info("")
    logger.info("  🎮 Checking GPU acceleration...")
    from src.utils.helpers import check_ollama_gpu_usage
    gpu_info = check_ollama_gpu_usage()
    if gpu_info["models_loaded"]:
        if gpu_info["using_gpu"]:
            logger.info(f"  ✅ GPU acceleration active: {gpu_info['processor_info']}")
            status_info["gpu_active"] = True
        else:
            logger.warning(f"  ⚠️  CPU-only mode detected: {gpu_info['processor_info']}")
            logger.warning("  💡 Generation will be slower. Check Ollama Metal support.")
            status_info["gpu_active"] = False
    else:
        logger.info("  ℹ️  No models currently loaded (GPU check requires active model)")
        logger.info("  💡 GPU will be verified when model is first used")
        status_info["gpu_active"] = None  # Unknown - no models loaded

    logger.info("─" * 60)
    return status_info["running"] and status_info["configured_model_available"], status_info


def print_summary(
    logger: logging.Logger,
    success: bool,
    system_info: Dict[str, str],
    tool_versions: Dict[str, str],
    config_stats: Dict[str, any],
    ollama_status: Dict[str, any],
) -> None:
    """Print comprehensive summary of environment setup.

    Args:
        logger: Logger instance for output
        success: Overall success status
        system_info: System information dictionary
        tool_versions: Tool version information
        config_stats: Configuration statistics
        ollama_status: Ollama status information
    """
    logger.info("")
    logger.info("📊 ENVIRONMENT SETUP SUMMARY")
    logger.info("─" * 60)

    # Overall status
    status_emoji = "✅" if success else "❌"
    status_text = "READY" if success else "INCOMPLETE"
    logger.info(f"{status_emoji} Overall Status: {status_text}")
    logger.info("")

    # System
    logger.info("💻 System:")
    logger.info(f"  • Python: {system_info.get('Python Version', 'unknown')}")
    logger.info(f"  • Platform: {system_info.get('Platform', 'unknown')[:50]}")
    logger.info(f"  • Disk Free: {system_info.get('Disk Free', 'unknown')}")
    logger.info("")

    # Tools
    logger.info("🔧 Tools:")
    for tool, version in tool_versions.items():
        status_emoji = "✅" if version != "NOT FOUND" else "❌"
        display_version = version[:50] if len(version) > 50 else version
        logger.info(f"  {status_emoji} {tool}: {display_version}")
    logger.info("")

    # Configuration
    logger.info("⚙️  Configuration:")
    logger.info(f"  • Modules: {config_stats.get('module_count', 0)}")
    logger.info(f"  • LLM Model: {config_stats.get('llm_model', 'unknown')}")
    logger.info(f"  • Output Directories: {config_stats.get('output_directory_count', 0)}")
    logger.info("")

    # Ollama
    logger.info("🤖 Ollama:")
    ollama_running_emoji = "✅" if ollama_status.get("running") else "❌"
    ollama_running_text = "Running" if ollama_status.get("running") else "Not Running"
    logger.info(f"  {ollama_running_emoji} Service: {ollama_running_text}")
    logger.info(f"  📊 Available Models: {len(ollama_status.get('available_models', []))}")
    model_ready_emoji = "✅" if ollama_status.get("configured_model_available") else "❌"
    model_ready_text = "Available" if ollama_status.get("configured_model_available") else "Not Available"
    logger.info(f"  {model_ready_emoji} Configured Model: {model_ready_text}")
    logger.info("─" * 60)
    logger.info("")

    if success:
        logger.info("✅ Environment is ready for validation and testing")
        logger.info("  💡 Next step: uv run python3 scripts/02_run_tests.py")
    else:
        logger.warning("⚠️  Environment setup incomplete - address issues above")


def run_environment_setup(
    args: argparse.Namespace,
    project_root: Path,
    logger: logging.Logger,
) -> int:
    """Run the full environment setup flow (Stage 01).

    Args:
        args: Parsed CLI arguments (auto_install, start_ollama, config_dir)
        project_root: Repository root directory
        logger: Logger instance configured by the calling script

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Track overall success
    overall_success = True

    # System information
    system_info = report_system_info(logger, project_root)
    logger.info("")

    # Tool availability
    tools_available, tool_versions = check_tool_availability(logger)
    if not tools_available:
        logger.error("Required tools are missing - cannot continue")
        return 1
    logger.info("")

    # Optional dependency install
    if args.auto_install:
        logger.info("")
        logger.info("📦 Installing Dependencies")
        logger.info("─" * 60)
        logger.info("  🔄 Running: uv pip install -e .[dev]")
        install_result = run_cmd_capture(
            ["uv", "pip", "install", "-e", ".[dev]"],
            cwd=project_root,
        )
        if install_result.returncode == 0:
            logger.info("  ✅ Dependencies installed successfully")
        else:
            logger.error("  ❌ Dependency installation failed")
            logger.error(f"  {install_result.stderr}")
            overall_success = False
        logger.info("─" * 60)
        logger.info("")

    # Configuration validation
    config_valid, config_loader, config_stats = validate_configurations(
        args.config_dir, logger
    )
    if not config_valid:
        logger.error("Configuration validation failed - cannot continue")
        return 1
    logger.info("")

    # Output structure
    output_success, created_dirs = setup_output_structure(args.config_dir, logger)
    if not output_success:
        logger.warning("Output structure setup had issues")
        overall_success = False
    logger.info("")

    # Ollama status
    ollama_ready, ollama_status = check_ollama_status(
        config_loader, logger, args.start_ollama
    )
    if not ollama_ready:
        logger.warning("Ollama is not fully ready")
        overall_success = False
    logger.info("")

    # Summary
    print_summary(
        logger,
        overall_success,
        system_info,
        tool_versions,
        config_stats,
        ollama_status,
    )

    return 0 if overall_success else 1
