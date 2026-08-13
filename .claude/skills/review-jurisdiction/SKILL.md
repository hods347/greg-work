---
name: review-jurisdiction
description: >-
  Run the full year-over-year review for one jurisdiction: launch its agent,
  validate its output, and refresh the HTML report. Use for requests like
  "review California", "what changed on Form 5471 this year", or
  /review-jurisdiction <id>.
---

# Review one jurisdiction

Argument: a jurisdiction id from `scripts/jurisdictions.py`
(`federal-1120`, `federal-5471`, `federal-8865`, `federal-8858`,
`state-<2-letter>`, `state-dc`, `state-nyc`). If the user gave a name
("California", "Form 8865"), resolve it against the registry; if ambiguous,
ask.

## Steps

1. Confirm the agent exists: `.claude/agents/<id>.md`. If not, re-run
   `python3 scripts/gen_agents.py` (and add the jurisdiction to the registry
   first if it's genuinely new).
2. Launch the jurisdiction's agent via the Agent tool
   (`subagent_type: "<id>"`). Tell it which tax year to treat as current if
   the user specified one; otherwise it compares the latest published
   revision to the prior one. The agent fetches, diffs, and writes
   `data/changes/<id>.json` per its own instructions.
3. When the agent finishes, run
   `python3 scripts/validate_changes.py data/changes/<id>.json`.
   If validation fails, fix the file (or re-brief the agent) before
   proceeding.
4. Regenerate the report: `python3 scripts/generate_report.py`.
5. Report back to the user: changes found by category, the high-impact
   items by name, any coverage gaps the agent recorded, and where the
   updated report lives.

## Notes

- Network-restricted sessions: if the agent reports it could not retrieve
  sources, keep its entries `unverified` and its gaps recorded — do not fill
  holes from memory. Say plainly which sources were unreachable.
- Multiple jurisdictions requested at once → use the
  `review-all-jurisdictions` skill instead, with the requested subset.
