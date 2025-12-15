#!/usr/bin/env python3
"""Test script for 04_generate_primary.py - returns success or failure."""
import sys
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config-dir', type=Path)
    parser.add_argument('--modules', nargs='+', type=int, default=None)
    parser.add_argument('--all', action='store_true')
    parser.add_argument('--outline', type=Path, default=None)
    args = parser.parse_args()
    
    # For test failure scenario
    import os
    if os.environ.get('TEST_PRIMARY_FAIL') == '1':
        return 1
    
    # Real script would generate primary materials
    # For test: just return success
    return 0

if __name__ == '__main__':
    sys.exit(main())


