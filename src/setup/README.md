# Setup Module

The Stage 01 [environment module](environment.py) checks tool availability and
configuration, prepares output directories, and checks the configured Ollama
service and model.

## Entry point

The [Stage 01 script](../../scripts/01_setup_environment.py) handles command-line
arguments, import paths, and logging, then calls `run_environment_setup` in
`src.setup.environment`. The function returns exit code 0 when setup
succeeds and 1 when it cannot complete.

See the [setup guide](../../docs/SETUP.md) for prerequisites and the
[pipeline guide](../../docs/PIPELINE_GUIDE.md) for the stage sequence.

## Related tests

The [configuration loader tests](../../tests/test_config_loader.py) cover loading
and validation of project configuration. The [logging tests](../../tests/test_logging_setup.py)
cover the logging helpers used by the wrapper and environment module.

See [AGENTS.md](AGENTS.md) for the source boundaries.
