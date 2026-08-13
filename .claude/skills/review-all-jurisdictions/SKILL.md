---
name: review-all-jurisdictions
description: >-
  Fan out year-over-year reviews across many or all jurisdictions (federal
  forms plus states), then rebuild the HTML change report. Use for "review
  everything", "refresh all states", or an annual full-cycle run.
---

# Review all jurisdictions

This is the annual full-cycle run: every jurisdiction's agent fetches, diffs,
and writes its change file; then the report is rebuilt once at the end.

## Scope selection

Default scope is every id in `scripts/jurisdictions.py`. Honor subsets the
user asks for ("just the states", "federal only", "the combined-reporting
states"). List the scope before starting so the user sees the plan.

## Execution

Run jurisdiction agents in parallel batches via the Agent tool
(`subagent_type` = the jurisdiction id), roughly 4-6 at a time — state DOR
sites and irs.gov tolerate this fine, and it keeps failures diagnosable.
Federal forms first (their findings give state agents useful context about
what conformity items to look for), then states alphabetically.

If the user has opted into multi-agent orchestration (ultracode / an explicit
workflow request), the Workflow tool with a `pipeline()` over jurisdiction
ids is the better engine: fetch/diff/write per item, with a final barrier
before report generation. Otherwise plain batched Agent calls are fine.

## Per-jurisdiction contract

Each agent must end with `data/changes/<id>.json` written or a coverage gap
recorded. Track three buckets as results come in:
- **completed** — file written and `validate_changes.py` passes;
- **degraded** — file written but with `unverified` entries or gaps
  (typical in network-restricted sessions);
- **failed** — no file; re-run once, then record and move on.

## Finish

1. `python3 scripts/validate_changes.py` (all files).
2. `python3 scripts/generate_report.py`.
3. Summarize for the user: jurisdictions completed/degraded/failed, total
   changes by category, the top high-impact changes across all
   jurisdictions, and the report location. Commit the refreshed
   `data/changes/` and `report/index.html` if the session is push-enabled
   and the user expects it.
