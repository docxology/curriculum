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
