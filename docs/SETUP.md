# Setup

From the repository root, use uv to install the checked-in environment.
The repository pins Python in [`.python-version`](../.python-version) and
declares its supported range in [`pyproject.toml`](../pyproject.toml).

```bash
uv sync --locked --extra dev
uv lock --check
```

## Verify local authoring and website assembly

Run the [offline fixture](OFFLINE_FIXTURE.md) to generate a temporary course
website. The selected native checks below use local files and real parser
and website code. `--noconftest` keeps the repository-wide Ollama autostart
fixture out of this run.

```bash
uv run --no-sync python -m pytest --noconftest -q \
  tests/test_config_loader.py tests/test_json_outline_integration.py \
  tests/test_parser.py tests/test_parser_edge_cases.py tests/test_cleanup.py \
  tests/test_website_content_loader.py tests/test_website_generator.py \
  tests/test_website_templates.py tests/test_website_scripts.py \
  tests/test_website_scripts_interaction.py tests/test_website_styles.py
```

## Choose a pipeline entry point

Stage 06 can start with existing inputs. Use an explicit `--outline` when
multiple course runs are present, and `--output` when you need a separate
HTML destination. Session material lookup still follows the output YAML
and the course key recorded in the outline. The [fixture](OFFLINE_FIXTURE.md)
shows how to isolate that lookup in a temporary directory.

Stages 03–05 generate outlines and materials through a local Ollama service.
Check the configured model and service settings in
[`config/llm_config.yaml`](../config/llm_config.yaml) before choosing those
stages. The [pipeline guide](PIPELINE_GUIDE.md) covers stage order and the
[configuration reference](CONFIGURATION.md) covers course and output settings.
Review generated content before using it for teaching.
