# Tax Form Changes Tracker

An agent-driven system with **two layers** of corporate tax change tracking:

1. **Form-instruction changes (annual).** Reviews corporate tax form
   instructions year-over-year — the federal corporate suite (**1120,
   1120-PC**, their separately-instructed schedules **D, M-3, O, PH, UTP**,
   international forms **5471, 5472, 8865, 8858, 1118, 926, 8975, 8991,
   8992, 8993**, and computation/disclosure forms **3800, 8990, 4626, 4562,
   4797, 3115, 2220, 7004, 1125-A/E, 8886**) and **every state
   jurisdiction** — and reports the changes that matter to a tax preparer:
   reporting requirements, apportionment rules, state modifications, rates
   and thresholds, credits, NOL limits, filing methods.
2. **Legislation monitoring (recurring).** Separate agents per jurisdiction
   watch for **newly enacted legislation** with corporate income tax return
   impact throughout the year. Every law gets two summaries — one written
   for an in-house corporate tax department, one for an accounting firm
   serving many clients — plus return-mapping fields
   (`affected_returns`, `first_return_year_affected`) designed to be joined
   against tax return preparation data later.

The output is one interactive HTML report (`report/index.html`) with a tab
per layer. Each entry carries an AI-generated summary, and **clicking it
pops out the verbatim passage** — from the actual form instructions, or the
operative bill language with the pre-amendment statute — with its citation
and source links. The Legislation tab has a **Company view / Firm view**
toggle that switches every summary to the chosen audience.

## How it works

```
.claude/agents/<jurisdiction>.md      form-instruction agents (79)
.claude/agents/legis-<id>.md          legislation monitors (53)
        │  fetch/search → diff/verify → summarize (guided by the skills below)
        ▼
data/sources/<jurisdiction>/<year>/   cached instruction PDFs/HTML + text
data/changes/<jurisdiction>.json      instruction findings (schema-validated)
data/legislation/<legis-id>.json      enacted-law findings (schema-validated)
        │
        ▼  scripts/generate_report.py
report/index.html                     self-contained two-tab report
```

### Agents

Generated from the registry in `scripts/jurisdictions.py` by
`scripts/gen_agents.py` — do not hand-edit agent files; edit the registry or
templates and re-run the generator.

**Form-instruction layer (79):**
- Core returns: `federal-1120`, `federal-1120-pc`
- 1120 schedules with their own instructions: `federal-1120-sch-d`,
  `federal-1120-sch-m3` (incl. 8916-A), `federal-1120-sch-o`,
  `federal-1120-sch-ph`, `federal-1120-sch-utp`
- International: `federal-5471`, `federal-5472`, `federal-8865`,
  `federal-8858`, `federal-1118`, `federal-926`, `federal-8975`,
  `federal-8991` (BEAT), `federal-8992` (GILTI/NCTI), `federal-8993` (§250)
- Computation & disclosure: `federal-3800`, `federal-8990` (§163(j)),
  `federal-4626` (CAMT), `federal-4562`, `federal-4797`, `federal-3115`,
  `federal-2220`, `federal-7004`, `federal-1125` (1125-A/E), `federal-8886`
- `state-al` … `state-wy` (all 50 states), `state-dc`, `state-nyc`

**Legislation layer (53):**
- `legis-federal` (one Congress covers all four federal forms)
- `legis-al` … `legis-wy`, `legis-dc`, `legis-nyc`

Each agent knows its jurisdiction's agency, primary forms, and regime
profile (combined vs separate filing, conformity style, gross-receipts
regimes for NV/OH/TX/WA, etc.). Instruction agents follow fetch → diff →
summarize → validate; legislation monitors follow a rolling-window
search → primary-source verify → dual-audience summarize → validate
workflow where each run picks up where the last `window_end` left off.

### Skills

| Skill | Purpose |
|---|---|
| `fetch-form-instructions` | Locate & cache current + prior year instructions (IRS URL patterns, state DOR archives, Wayback fallback), extract text with page markers |
| `diff-form-instructions` | Three-pass comparison: "What's New", structural sweep, targeted section diffs; substantive-vs-cosmetic rules |
| `summarize-tax-changes` | Write schema-conforming change entries: preparer-focused summaries, categories, impact, verbatim excerpts, verified/unverified discipline |
| `generate-changes-report` | Rebuild and QA the two-tab HTML report |
| `review-jurisdiction` | Orchestrate one instruction review end-to-end (`/review-jurisdiction state-ca`) |
| `review-all-jurisdictions` | Fan out the annual full-cycle instruction run, then rebuild the report |
| `monitor-legislation` | Search strategy + primary-source verification for newly enacted laws |
| `summarize-legislation` | Write dual-audience legislation entries with return-mapping fields |
| `track-legislation` | Run legislation monitoring for one/many/all jurisdictions (`/track-legislation legis-federal legis-ca`) — the recurring counterpart to the annual review |

## Usage

```bash
# Review one jurisdiction's form instructions (in a Claude Code session):
/review-jurisdiction federal-1120
/review-jurisdiction state-ca

# Full annual instruction cycle:
/review-all-jurisdictions

# Recurring legislation sweeps (monthly/quarterly, or after budget season):
/track-legislation legis-federal
/track-legislation all

# Rebuild the report manually:
python3 scripts/validate_changes.py && python3 scripts/generate_report.py

# Regenerate agents after editing the registry:
python3 scripts/gen_agents.py
```

Open `report/index.html` in any browser — it is fully self-contained
(no network requests), so it can be emailed or published as-is.

## Data contract

Both layers share the same discipline. Instruction entries
(`schemas/change_entry.schema.json`) require a verbatim `excerpt.current`
passage; legislation entries (`schemas/legislation_entry.schema.json`)
require verbatim operative bill language in `excerpt.passage`, both
audience summaries, and the return-mapping fields. Every entry carries a
source citation, a category from the shared taxonomy, an impact rating,
and a `status`:

- **verified** — the excerpt was copied from a document retrieved during the
  review. This is the only trustworthy state.
- **unverified** — drafted without confirming against a retrieved source.
  The report badges these prominently.

## Roadmap: return-data comparison

Legislation entries are deliberately structured for a future layer that
joins them against tax return preparation data: `affected_returns` names
the exact forms/schedules, `related_form_jurisdictions` links to the form
layer, and `first_return_year_affected` anchors each law to a filing
season. That comparison (which clients/entities are actually exposed to
each change) is planned but not built yet.

## ⚠ Current data is demo data

The files now in `data/changes/` (federal-1120, state-ca, state-tx) and
`data/legislation/` (legis-federal, legis-la) were produced in a
**network-restricted session**: entries are AI-recalled, marked
`unverified`, and their excerpts are illustrative rather than verbatim.
They exist to exercise the pipeline and the report UI. Run the agents in a
session with web access to replace them with verified findings before
relying on anything here.
