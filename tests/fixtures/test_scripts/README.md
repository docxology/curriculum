# Test Script Fixtures

Fixture copies of pipeline scripts for testing purposes.

## Overview

This directory contains test fixtures that are copies or references to scripts in `scripts/`. These are used in tests to verify script execution, argument parsing, and integration patterns.

## Contents

- `01_setup_environment.py` - Environment setup script fixture
- `02_run_tests.py` - Test runner script fixture
- `03_generate_outline.py` - Outline generation script fixture
- `04_generate_primary.py` - Primary materials script fixture
- `05_generate_secondary.py` - Secondary materials script fixture
- `06_website.py` - Website generation script fixture

## Usage

These fixtures are used in tests to:
- Verify script execution without modifying source scripts
- Test specific script behaviors in isolation
- Validate argument parsing and error handling
- Test integration with the test framework

## Maintenance

When source scripts in `scripts/` are updated, corresponding fixtures may need to be updated to maintain test accuracy.

## See Also

- **[../../README.md](../../README.md)** - Test suite documentation
- **[../../../scripts/README.md](../../../scripts/README.md)** - Script documentation
