# Build a course website without a model call

This example uses the checked-in [outline](../tests/fixtures/sample_outline.json),
[lecture](../tests/fixtures/sample_lecture.md), and
[Mermaid source](../tests/fixtures/sample_diagram.mmd).
It builds in a temporary directory so course-specific material lookup and logs
stay separate from the tracked course outputs. Run from the repository root
after [setup](SETUP.md).

```bash
project_dir="$(pwd -P)"
fixture_dir="$(mktemp -d)"
course_key="$(uv run --no-sync python -c 'from src.config.loader import ConfigLoader; print(ConfigLoader("config").get_output_paths()["course_name"])')"
session_dir="$fixture_dir/output/$course_key/modules/module_01_cell_biology/session_01"
mkdir -p "$session_dir"
cp tests/fixtures/sample_lecture.md "$session_dir/lecture.md"
cp tests/fixtures/sample_diagram.mmd "$session_dir/diagram_1.mmd"
(
  cd "$fixture_dir"
  uv run --no-sync --project "$project_dir" python "$project_dir/scripts/06_website.py" \
    --config-dir "$project_dir/config" \
    --outline "$project_dir/tests/fixtures/sample_outline.json" \
    --output "$fixture_dir/course.html"
)
printf '%s\n' "$fixture_dir/course.html"
```

Inspect the HTML source for the course title, module and session buttons,
and the lecture and diagram buttons assigned to the first session. Other
sessions appear in navigation because they are in the outline. A session
without material files has no corresponding material buttons.

The output bundles the course content in one HTML file. Its template still
links to browser assets, including Mermaid and syntax highlighting libraries
served by CDNs. The generation command works offline. Rendering those
external assets in a browser depends on availability or the browser cache.
See the [manuscript results](manuscript/03_results.md) for the observed markup.
