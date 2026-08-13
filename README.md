# Tax Form Changes Tracker

An agent-driven system that reviews corporate tax form instructions
year-over-year — federal Forms **1120, 5471, 8865, 8858** and **every state
jurisdiction** — and reports the changes that matter to a tax preparer:
reporting requirements, apportionment rules, state modifications, rates and
thresholds, credits, NOL limits, filing methods, and more.

The output is an interactive HTML report (`report/index.html`) where each
change carries an AI-generated summary, and **clicking a change pops out the
verbatim passage from the actual form instructions** with its citation and a
link to the source document.

## How it works

```
.claude/agents/<jurisdiction>.md      one agent per jurisdiction (56 total)
        │  fetch → diff → summarize (guided by the skills below)
        ▼
data/sources/<jurisdiction>/<year>/   cached instruction PDFs/HTML + text
data/changes/<jurisdiction>.json      structured findings (schema-validated)
        │
        ▼  scripts/generate_report.py
report/index.html                     self-contained interactive report
```

### Agents (one per jurisdiction)

Generated from the registry in `scripts/jurisdictions.py` by
`scripts/gen_agents.py` — do not hand-edit agent files; edit the registry or
templates and re-run the generator.

- `federal-1120`, `federal-5471`, `federal-8865`, `federal-8858`
- `state-al` … `state-wy` (all 50 states), `state-dc`, `state-nyc`

Each agent knows its jurisdiction's agency, primary forms, and regime
profile (combined vs separate filing, conformity style, gross-receipts
regimes for NV/OH/TX/WA, etc.), and follows the shared fetch → diff →
summarize → validate workflow.

### Skills

| Skill | Purpose |
|---|---|
| `fetch-form-instructions` | Locate & cache current + prior year instructions (IRS URL patterns, state DOR archives, Wayback fallback), extract text with page markers |
| `diff-form-instructions` | Three-pass comparison: "What's New", structural sweep, targeted section diffs; substantive-vs-cosmetic rules |
| `summarize-tax-changes` | Write schema-conforming change entries: preparer-focused summaries, categories, impact, verbatim excerpts, verified/unverified discipline |
| `generate-changes-report` | Rebuild and QA the HTML report |
| `review-jurisdiction` | Orchestrate one jurisdiction end-to-end (`/review-jurisdiction state-ca`) |
| `review-all-jurisdictions` | Fan out the annual full-cycle run across all agents, then rebuild the report |

## Usage

```bash
# Review one jurisdiction (in a Claude Code session):
/review-jurisdiction federal-1120
/review-jurisdiction state-ca

# Full annual cycle:
/review-all-jurisdictions

# Rebuild the report manually:
python3 scripts/validate_changes.py && python3 scripts/generate_report.py

# Regenerate agents after editing the registry:
python3 scripts/gen_agents.py
```

Open `report/index.html` in any browser — it is fully self-contained
(no network requests), so it can be emailed or published as-is.

## Data contract

Every change entry (see `schemas/change_entry.schema.json`) requires a
verbatim `excerpt.current` passage, a source citation, a category from the
fixed taxonomy, an impact rating, and a `status`:

- **verified** — the excerpt was copied from a document retrieved during the
  review. This is the only trustworthy state.
- **unverified** — drafted without confirming against a retrieved source.
  The report badges these prominently.

## ⚠ Current data is demo data

The three change files now in `data/changes/` (federal-1120, state-ca,
state-tx) were produced in a **network-restricted session**: entries are
AI-recalled, marked `unverified`, and their excerpts are illustrative rather
than verbatim. They exist to exercise the pipeline and the report UI.
Run the agents in a session with web access to replace them with verified
findings before relying on anything here.
