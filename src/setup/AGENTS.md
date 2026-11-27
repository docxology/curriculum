# Setup Module

[environment.py](environment.py) owns the Stage 01 environment checks.
[__init__.py](__init__.py) defines the package.

## Stage 01 interface

[The Stage 01 script](../../scripts/01_setup_environment.py) sets up its
import path, parses arguments, and configures logging before delegating to
`src.setup.environment.run_environment_setup(args, project_root, logger)`.
The function reports system information, checks tools and configuration,
prepares output directories, and checks Ollama and the configured model.
It returns exit code 0 on success and 1 when setup is incomplete.

Keep environment validation and setup behavior in `environment.py` and
command-line argument parsing and logging initialization in the wrapper.
The [scripts guide](../../scripts/AGENTS.md) covers the other stage entry points.

## Related tests

- [Configuration loader tests](../../tests/test_config_loader.py) cover the
  `ConfigLoader` loading and validation behavior that Stage 01 uses.
- [Logging tests](../../tests/test_logging_setup.py) cover `setup_logging` in
  the wrapper and the formatting helpers used in `environment.py`.

See the [module README](README.md) and [setup guide](../../docs/SETUP.md)
for user-facing navigation.
