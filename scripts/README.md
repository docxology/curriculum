# Scripts

Thin orchestrator scripts for the educational course materials generator. All
testable logic lives in `src/` modules; scripts only set paths, configure
logging, and invoke a single `src/` entrypoint.

## Script Inventory

| Script | Purpose | Delegates to | Command |
|--------|---------|--------------|---------|
| `01_setup_environment.py` | Environment validation: tools, config, output dirs, Ollama | `src/setup/environment.py::run_environment_setup` | `uv run python3 scripts/01_setup_environment.py` |
| `02_run_tests.py` | Config validation + pytest with reports/metrics | `src/validation/runner.py::run_validation_and_tests` | `uv run python3 scripts/02_run_tests.py` |
| `03_generate_outline.py` | Course outline generation (interactive/batch) | `src/generate/stages/outline_workflow.py::run_outline_generation` | `uv run python3 scripts/03_generate_outline.py --no-interactive` |
| `04_generate_primary.py` | Session-based primary materials (lectures, labs, notes, diagrams, questions) | `src/generate/orchestration/pipeline.py::ContentGenerator` | `uv run python3 scripts/04_generate_primary.py --modules 1` |
| `05_generate_secondary.py` | Session-based secondary materials (application, extension, visualization, integration, investigation, open questions) | `src/generate/stages/secondary.py::run_secondary_generation` | `uv run python3 scripts/05_generate_secondary.py --modules 1 --dry-run` |
| `06_website.py` | Single-file website generation | `src/website/generator.py::WebsiteGenerator` | `uv run python3 scripts/06_website.py --open-browser` |
| `run_pipeline.py` | Runs stages 01 → 06 sequentially | the six stage scripts | `uv run python3 scripts/run_pipeline.py` |

## Pipeline Order

```
01_setup_environment → 02_run_tests → 03_generate_outline
  → 04_generate_primary → 05_generate_secondary → 06_website
```

`run_pipeline.py` chains all six stages and supports
`--skip-outline`, `--modules`, and `--log-level` (see `docs/PIPELINE_GUIDE.md`).

## Outputs

- Outlines: `output/outlines/` and `output/{course_name}/outlines/` (`.json` + `.md`)
- Session materials: `output/{course_name}/modules/module_XX_name/session_YY/`
- Test reports: `output/test_reports/` (`test_results_TIMESTAMP.log` / `.json`)
- Runtime logs: `output/logs/`
- Website: `output/{course_name}/website/index.html` (fallback: `output/website/index.html`)

All generated artifacts belong under the repo-root `output/` tree — never
inside `scripts/`.

## Development Contract

- Scripts are orchestration only: argparse, path bootstrap, logging, and one
  delegated call into `src/`.
- Business/data/plot/analysis logic lives in `src/` (importable and tested).
- See `scripts/AGENTS.md` for the technical contract and module mapping.
