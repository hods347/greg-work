---
name: summarize-legislation
description: >-
  Write structured legislation entries in data/legislation/<legis-id>.json —
  dual-audience summaries (in-house company vs accounting firm), return
  mapping fields, categories, and verbatim bill excerpts. Use after
  monitoring finds new laws, or when editing existing legislation files.
---

# Summarize legislation

Output: `data/legislation/<legis-id>.json` conforming to
`schemas/legislation_entry.schema.json` (read it before writing). Validate
with `python3 scripts/validate_changes.py data/legislation/<legis-id>.json`.

## One law, how many entries?

Default is one entry per law. Split a single act into multiple entries only
when its provisions differ materially in category, impact, or effective
year (e.g., a mega-act's domestic expensing provisions vs its international
regime changes). Use ids like `obbba-domestic-business-provisions`,
`obbba-international-provisions` so the family is visible.

## The two summaries

Same facts, different reader. Both are 2-5 sentences, plain language,
naming code sections, forms, and dates. Do not write one and lightly reword
it — the reader's decisions differ.

**`summary_for_company`** — the in-house corporate tax department. Answer:
what changes on OUR returns and provision, starting which year; what data,
elections, or statements we need; any deadline or transition-date to
calendar. Assume one taxpayer with continuing facts.
("Beginning with the 2025 return, domestic R&E is deductible again under
new §174A; decide deduct-vs-amortize and consider the retroactive
small-business election by …")

**`summary_for_firm`** — an accounting firm serving many clients. Answer:
which client segments are affected (size, industry, filing profile); what
changes across the book of business; what to communicate proactively and
what planning opportunities exist.
("All corporate clients with R&E; small-business clients (≤$31M gross
receipts) can amend 2022-2024 — triage the client list for refund
opportunities before …")

## Return mapping (feeds future return-data comparison)

- `affected_returns`: the specific forms and schedules touched, named the
  way return software names them ("Form 1120", "Form 5471 Sch. I-1",
  "CA Form 100"). Be exhaustive — this is the join key.
- `related_form_jurisdictions`: the form-layer ids (e.g., ["federal-1120"]).
- `first_return_year_affected`: the first tax year whose filed return
  changes. For a law effective for tax years beginning after 12/31/2025,
  that is 2026.

## Everything else

Category, impact, and status follow the same rules as form-instruction
changes (see `summarize-tax-changes`): the same category taxonomy applies;
impact is judged by breadth × dollars; `verified` requires a verbatim
excerpt from a primary source retrieved this run. `excerpt.passage` holds
the operative bill language; use `excerpt.amended_from` for the replaced
statutory text when a before/after is illuminating.
