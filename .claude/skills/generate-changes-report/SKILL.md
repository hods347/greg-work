---
name: generate-changes-report
description: >-
  Build the interactive HTML tax form changes report from data/changes/*.json.
  Use after any jurisdiction review updates its change file, or when asked to
  regenerate, restyle, or publish the change-tracker report page.
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

- Header stats: jurisdictions reviewed, total changes, high-impact count,
  and the review-date range.
- Sidebar: every jurisdiction from `scripts/jurisdictions.py` with its change
  count; jurisdictions with no change file yet are listed as "not reviewed"
  so coverage gaps stay visible.
- Filters: free-text search, category chips, impact chips, and a
  verified-only toggle.
- Change cards: title, AI-generated summary, category/impact/status badges,
  form and years compared.
- **Click-to-preview**: clicking a card opens a modal showing the verbatim
  passage from the actual instructions (`excerpt.current`) rendered as a
  document snippet, the prior-year passage beside it when present, the
  citation (document, section, page), and a link to the source URL.
- Unverified entries carry a visible "UNVERIFIED — confirm against source"
  badge in both card and modal.

## Rules

- Never hand-edit `report/index.html`; it is generated. Change
  `scripts/generate_report.py` for layout/behavior changes and change files
  for content changes, then regenerate.
- Run the validator first, always — the generator assumes valid input.
- After regenerating in an interactive session, send the file to the user
  (rendered) or publish it as an artifact if they want a shareable link.
