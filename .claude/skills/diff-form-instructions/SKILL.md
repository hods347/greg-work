---
name: diff-form-instructions
description: >-
  Compare two years of a tax form's instructions and isolate substantive
  changes, separating them from cosmetic edits. Use after both years'
  instructions are cached in data/sources/, when analyzing what changed
  between revisions of any tax form or booklet.
---

# Diff form instructions

Input: two extracted `.txt` files (current and prior year) from
`data/sources/<jurisdiction>/<year>/`. Output: a worked list of substantive
changes with the exact supporting passages and their locations — the raw
material the `summarize-tax-changes` skill turns into structured entries.

## Pass 1 — "What's New"

Read the current year's "What's New" / "Important Information" /
"Legislative Update" section first. It is the agency's own change list:
every item in it is a candidate change entry, and its wording is usually the
best excerpt. But treat it as a floor, not a ceiling — agencies omit plenty.

## Pass 2 — structural sweep

Compare the two documents' skeletons before their prose:

```bash
# Section headings side by side (tune the regex to the document's style)
grep -nE '^[A-Z][A-Za-z0-9 ,''&()-]{3,60}$' prior.txt > /tmp/h-prior.txt
grep -nE '^[A-Z][A-Za-z0-9 ,''&()-]{3,60}$' current.txt > /tmp/h-current.txt
diff /tmp/h-prior.txt /tmp/h-current.txt
```

Headings that appear/disappear signal new schedules, removed worksheets, new
elections. Also grep both years for high-signal tokens and compare hits:
line numbers (`Line 29b`), schedule letters, "must file", "required to",
"election", "new for", percentages, dollar thresholds, IRC section numbers
(`section 174`, `163(j)`, `951A`), and state-specific terms (apportionment,
addback, addition, subtraction, modification, throwback, combined, unitary,
conformity, market-based, cost of performance).

## Pass 3 — targeted section diffs

For every section flagged by passes 1-2, and for the standing high-value
sections regardless (Who Must File; What's New; apportionment schedule
instructions; addition/subtraction modification schedules; rate schedules;
penalty and due-date sections), extract the section from both years and diff:

```bash
python3 - <<'EOF'
# extract lines between two headings, then difflib.unified_diff the sections
EOF
```

Word-level `git diff --no-index --word-diff=plain prior-sec.txt current-sec.txt`
is often clearer than line diffs for reflowed PDF text.

## Substantive vs cosmetic

Substantive (report): meaning changes — new/removed obligations, changed
amounts, changed dates, changed computations, changed definitions, new or
retired forms/schedules/lines, changed sourcing or apportionment mechanics,
new elections/statements, e-file mandates, penalty changes.

Cosmetic (drop): reflowed lines, page-number shifts, revision-date and
OMB-number updates, pure rewording with identical meaning, address changes
for paper filing (borderline — report only if the jurisdiction pushes many
paper filers), routine inflation indexing UNLESS preparers key on the number
(no-tax-due thresholds, minimum tax tiers: report those).

## Capture discipline

For every substantive change, capture in your notes before moving on:
1. Verbatim current-year passage (copy exactly, including the line/section
   reference text; trim interior with "…" only if very long).
2. Verbatim prior-year counterpart passage, or the determination "no prior
   counterpart — new text".
3. Location: section heading + `=== PAGE n ===` marker (PDF) or nearest
   heading (HTML).
4. Which document/URL each passage came from.

These four items are mandatory inputs to `summarize-tax-changes`; if you
cannot produce the verbatim current passage, the change cannot be marked
`verified`.
