---
name: monitor-legislation
description: >-
  Find and verify newly enacted legislation affecting corporate income tax
  returns in a jurisdiction — search strategy, primary-source verification,
  and review-window mechanics. Use during any legislation-monitor agent run,
  or when asked what new tax laws a jurisdiction passed.
---

# Monitor legislation

Goal: within a defined enactment window, find every law that changes how
corporate income tax returns are prepared in the jurisdiction, and verify
each one against primary text. This skill covers finding and verifying;
`summarize-legislation` covers writing the entries.

## Window mechanics

The jurisdiction's file `data/legislation/<legis-id>.json` is a rolling log:

- `window_start` = previous run's `window_end` (or 12 months back on the
  first run). `window_end` = today.
- Carry existing entries forward untouched unless a law was amended or the
  entry needs correction; never re-add a law under a new id.
- Enactment date, not effective date, decides whether a law belongs to the
  window. A law enacted in the window but effective years later still goes
  in (with `effective` and `first_return_year_affected` set accordingly).

## Search strategy (in order of reliability)

1. **Revenue agency law-change pages** — most state DORs publish "Recent law
   changes", "Tax law updates", or an annual legislative bulletin. Highest
   signal; start here.
2. **Legislature bill-status sites** — search chaptered/enrolled bills in
   the revenue/taxation subject area for the session(s) overlapping the
   window. Federal: congress.gov, filter enacted laws on taxation.
3. **Governor / President signing announcements** for the window.
4. **WebSearch sweeps** to catch what 1-3 miss, e.g.:
   `"<state>" corporate income tax law enacted <year>`,
   `"<state>" <year> tax bill signed apportionment OR conformity OR "net operating loss"`.
   Treat news/firm alerts as leads only — they locate bills; they are never
   the cited source.

## Primary-source verification

For each candidate law, retrieve at least one of, in preference order:
1. Enrolled/chaptered bill text or session law (best);
2. The revenue agency's official summary of the act;
3. The legislature's official bill digest.

Copy the operative language verbatim into `excerpt.passage` — the section
that actually amends the statute, not the preamble. Record the bill section
in `source.section`. Only then may the entry be `"status": "verified"`.
A law you could not open primary text for is recorded `unverified` with the
best available secondary source cited, and a note in `coverage.gaps`.

## Scope judgment

In: anything that changes corporate return preparation — rates, conformity,
apportionment/sourcing, modifications, NOLs/credits, filing methods and
procedure, new corporate-level taxes or surcharges, and agency guidance that
operationalizes a new law (e.g., a revenue procedure implementing new
elections). Out: dead bills, individual-income-only provisions, restatements
with no preparer action. Borderline (e.g., PTE-tax changes that alter the
corporate partner's addback): include, at `low`/`medium` impact, and say why
in the summaries.
