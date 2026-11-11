# TODO — curriculum

Backlog for agent-ergonomics and repo hygiene work. One line per entry.
Created 2026-08-31 (agent-erg fleet); items marked DONE completed same day in a follow-up pass
(commit 045875b). Scope any remaining work here.

## Minor

- [x] docs/TROUBLESHOOTING.md broken link (../../ -> ../src/) — DONE 2026-08-31
- [x] README/AGENTS.md stale test counts (~540/25 -> 658 collected/35 files, dated + verification command) — DONE 2026-08-31
- [x] AGENTS.md layout root mislabeled "biology/" — DONE 2026-08-31
- [x] output/ "gitignored" claims were false (no .gitignore existed) — DONE 2026-08-31: .gitignore added; claims now true

## Medium

- [x] Untracked generated AGENTS.md/README.md stub pairs (~200 files) polluted `git status` — DONE 2026-08-31: ignored via .gitignore per their own "gitignored, never committed" declaration
- [x] AGENTS.md "Recent Updates" frozen at Dec 2024 — DONE 2026-08-31: dated verified-state line added; keep appending dated entries (do not rewrite history)

## Major

- [x] 194 git-tracked .pyc files permanently showing as modified — DONE 2026-08-31: untracked via `git rm -r --cached` in commit 045875b; .gitignore now covers __pycache__/ and *.pyc
- [x] No .gitignore at all — DONE 2026-08-31: added in commit 045875b (also untracked .DS_Store, .coverage, output/logs/, scripts/output/logs/, scripts/test_reports/)
- [x] pytest marker scheme was broken: 28/35 test files had no marker, so `pytest -m unit` deselected all 658 — DONE 2026-08-31 Round 2: annotated 28 files with `pytestmark = pytest.mark.unit`; gate now runs 613 passed / 45 deselected / 0 failed
- [ ] No fast pre-push gate declared (lint/typecheck). If wanted: `uv run black --check src scripts` + `uv run flake8 src scripts` (tools already in dev deps) — owner decision whether to wire into a hook
- [ ] Full integration suite (`uv run pytest -m integration`) requires local Ollama + gemma3:4b; not verified in this pass — run before any release/tag

## Verification (2026-08-31, Round 2)

- Fast gate: `uv run pytest -m unit` -> 613 passed, 45 deselected, 0 failed (407s on external drive)
- `git status --porcelain | wc -l`: 206 (pre-pass) -> 1 (post-pass; the 1 is a pre-existing edit this fleet did not author)
- `git ls-files | grep -c '\.pyc$'` -> 0
- Link check across all touched docs: 0 broken

## Workflowz review — 2026-11-10

- [ ] **WFZ-01** (P1) Make `OllamaHealth.check_model_exists` fail closed or surface uncertainty instead of returning `True` on any exception. Evidence: src/llm/health.py:133-135 — `except Exception: # If we can't check, assume it might exist / return True`. Observable outcome: when the model-list request fails (connection error/timeout/HTTP error), the check no longer reports the model as present; callers either get `False` or an explicit "unknown" result they can act on. Acceptance probe (from repo root): add an unreachable `models_url` regression to the real health tests, then run `uv run pytest tests/test_llm_client.py tests/test_llm_client_timeouts.py -m unit`; expected: connection/timeout/HTTP failures never return a bare `True` and existing health diagnostics remain green. Dependencies/constraints: must stay consistent with the project's safe-to-fail logging guidance (.cursorrules/09) — log the failure reason before returning; do not break `get_diagnostics` (src/llm/health.py:137) which legitimately tolerates errors.
- [ ] **WFZ-02** (P2) Log per-file read failures in `load_session_content` instead of silently dropping material. Evidence: src/generate/stages/secondary.py:117-123 — material files are read in a loop and `except Exception: pass` skips any unreadable file with no record; contrast the sibling outline loader at src/generate/stages/secondary.py:51-55 which at least returns `""` for a single explicit path. Observable outcome: a session material file that fails to read (permissions/encoding) produces a warning naming the file, so generated secondary content is not silently built on incomplete input. Acceptance probe (from repo root): add a temporary-directory case with one valid Markdown file and one invalid-UTF-8 file, capturing logs with `caplog`, then run `uv run pytest tests/test_stage_workflows.py -m unit`; expected: valid content remains, the warning names the bad path, and tolerant skip behavior is preserved. Dependencies/constraints: keep the tolerant skip behavior (safe-to-fail); only add observability, do not turn it into a hard failure.
- [ ] **WFZ-03** (P2) Escape raw markdown in the `markdown_to_html` fallback to prevent injecting unescaped HTML into the generated site. Evidence: src/website/templates.py:35-38 — on conversion failure it returns `f\"<pre>{markdown_text}</pre>\"` with the raw text unescaped, while the same module already escapes user-facing strings via `escape_html(course_name)` at src/website/templates.py:115. Observable outcome: when `markdown.markdown` raises, the fallback output HTML-escapes `<`, `>`, `&` in the source text so embedded tags cannot break page structure or inject markup. Acceptance probe (from repo root): add a conversion-failure case containing `<script>`/`<b>` through the repository’s sanctioned failure-injection seam, then run `uv run pytest tests/test_website_templates.py -m unit`; expected: fallback output contains escaped entities and no raw script element, inside the existing `<pre>` wrapper. Dependencies/constraints: reuse the module's existing `escape_html` helper rather than adding a new dependency; keep the `<pre>` wrapper contract.
