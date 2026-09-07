# AGENTS: `scripts/` — Thin Orchestrator Scripts

Technical specification for the course generator's pipeline scripts.

## Script Inventory

| Script | Pattern | Delegates to | Output |
|--------|---------|--------------|--------|
| `01_setup_environment.py` | Stage 01 Thin Orchestrator | `src/setup/environment.py` (`run_environment_setup`) | Console report; creates `output/` directory structure; exit code 0/1 |
| `02_run_tests.py` | Stage 02 Thin Orchestrator | `src/validation/runner.py` (`run_validation_and_tests`) | `output/test_reports/test_results_TIMESTAMP.{log,json}`; exit codes 0/1/2/3 |
| `03_generate_outline.py` | Stage 03 Thin Orchestrator | `src/generate/stages/outline_workflow.py` (`run_outline_generation`) → `src/generate/orchestration/pipeline.py::ContentGenerator` | `output/{course_name}/outlines/course_outline_TIMESTAMP.{json,md}`; exit 0/1 |
| `04_generate_primary.py` | Stage 04 Thin Orchestrator | `src/generate/orchestration/pipeline.py::ContentGenerator` | `output/{course_name}/modules/module_XX/session_YY/` primary materials; exit 0/1 |
| `05_generate_secondary.py` | Stage 05 Thin Orchestrator | `src/generate/stages/secondary.py` (`run_secondary_generation`) | `output/{course_name}/modules/module_XX/session_YY/` secondary materials; exit 0/1 |
| `06_website.py` | Stage 06 Thin Orchestrator | `src/website/generator.py::WebsiteGenerator` | `output/{course_name}/website/index.html`; exit 0/1 |
| `run_pipeline.py` | Master orchestrator | the six stage scripts (subprocess) | All stage outputs; aggregated exit code |

## Design Contract

- Scripts are orchestration only: argparse, path bootstrap (insert repo root
  on `sys.path`), logging setup, and a single delegated call into `src/`.
- Configuration/business/generation/analysis logic lives in `src/` modules and
  must be importable and testable independently of the scripts.
- Exit codes: `0` success; `1` validation/failure; `2` tests failed (stage 02);
  `3` pytest error / no tests collected (stage 02).
- Generated artifacts belong under repo-root `output/`; never commit or write
  runtime artifacts inside `scripts/`.
- All reusable script behavior must be covered by tests in `tests/`
  (unit-marked tests require no Ollama; integration tests require Ollama).

## Stage Modules

| Module | Contents |
|--------|----------|
| `src/setup/environment.py` | `report_system_info`, `check_tool_availability`, `validate_configurations`, `setup_output_structure`, `check_ollama_status`, `print_summary`, `run_environment_setup` |
| `src/validation/runner.py` | `validate_config`, `check_ollama`, `parse_pytest_output`, `parse_test_modules`, `discover_tests`, `stream_pytest_output`, `extract_warnings`, `extract_failures`, `parse_durations`, `run_tests_with_reporting`, `run_validation_and_tests` |
| `src/generate/stages/outline_workflow.py` | `maybe_override_course_info`, `run_outline_generation` |
| `src/generate/stages/secondary.py` | `SECONDARY_TYPES_DEFAULT`, `find_latest_outline`, `load_session_content`, `generate_secondary_for_session`, `run_secondary_generation` |
