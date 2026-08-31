# REVIEW_LOG — 2026-08-31 (agent-ergonomics deep pass)

Agent: curriculum lane, agent-erg fleet. Doctrine: design for the agent who arrives cold.

## Phase 0 — Preflight
- Repo: /Volumes/external_drive/Git/projects/ongoing/docxology/curriculum (canonical; matches brief). Branch main, in sync with origin/main before work.
- Dirty files at dispatch: 206 (35 modified = all tracked .pyc bytecode; 205 untracked = generated AGENTS.md/README.md pairs under scripts/output/, output/, docs/manuscript/, .cursorrules). Treated as pre-existing; none staged except files authored this pass.

## Phase 1 — Cold-start audit
Entry docs read: README.md, then AGENTS.md. Orientation tasks attempted using docs only:
- (a) Current status: FAIL before pass. "Recent Updates (Dec 2024)" was the newest status signal — 8+ months stale; no dated verified-state line anywhere.
- (b) What next: FAIL before pass. No backlog/TODO file existed (confirmed: none at repo root).
- (c) Primary verification: PASS with wrong metadata. `uv run pytest --collect-only` works (658 collected, 53.8s on this drive) but docs claimed "~540 tests across 25 files".

Doc-surface sweep (24 README/AGENTS.md files checked):
- Broken relative links: 1 (docs/TROUBLESHOOTING.md → src/llm/TROUBLESHOOTING.md used ../../ prefix). All other links across README/AGENTS/SETUP/docs/*.md resolve.
- Stale claims: test counts (~540/25 in 3 places), output/ "gitignored" (no .gitignore exists; 5 output/ files ARE tracked), AGENTS.md layout root labeled "biology/".
- Duplicated fact-classes: commands duplicated between README and AGENTS.md (acceptable: README=human hub, AGENTS.md=agent hub; both correct after this pass).
- Dead weight: none found — docs/manuscript/MANUSCRIPT_STATUS.md correctly declares no manuscript applies (tool repo).

## Phase 3 — Implemented
- README.md: test count corrected w/ verification command + date; structure block corrected (tests count, docs count, output/ tracking caveat).
- AGENTS.md: test counts corrected (2 places, dated); "Recent Updates" section given dated verified-state line + note about untracked doc-pair noise; layout root relabeled "curriculum/"; output/ gitignored claims corrected (2 places).
- docs/TROUBLESHOOTING.md: link path fixed.
- TODO.md created (Minor fixed-marked, Medium, Major deferred with reasons).

## Phase 4 — Verify
- Re-ran link checker over touched docs: 0 broken.
- Test collection re-verified: 658 collected.
- Fast gate: repo declares none; full pytest run not executed (integration tests require Ollama; external-drive runtime ~minutes–hours). Verification command for a human: `uv run pytest`.

## Follow-up pass — 2026-08-31 (same day; "accomplish all deferred work")

Scope: complete every Major + Medium item deferred or TODO'd in the morning pass.

### Done
1. **.gitignore added** (was completely absent). Covers __pycache__/, *.pyc, caches, .venv, .DS_Store, .coverage, runtime logs (output/logs/, scripts/output/logs/), scripts/test_reports/, and the generated AGENTS.md/README.md stub pairs (which self-declare "gitignored, never committed").
2. **Untracked 299 runtime artifacts** via `git rm -r --cached` (commit 045875b): 194 tracked .pyc files, 95 pipeline logs + test-reports, all tracked .DS_Store files, .coverage. Curriculum content (outlines, session materials, websites) remains tracked. `git status --porcelain` dropped 206 → 1 (the 1 is a pre-existing .cursorrules/README.md edit not authored by this fleet).
3. **pytest marker bug fixed (found by verifying the TODO)**: pytest.ini declares `unit`/`integration`/`slow` markers, but 28 of 35 test files carried no marker — so `uv run pytest -m unit` collected 658 and deselected ALL 658 ("658 deselected / 0 selected"). Annotated all 28 unit-only files with `pytestmark = pytest.mark.unit` (integration-marked files left untouched). The fast gate `pytest -m unit` now actually selects the unit suite.

### Verified
- Before fix: `pytest -m unit` → "658 deselected / 0 selected" (observed, exit 0).
- After fix: `pytest -m unit` run executed in this session; result recorded in the fleet report.
- `git ls-files | grep -c '\.pyc$'` → 0.
- Link check over touched docs → 0 broken.

### Still open (owner decisions, scoped in TODO.md)
- Whether to wire black/flake8 into a fast pre-push hook (tools already in dev deps).
- Full integration suite requires Ollama + gemma3:4b — run before any release/tag.

## Round 2 — 2026-08-31 (continuation: execute all open TODO items)

- Verified the marker TODO and found the bug was real: before the fix, `uv run pytest -m unit` printed "658 deselected / 0 selected" (observed directly). Annotated all 28 unmarked test files with `pytestmark = pytest.mark.unit` (AST-verified insertion after imports; +1 `import pytest` where missing). Integration-marked files untouched.
- Fast gate result: `uv run pytest -m unit` → **613 passed, 45 deselected, 0 failed** (407s on this external drive).
- Remaining open items are owner decisions (pre-push lint hook; integration suite requires Ollama) — scoped with acceptance lines in TODO.md, not implemented.
