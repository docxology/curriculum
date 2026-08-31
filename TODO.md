# TODO — curriculum

Backlog for agent-ergonomics and repo hygiene work. One line per entry.
Entries added 2026-08-31 by the agent-ergonomics pass (see REVIEW_LOG_2026-08-31.md).

## Minor

- [ ] docs/TROUBLESHOOTING.md link to src/llm/TROUBLESHOOTING.md was broken (../../ instead of src/) — FIXED 2026-08-31
- [ ] README.md / AGENTS.md test counts said "~540 tests across 25 files"; actual 658 collected across 35 files — FIXED 2026-08-31 (claims now dated + carry verification command)
- [ ] AGENTS.md project-layout code block labeled repo root "biology/" — FIXED 2026-08-31 (relabeled "curriculum/ repo root")
- [ ] docs claims said `output/` is "gitignored" but the repo has no .gitignore and 5 files under output/ are git-tracked — FIXED 2026-08-31 (claims corrected; see Major below)

## Medium

- [ ] AGENTS.md "Recent Updates" section was frozen at Dec 2024 with no date-visible status; now has a verified-state line (2026-08-31) — keep updating it as a dated log, or convert to a STATUS.md appended-only log
- [ ] ~205 untracked files under scripts/output/ and output/ (generated AGENTS.md/README.md doc pairs) make `git status` noise for cold agents; either add a .gitignore rule for generated doc pairs or track them deliberately

## Major

- [ ] 194 compiled .pyc files are git-tracked (e.g. src/*/__pycache__/*.pyc, tests/__pycache__/*.pyc) and show as permanently modified in git status. Fix: add a .gitignore covering __pycache__/, then `git rm -r --cached` the .pyc files. Requires owner decision because it rewrites what CI sees and touches 194 tracked paths (deliberately NOT done in this docs pass).
- [ ] No .gitignore exists at all. Output/, .venv, __pycache__ are unprotected. Same owner decision as above (source-hygiene change, out of docs-pass scope).
