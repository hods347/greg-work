#!/usr/bin/env python3
"""Validate jurisdiction change files against the repo's schema and registry.

Usage:
    python3 scripts/validate_changes.py                 # validate all of data/changes/
    python3 scripts/validate_changes.py data/changes/state-ca.json

Dependency-free (no jsonschema): enforces the checks that matter for the
report pipeline. Exits non-zero on any error.
"""
import json
import pathlib
import re
import sys

from jurisdictions import BY_ID

ROOT = pathlib.Path(__file__).resolve().parent.parent
CHANGES_DIR = ROOT / "data" / "changes"

CATEGORIES = {
    "reporting-requirement", "apportionment", "state-modification",
    "income-or-deduction", "rate-or-threshold", "credit-or-incentive",
    "nol-or-limitation",
    "filing-method", "filing-procedure", "due-date", "new-form-or-schedule",
    "conformity", "definition-change", "penalty", "other",
}
IMPACTS = {"high", "medium", "low"}
STATUSES = {"verified", "unverified"}
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def validate_file(path: pathlib.Path) -> list[str]:
    errs: list[str] = []

    def err(msg: str) -> None:
        errs.append(f"{path.name}: {msg}")

    try:
        doc = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        return [f"{path.name}: invalid JSON — {e}"]

    for key in ("jurisdiction", "tax_year", "compared_to_year", "reviewed_date", "coverage", "changes"):
        if key not in doc:
            err(f"missing top-level key '{key}'")
    if errs:
        return errs

    jid = doc["jurisdiction"]
    if jid not in BY_ID:
        err(f"unknown jurisdiction '{jid}' (see scripts/jurisdictions.py)")
    if path.stem != jid:
        err(f"filename should be {jid}.json to match its jurisdiction field")
    if not isinstance(doc["tax_year"], int) or not isinstance(doc["compared_to_year"], int):
        err("tax_year and compared_to_year must be integers")
    elif doc["tax_year"] <= doc["compared_to_year"]:
        err("tax_year must be greater than compared_to_year")
    if not DATE_RE.match(str(doc["reviewed_date"])):
        err("reviewed_date must be YYYY-MM-DD")

    cov = doc["coverage"]
    if not isinstance(cov, dict) or not isinstance(cov.get("documents_reviewed"), list):
        err("coverage.documents_reviewed must be a list")
    else:
        for i, d in enumerate(cov["documents_reviewed"]):
            for key in ("title", "current_url"):
                if not d.get(key):
                    err(f"coverage.documents_reviewed[{i}] missing '{key}'")

    seen_ids: set[str] = set()
    for i, c in enumerate(doc["changes"]):
        where = f"changes[{i}]"
        for key in ("id", "title", "summary", "category", "impact", "status", "form", "source", "excerpt"):
            if key not in c:
                err(f"{where} missing '{key}'")
        cid = c.get("id", "")
        if cid:
            where = f"changes[{i}] ({cid})"
            if not ID_RE.match(cid):
                err(f"{where}: id must be kebab-case")
            if cid in seen_ids:
                err(f"{where}: duplicate id")
            seen_ids.add(cid)
        if c.get("category") not in CATEGORIES:
            err(f"{where}: bad category '{c.get('category')}'")
        if c.get("impact") not in IMPACTS:
            err(f"{where}: bad impact '{c.get('impact')}'")
        if c.get("status") not in STATUSES:
            err(f"{where}: bad status '{c.get('status')}'")
        src = c.get("source") or {}
        if not src.get("document") or not src.get("url"):
            err(f"{where}: source needs 'document' and 'url'")
        exc = c.get("excerpt") or {}
        if not exc.get("current"):
            err(f"{where}: excerpt.current is required (verbatim passage powers the report preview)")
        elif len(exc["current"]) < 40:
            err(f"{where}: excerpt.current is suspiciously short — copy the full supporting passage")
    return errs


def main(argv: list[str]) -> int:
    paths = [pathlib.Path(p) for p in argv[1:]] or sorted(CHANGES_DIR.glob("*.json"))
    if not paths:
        print(f"no change files found in {CHANGES_DIR}")
        return 1
    all_errs: list[str] = []
    for p in paths:
        all_errs.extend(validate_file(p))
    if all_errs:
        print("\n".join(all_errs))
        print(f"\nFAILED: {len(all_errs)} error(s) across {len(paths)} file(s)")
        return 1
    print(f"OK: {len(paths)} file(s) valid")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
