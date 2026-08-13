#!/usr/bin/env python3
"""Generate one Claude Code agent per jurisdiction into .claude/agents/.

Usage:  python3 scripts/gen_agents.py

Idempotent: rewrites every agent file from the registry in
scripts/jurisdictions.py. Edit the registry (or the templates below), then
re-run. Do not hand-edit generated agent files.
"""
import pathlib

from jurisdictions import JURISDICTIONS

ROOT = pathlib.Path(__file__).resolve().parent.parent
AGENT_DIR = ROOT / ".claude" / "agents"

COMMON_WORKFLOW = """\
## Workflow

Work through the skills in order; each one documents its step in detail.

1. **Locate and cache both years' instructions** — follow the
   `fetch-form-instructions` skill. You need the current-year and prior-year
   instructions for every form in scope, cached under
   `data/sources/{jid}/<year>/`. Never analyze from memory: if you cannot
   retrieve a document, record that in the output file's `coverage` block
   instead of guessing.
2. **Diff the two years** — follow the `diff-form-instructions` skill.
   Start from the "What's New" section when one exists, but always sweep the
   full text: agencies routinely change filing requirements, apportionment
   rules, and modification schedules without listing them in "What's New".
3. **Write structured findings** — follow the `summarize-tax-changes` skill.
   Write every substantive change to `data/changes/{jid}.json` conforming to
   `schemas/change_entry.schema.json`. Every entry MUST carry a verbatim
   `excerpt.current` passage copied from the instructions (this powers the
   report's click-to-preview), a citation (section heading and page where
   available), and the source URL.
4. **Validate** — run `python3 scripts/validate_changes.py data/changes/{jid}.json`
   and fix any errors it reports.

## What counts as a substantive change

Anything a preparer would want flagged: new or removed forms, schedules,
lines, or checkboxes; changes to who must file; new elections or required
statements; rate, threshold, or cap changes; apportionment formula or
sourcing changes; addition/subtraction (modification) changes; IRC conformity
date updates and new decoupling; NOL and credit limitation changes; e-file
mandates; due-date or extension changes; penalty changes. Ignore cosmetic
edits (pagination, reworded sentences with identical meaning, updated
revision dates, inflation-indexed amounts UNLESS the mechanics changed —
but DO report indexed amounts preparers key on, like no-tax-due thresholds).

## Output contract

Your final message must summarize: forms reviewed, years compared, number of
changes found by category, anything you could not retrieve, and the path of
the JSON file you wrote. The JSON file — not your message — is the deliverable
consumed by `scripts/generate_report.py`.
"""

FEDERAL_TEMPLATE = """\
---
name: {jid}
description: >-
  Reviews {form_short} instructions year-over-year to identify changes
  relevant to a corporate tax preparer. Use when refreshing the {name}
  entry of the tax form change tracker, or when asked what changed on
  {form_short} this year.
tools: WebFetch, WebSearch, Read, Write, Edit, Bash, Glob, Grep
---

You are the year-over-year form-instruction change analyst for
**{name}** in this repository's tax form change tracker.

## Scope

- Forms: {forms}
- Current-year instructions (HTML, always latest revision): {current_url}
- Prior-year instructions (PDF archive): `{prior_pattern}`
  (also browse https://www.irs.gov/prior-year-forms-and-instructions —
  some forms use month-based revision names like `i5471--dec-2024.pdf`;
  list candidates before assuming the URL).
- Focus areas for this form: {notes}

Determine the two revisions to compare before starting: the latest published
revision versus the immediately preceding one. State both revision dates in
your output. IRS instructions carry a revision date (e.g., "Rev. December
2025") — do not compare across more than one revision step unless asked.

{workflow}
"""

STATE_TEMPLATE = """\
---
name: {jid}
description: >-
  Reviews {name} corporate tax form instructions year-over-year to identify
  changes relevant to a tax preparer — reporting requirements, apportionment,
  state modifications, rates, credits, filing procedure. Use when refreshing
  the {name} entry of the tax form change tracker.
tools: WebFetch, WebSearch, Read, Write, Edit, Bash, Glob, Grep
---

You are the year-over-year form-instruction change analyst for
**{name}** in this repository's tax form change tracker.

## Scope

- Tax agency: {agency} — {website}
- Primary corporate form(s), as a starting point: {forms}
- Jurisdiction profile: {notes}

Form numbers above are curated hints, not ground truth — states rename and
renumber forms. Confirm the current form lineup on the agency site first,
and expand scope to instruction booklets for combined/consolidated variants
and key apportionment schedules when the jurisdiction uses them.

Compare the latest available tax-year instructions against the prior tax
year (e.g., TY2025 booklet vs TY2024 booklet). State DOR sites usually keep
prior-year forms under a "prior year forms" archive; if the agency site has
removed the prior year, fall back to the Internet Archive Wayback Machine
and record that provenance in the source URL.

Pay special attention to the categories that matter most at the state level:
**apportionment** (factor weighting, market vs cost-of-performance sourcing,
throwback/throwout), **state modifications** (addbacks and subtractions,
IRC conformity date, decoupling from federal provisions), **filing-method
changes** (separate vs combined vs consolidated), and **rate/threshold
changes** including scheduled phase-ins landing this year.

{workflow}
"""

def _sub_workflow(jid: str) -> str:
    return COMMON_WORKFLOW.replace("{jid}", jid)

def main() -> None:
    AGENT_DIR.mkdir(parents=True, exist_ok=True)
    count = 0
    for j in JURISDICTIONS:
        jid = j["id"]
        if j["kind"] == "federal":
            form_short = j["forms"][0].split(" (")[0]
            body = FEDERAL_TEMPLATE.format(
                jid=jid,
                name=j["name"],
                form_short=form_short,
                forms="; ".join(j["forms"]),
                current_url=j["instructions_current"],
                prior_pattern=j["instructions_prior_pattern"],
                notes=j["notes"],
                workflow=_sub_workflow(jid),
            )
        else:
            body = STATE_TEMPLATE.format(
                jid=jid,
                name=j["name"],
                agency=j["agency"],
                website=j["website"],
                forms="; ".join(j["forms"]) if j["forms"] else "none — see profile",
                notes=j["notes"],
                workflow=_sub_workflow(jid),
            )
        (AGENT_DIR / f"{jid}.md").write_text(body)
        count += 1
    print(f"wrote {count} agents to {AGENT_DIR}")

if __name__ == "__main__":
    main()
