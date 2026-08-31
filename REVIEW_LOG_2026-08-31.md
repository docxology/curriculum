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
