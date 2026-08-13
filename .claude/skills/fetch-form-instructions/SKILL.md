---
name: fetch-form-instructions
description: >-
  Locate and cache current-year and prior-year tax form instructions (IRS and
  state) for year-over-year comparison. Use at the start of any jurisdiction
  review, when a source PDF/HTML is missing from data/sources/, or when asked
  to find where a form's instructions live.
---

# Fetch form instructions

Goal: for every form in the jurisdiction's scope, cache BOTH the current-year
and prior-year instructions locally, plus an extracted plain-text version,
under a predictable layout. Everything downstream (diffing, excerpting,
citation) reads from this cache.

## Cache layout

```
data/sources/<jurisdiction-id>/<year>/<slug>.pdf|html   # original document
data/sources/<jurisdiction-id>/<year>/<slug>.txt        # extracted text
data/sources/<jurisdiction-id>/manifest.json            # what was fetched, from where, when
```

`<slug>` is a kebab-case form identifier (`i1120`, `form-100-booklet`).
`manifest.json` maps each cached file to its source URL, retrieval date, and
document revision — the report cites these, so record them accurately.

## Finding IRS instructions

- Current revision (HTML): `https://www.irs.gov/instructions/i<form>` —
  e.g., `i1120`, `i5471`, `i8865`, `i8858`. The HTML page states the revision
  ("Rev. December 2025" or a tax year).
- Prior revisions (PDF): `https://www.irs.gov/pub/irs-prior/i<form>--<yyyy>.pdf`.
  Continuous-use forms use month names: `i5471--dec-2024.pdf`. When unsure,
  search the prior-year products page:
  `https://www.irs.gov/prior-year-forms-and-instructions?find=<form>`.
- Also fetch the FORM itself (not just instructions) for both years when line
  layout changes matter: `f1120--<yyyy>.pdf` under the same prefix.

## Finding state instructions

1. Start from the agency site listed in the agent's scope block. Look for
   "Forms" or "Forms and Instructions", filtered to corporate/business income
   tax. Most states publish a corporate instructions *booklet* PDF — prefer
   the booklet over per-form snippets.
2. Prior year: look for a "Prior year forms" archive on the same site.
3. If the agency removed the prior year, use the Wayback Machine:
   `https://web.archive.org/web/2024*/<form-url>` and record the archive URL
   as the source. Never cite a document you did not actually retrieve.
4. WebSearch is the fallback for locating pages (e.g.,
   `"Form CT-1120CU" 2025 instructions site:portal.ct.gov`), but only cache
   documents fetched from the agency domain or web.archive.org.

## Retrieval mechanics

- Try WebFetch first for HTML pages. For PDFs, use Bash `curl -L -o <path>`;
  if the environment's egress proxy blocks a domain, note it and fall back to
  WebFetch; if both fail, record the gap — do not substitute memory.
- Extract text from PDFs into the sibling `.txt` file:
  `pdftotext -layout file.pdf file.txt` if available, else Python `pypdf`:
  ```bash
  python3 - <<'EOF'
  from pypdf import PdfReader
  import sys
  r = PdfReader("in.pdf")
  with open("out.txt", "w") as f:
      for i, p in enumerate(r.pages, 1):
          f.write(f"\n=== PAGE {i} ===\n" + (p.extract_text() or ""))
  EOF
  ```
  Keep the `=== PAGE n ===` markers — they let you cite page numbers.
- For HTML instructions, save the raw HTML and also produce a `.txt` by
  stripping tags, so both years diff as text.

## Failure handling

If a document in scope cannot be retrieved after reasonable attempts, add a
human-readable line to the `coverage.gaps` array of the jurisdiction's change
file (e.g., "2024 Form 100W booklet: ftb.ca.gov blocked by egress policy and
no Wayback capture found"). A gap recorded honestly is a valid result; an
excerpt invented from memory is not.
