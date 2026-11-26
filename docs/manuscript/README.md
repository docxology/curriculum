# Curriculum technical manuscript

The numbered Markdown files, configuration, preamble, and bibliography here
form the canonical source. The study uses existing fixture inputs to test
course website assembly. The [earlier scope audit](../other/curriculum_manuscript_scope_audit.md)
and tracked course outputs remain historical records.

## Render from a clean checkout

Install Git, uv, Graphviz, Pandoc `3.14`, and XeLaTeX with the
[Template PDF prerequisites](https://github.com/docxology/template/blob/87704feae0a4490ef7dad9c931d268e8c30273c2/docs/guides/startup-and-setup.md).
Run from the standalone repository root with the desired commit checked
out.

```bash
curriculum_source="$(pwd -P)"
curriculum_commit="$(git rev-parse HEAD)"
render_workspace="$(mktemp -d)"
template_checkout="$render_workspace/template"
git clone https://github.com/docxology/template.git "$template_checkout"
git -C "$template_checkout" checkout --detach 87704feae0a4490ef7dad9c931d268e8c30273c2
mkdir -p "$template_checkout/projects/working"
git clone "$curriculum_source" "$template_checkout/projects/working/curriculum"
cd "$template_checkout/projects/working/curriculum"
git checkout --detach "$curriculum_commit"
printf '\n/output/\n' >> .git/info/exclude
uv sync --locked --extra dev
```

The disposable checkout uses a local Git exclusion for generated output.
The tracked course snapshots remain in the checkout.

Run the command block in the [offline fixture walkthrough](../OFFLINE_FIXTURE.md)
in the same shell to set `fixture_dir` and build the course HTML, then
generate the JSON receipt and figure from that actual output.

```bash
uv run --no-sync python - "$fixture_dir/course.html" <<'PYTHON'
from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess
import sys


class CourseButtons(HTMLParser):
    def __init__(self):
        super().__init__()
        self.buttons = {"module-button": [], "session-button": [], "content-button": []}

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        kind = values.get("class")
        if tag == "button" and kind in self.buttons:
            self.buttons[kind].append(values)


html = Path(sys.argv[1]).read_text(encoding="utf-8")
page = CourseButtons()
page.feed(html)
modules = len(page.buttons["module-button"])
sessions = len(page.buttons["session-button"])
materials = page.buttons["content-button"]
assert (modules, sessions, len(materials)) == (2, 6, 2)
assert {entry["data-content-type"] for entry in materials} == {"lecture", "diagram_1"}
assert all(entry["data-module-id"] == "1" and entry["data-session"] == "session_01"
           for entry in materials)
assert "Cell Theory" in html and "mermaid@10" in html

data = Path("output/data")
figures = Path("output/figures")
data.mkdir(parents=True, exist_ok=True)
figures.mkdir(parents=True, exist_ok=True)
receipt = {"module_buttons": modules, "session_buttons": sessions,
           "material_buttons": len(materials), "material_placement": materials,
           "lecture_heading_found": True}
(data / "fixture_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")

graph = f"""digraph {{
  graph [rankdir=LR, pad=0.22, bgcolor="white", dpi=155]
  node [shape=box, style="rounded,filled", color="#174265", fillcolor="#E9F4FC",
        fontname="DejaVu Sans", fontsize=13, margin="0.20,0.16"]
  edge [color="#174265"]
  outline [label="Fixture outline"]
  inputs [label="Lecture and Mermaid files\\nfirst session"]
  navigation [label="{modules} module buttons\\n{sessions} session buttons"]
  content [label="{len(materials)} material buttons\\nlinked to first session"]
  outline -> navigation
  inputs -> content
}}"""
subprocess.run(["dot", "-Tpng", "-o", str(figures / "fixture_assembly.png")],
               input=graph, text=True, check=True)
PYTHON

cd "$template_checkout"
uv sync --locked
uv run --no-sync python scripts/pipeline/stage_03_render.py --project working/curriculum
uv run --no-sync python scripts/pipeline/stage_04_validate.py --project working/curriculum
```

In the working project, the technical artifacts are
`output/pdf/curriculum_combined.pdf`, `output/web/index.html`, and the
validation and source receipts under `output/reports/`. The course HTML
is the temporary `course.html` produced by Stage 06.
