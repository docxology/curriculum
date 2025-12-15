#!/usr/bin/env python3
"""06 - Website generation (Stage 06).

Generates a single, self-contained HTML website that serves as an entry point
to browse all course materials (modules, sessions, and content types).

The website is saved to: output/website/index.html
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to Python path to allow imports when run directly
_script_dir = Path(__file__).resolve().parent
_project_root = _script_dir.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

import argparse
import logging
import webbrowser

from src.config.loader import ConfigLoader
from src.website.generator import WebsiteGenerator
from src.utils.logging_setup import (
    setup_logging,
    log_section_clean,
    log_info_box,
    log_status_item,
)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate a single HTML website for browsing all course materials.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate website (auto-discovers latest outline)
  %(prog)s
  
  # Use specific outline file
  %(prog)s --outline scripts/output/outlines/course_outline_20241208.json
  
  # Custom output path
  %(prog)s --output custom/website.html
  
  # Open in browser after generation
  %(prog)s --open-browser
        """
    )
    parser.add_argument(
        "--outline",
        type=Path,
        default=None,
        help="Path to specific outline JSON (default: most recent in output/outlines/ or scripts/output/outlines/).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Custom output path for HTML file (default: output/website/index.html).",
    )
    parser.add_argument(
        "--config-dir",
        type=Path,
        default=Path(__file__).parent.parent / "config",
        help="Path to config directory (default: ../config).",
    )
    parser.add_argument(
        "--open-browser",
        action="store_true",
        help="Open generated website in default browser after generation.",
    )
    return parser.parse_args()


def main() -> int:
    """Main entry point."""
    args = parse_args()
    
    # Setup logging with file output
    log_file = setup_logging(
        script_name="06_website",
        log_level="INFO",
        console_output=True,
        file_output=True
    )
    
    logger = logging.getLogger("generate_website")
    
    log_section_clean(logger, "STAGE 06: WEBSITE GENERATION", emoji="🌐")
    
    logger.info("Generating single HTML website for course materials")
    logger.info("Output: output/website/index.html")
    logger.info("")
    
    try:
        # Initialize configuration
        config_loader = ConfigLoader(args.config_dir)
        config_loader.validate_all_configs()
        
        config_info = {
            "Config Directory": str(args.config_dir),
            "Log File": str(log_file) if log_file else "None"
        }
        log_info_box(logger, "CONFIGURATION", config_info, emoji="⚙️")
        
        # Validate outline exists
        if args.outline:
            logger.info(f"Using specified outline: {args.outline}")
            if not args.outline.exists():
                logger.error(f"Outline file not found: {args.outline}")
                logger.error("Please provide a valid outline path or omit --outline to use the latest.")
                return 1
            outline_path = args.outline
        else:
            # Find latest outline
            outline_path = config_loader._find_latest_outline_json()
            if not outline_path:
                logger.error("")
                log_status_item(logger, "ERROR", "No outline JSON found", "error")
                logger.error("Searched in:")
                logger.error("  - output/outlines/")
                logger.error("  - scripts/output/outlines/")
                logger.error("  - output/{course_name}/outlines/ (all course-specific directories)")
                logger.error("")
                logger.error("Generate an outline first:")
                logger.error("  uv run python3 scripts/03_generate_outline.py")
                logger.error("")
                return 1
            logger.info(f"Using most recent outline: {outline_path}")
        
        logger.info("")
        
        # Create website generator
        generator = WebsiteGenerator(config_loader)
        
        # Generate website
        try:
            output_path = generator.generate(
                outline_path=outline_path,
                output_path=args.output
            )
            
            logger.info("")
            log_status_item(logger, "SUCCESS", f"Website generated: {output_path.resolve()}", "success")
            logger.info("")
            logger.info("You can now open the website in your browser:")
            logger.info(f"  file://{output_path.resolve()}")
            logger.info("")
            
            # Open in browser if requested
            if args.open_browser:
                try:
                    webbrowser.open(f"file://{output_path.resolve()}")
                    logger.info("Opened website in default browser")
                except Exception as e:
                    logger.warning(f"Failed to open browser: {e}")
            
            return 0
            
        except FileNotFoundError as e:
            logger.error(f"File not found: {e}")
            return 1
        except ValueError as e:
            logger.error(f"Invalid data: {e}")
            return 1
        except Exception as e:
            logger.error(f"Website generation failed: {e}", exc_info=True)
            return 1
    
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())







