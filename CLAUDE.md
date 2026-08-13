# Tax Form Changes Tracker — working notes for Claude

Purpose: review corporate tax form instructions year-over-year (federal
1120/5471/8865/8858 + all states) and publish preparer-relevant changes in
`report/index.html` with click-to-preview source passages.

## Pipeline (always in this order)

1. Jurisdiction agent (`.claude/agents/<id>.md`) fetches + diffs + writes
   `data/changes/<id>.json`.
2. `python3 scripts/validate_changes.py` — must pass before generating.
3. `python3 scripts/generate_report.py` — rebuilds `report/index.html`.

## Hard rules

- `report/index.html` and `.claude/agents/*.md` are **generated** — never
  hand-edit. Edit `scripts/generate_report.py` / `scripts/jurisdictions.py` +
  `scripts/gen_agents.py` and regenerate.
- `scripts/jurisdictions.py` is the single source of truth for jurisdiction
  ids, names, agencies, and profiles. Adding a jurisdiction = add it there,
  re-run `gen_agents.py`.
- A change entry may be `"status": "verified"` ONLY if its excerpt was copied
  verbatim from a document retrieved in that run. No exceptions; when in
  doubt, `unverified`.
- Change ids are stable kebab-case; re-reviews update entries in place rather
  than appending duplicates.
- Cached source documents live under `data/sources/` (gitignored); change
  files and the report are committed.

## Testing the report

Headless render check:
`/opt/pw-browsers/chromium --headless --no-sandbox --screenshot=/tmp/r.png file://$PWD/report/index.html`
For interaction tests use `playwright-core` with
`executablePath: '/opt/pw-browsers/chromium'`.
