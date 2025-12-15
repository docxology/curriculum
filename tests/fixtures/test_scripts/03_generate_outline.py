#!/usr/bin/env python3
"""Test script for 03_generate_outline.py - returns success or failure based on course."""
import sys
import argparse
import json
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config-dir', type=Path, required=True)
    parser.add_argument('--course', type=str, default=None)
    parser.add_argument('--no-interactive', action='store_true')
    args = parser.parse_args()
    
    # For test failure scenario: if course is 'biology' and we want to test failure
    # Check for environment variable or specific condition
    import os
    if os.environ.get('TEST_OUTLINE_FAIL') == '1':
        return 1
    
    # Create minimal outline file to simulate success
    # Find output directory (could be in config dir parent or scripts/output)
    possible_outputs = [
        args.config_dir.parent / "output" / "outlines",
        args.config_dir.parent / "scripts" / "output" / "outlines",
        Path("output") / "outlines",
        Path("scripts") / "output" / "outlines",
    ]
    
    output_dir = None
    for possible in possible_outputs:
        if possible.parent.exists():
            output_dir = possible
            break
    
    if output_dir is None:
        # Create in config_dir parent
        output_dir = args.config_dir.parent / "output" / "outlines"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create minimal valid outline
    outline = {
        "course_metadata": {
            "course_template": args.course or "test",
            "name": f"Test {args.course or 'Course'}"
        },
        "modules": []
    }
    
    import time
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    outline_path = output_dir / f"course_outline_{timestamp}.json"
    outline_path.write_text(json.dumps(outline, indent=2), encoding='utf-8')
    
    return 0

if __name__ == '__main__':
    sys.exit(main())


