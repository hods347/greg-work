---
name: generate-changes-report
description: >-
  Build the interactive HTML tax changes report from data/changes/*.json and
  data/legislation/*.json. Use after any jurisdiction review or legislation
  monitoring run updates its data file, or when asked to regenerate, restyle,
  or publish the change-tracker report page.
---

# Generate the changes report

One command:

```bash
python3 scripts/validate_changes.py && python3 scripts/generate_report.py
```

Output: `report/index.html` — fully self-contained (inline CSS/JS, data
embedded as JSON, no external requests), so it can be opened from disk,
emailed, or published as an artifact unchanged.

## What the page does

- Two tabs: **Form instructions** (annual YoY instruction changes from
  `data/changes/`) and **Legislation** (newly enacted laws from
  `data/legislation/`, with a Company/Firm toggle that switches every card
  between `summary_for_company` and `summary_for_firm`).
- Header stats per tab: jurisdictions reviewed/monitored, total items,
  high-impact count.
- Sidebar: every jurisdiction from `scripts/jurisdictions.py` with its
  count; jurisdictions with no data file yet show "—" so coverage gaps stay
  visible.
- Filters: free-text search, category chips, impact chips, and a
  verified-only toggle.
- Change cards: title, AI-generated summary, category/impact/status badges,
  form and years compared.
- **Click-to-preview**: clicking a card opens a modal showing the verbatim
  passage rendered as a document snippet — for instruction changes,
  `excerpt.current` with the prior-year text; for laws, `excerpt.passage`
  (operative bill language) with the pre-amendment statute plus BOTH
  audience summaries — along with the citation and source links.
- Unverified entries carry a visible "UNVERIFIED — confirm against source"
  badge in both card and modal.

## Rules

- Never hand-edit `report/index.html`; it is generated. Change
  `scripts/generate_report.py` for layout/behavior changes and change files
  for content changes, then regenerate.
- Run the validator first, always — the generator assumes valid input.
- After regenerating in an interactive session, send the file to the user
  (rendered) or publish it as an artifact if they want a shareable link.
