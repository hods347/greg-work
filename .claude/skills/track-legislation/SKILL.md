---
name: track-legislation
description: >-
  Run legislation monitoring for one, several, or all jurisdictions and
  refresh the report — the recurring (monthly/quarterly) counterpart to the
  annual form-instruction review. Use for "check for new tax laws",
  "any new legislation this quarter", or /track-legislation [ids|all].
---

# Track legislation

Arguments: one or more legislative jurisdiction ids (`legis-federal`,
`legis-ca`, `legis-nyc`, …), or `all`. Resolve names against
`scripts/jurisdictions.py` (`LEGIS_JURISDICTIONS`). No argument + no context
→ default to `legis-federal` plus any jurisdictions that already have files
in `data/legislation/` (i.e., refresh what's being tracked).

## Steps

1. Agents live at `.claude/agents/legis-<id>.md`; if missing, re-run
   `python3 scripts/gen_agents.py`.
2. Launch each jurisdiction's monitor agent via the Agent tool
   (`subagent_type: "legis-<id>"`), in parallel batches of 4-6 when running
   many. Pass along any user-specified window ("since July 1"); otherwise
   agents derive the window from their existing file.
3. Validate: `python3 scripts/validate_changes.py` (validates both layers).
4. Rebuild: `python3 scripts/generate_report.py` — legislation appears on
   the report's Legislation tab with the company/firm audience toggle.
5. Summarize for the user: window covered per jurisdiction, new laws found
   (by impact), anything unverified or gapped, and the report location.

## Cadence guidance

This layer is designed to run repeatedly: monthly or quarterly for active
jurisdictions, and immediately after known major events (federal
reconciliation bills, state budget seasons — most legislatures adjourn
May-July, so a late-summer sweep catches the bulk of state activity).
Because each file's `window_end` becomes the next run's `window_start`,
frequent runs stay cheap: agents only search the gap.

## Relationship to the form-instruction layer

Legislation entries answer "what did lawmakers change" as it happens; the
annual form-instruction review answers "how did the agency implement it on
the forms". The `related_form_jurisdictions` field ties each law to the
form-layer jurisdiction so the two views can be cross-referenced — when a
tracked law later surfaces in a form's instructions, the instruction-change
entry should cite the same public-law/chapter number.
