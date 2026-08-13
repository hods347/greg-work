---
name: summarize-tax-changes
description: >-
  Turn diffed tax-instruction findings into structured change entries in
  data/changes/<jurisdiction>.json — preparer-focused summaries with verbatim
  source excerpts, categories, and impact ratings. Use after diffing a
  jurisdiction's instructions, or when editing/normalizing existing change
  files.
---

# Summarize tax changes

Output file: `data/changes/<jurisdiction-id>.json`, one per jurisdiction,
conforming to `schemas/change_entry.schema.json` (read it before writing).
Validate with `python3 scripts/validate_changes.py data/changes/<id>.json`.

## Writing the summary

The `summary` field is what a preparer reads first in the report. Write 2-5
sentences that answer, in order:
1. **What changed** — concretely, with the numbers ("The Section 163(j)
   limitation is again computed without depreciation and amortization"),
   not vaguely ("interest limitation rules were updated").
2. **Versus what** — the prior-year treatment, in one clause.
3. **What the preparer does differently** — new line, new statement, new
   election, different computation, different attachment.

Plain language, no hedging, no marketing tone. Name forms, lines, schedules,
and IRC/state code sections explicitly. If effectivity is odd (mid-year
acquisition dates, tax years beginning after a date), put it in `effective`
and mention it in the summary.

## Choosing category

Use the schema's enum. Disambiguation rules:
- Rate/threshold/cap amount changes → `rate-or-threshold`, even when a state
  modification implements them.
- Changes to how income or deductions are computed (expensing, capitalization,
  interest limitations, inclusion regimes) → `income-or-deduction`.
- Changes to addbacks/subtractions or decoupling mechanics →
  `state-modification`; a bare IRC conformity-date update → `conformity`.
- Factor weighting, sourcing method, throwback/throwout → `apportionment`.
- Separate/combined/consolidated regime changes → `filing-method`;
  e-file mandates, signature, payment mechanics → `filing-procedure`.
- A brand-new schedule/form → `new-form-or-schedule` even if it also changes
  reporting requirements; a changed obligation on an existing form →
  `reporting-requirement`.

## Choosing impact

- `high`: changes the tax computed, who must file, or the filing method for
  a broad class of filers (rate changes, apportionment formula changes,
  combined-reporting adoption, major decoupling).
- `medium`: new lines/statements/elections, notable credit or NOL changes,
  threshold changes affecting many but not most filers.
- `low`: narrow-industry items, procedural conveniences, clarifications that
  confirm existing practice.

## Status discipline (load-bearing)

`"status": "verified"` is a promise that `excerpt.current` was copied
verbatim from a document retrieved during this run and cited in `source`.
Anything reconstructed from memory, secondary sources, or a summary of a
summary is `"unverified"` — the report displays these with a warning badge.
Never upgrade status without re-copying the passage from the cached source.

## Excerpts

- `excerpt.current`: exact text from the current-year instructions — this is
  what pops out when a user clicks the change in the report. Keep enough
  context to stand alone (usually 1-3 sentences or the full bullet).
- `excerpt.prior`: the prior-year counterpart, verbatim, or `null` when the
  text is entirely new. Including it lets the report show a then/now view.
- Preserve the source's own wording exactly; mark elisions with "…". Fix
  only PDF-extraction artifacts (broken hyphen-ation, stray line breaks) —
  never paraphrase inside an excerpt.

## Stable ids

`id` is kebab-case and stable across re-runs ("ca-nol-suspension-2024-2026",
not "change-3"), so re-reviews update entries instead of duplicating them.
When re-running a jurisdiction, load the existing file first and carry ids
forward for changes that persist.
