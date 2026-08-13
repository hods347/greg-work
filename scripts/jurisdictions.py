"""Single source of truth for every jurisdiction covered by the tax
form-change review system.

Consumed by:
  - scripts/gen_agents.py       (generates one Claude Code agent per jurisdiction)
  - scripts/generate_report.py  (builds the HTML change report)
  - scripts/validate_changes.py (checks change files reference known jurisdictions)

Form numbers and URLs are curated starting points. Agents are instructed to
verify current form numbers and instruction locations on the agency site,
since states rename and renumber forms.
"""

FEDERAL = [
    {
        "id": "federal-1120",
        "name": "Federal — Form 1120",
        "kind": "federal",
        "agency": "Internal Revenue Service",
        "website": "https://www.irs.gov",
        "forms": ["Form 1120 (U.S. Corporation Income Tax Return)"],
        "instructions_current": "https://www.irs.gov/instructions/i1120",
        "instructions_prior_pattern": "https://www.irs.gov/pub/irs-prior/i1120--{year}.pdf",
        "notes": (
            "Core corporate return. Watch: new lines/schedules, elections and "
            "required statements (e.g., method changes, bonus depreciation, "
            "Section 174A domestic research expensing), Schedule J tax "
            "computation changes, Schedule K question changes, CAMT (Form 4626) "
            "applicability, e-file mandates, and changes cross-referencing new "
            "legislation."
        ),
    },
    {
        "id": "federal-5471",
        "name": "Federal — Form 5471",
        "kind": "federal",
        "agency": "Internal Revenue Service",
        "website": "https://www.irs.gov",
        "forms": ["Form 5471 (Information Return of U.S. Persons With Respect to Certain Foreign Corporations)"],
        "instructions_current": "https://www.irs.gov/instructions/i5471",
        "instructions_prior_pattern": "https://www.irs.gov/pub/irs-prior/i5471--{year}.pdf",
        "notes": (
            "CFC information return. Watch: filer category definitions "
            "(constructive ownership / Section 958(b) rules), new or revised "
            "separate schedules (E, G-1, H, I-1, J, M, P, Q, R), GILTI/NCTI "
            "terminology and computation changes, Section 250/960 changes, "
            "exchange-rate and functional-currency reporting, penalty and "
            "filing-relief updates."
        ),
    },
    {
        "id": "federal-8865",
        "name": "Federal — Form 8865",
        "kind": "federal",
        "agency": "Internal Revenue Service",
        "website": "https://www.irs.gov",
        "forms": ["Form 8865 (Return of U.S. Persons With Respect to Certain Foreign Partnerships)"],
        "instructions_current": "https://www.irs.gov/instructions/i8865",
        "instructions_prior_pattern": "https://www.irs.gov/pub/irs-prior/i8865--{year}.pdf",
        "notes": (
            "Foreign partnership return. Watch: filer category changes, "
            "Schedules K-2/K-3 requirements, constructive ownership rules, "
            "Section 721(c) gain deferral reporting, Schedule O/P transfer "
            "reporting, alignment with Form 1065 changes."
        ),
    },
    {
        "id": "federal-8858",
        "name": "Federal — Form 8858",
        "kind": "federal",
        "agency": "Internal Revenue Service",
        "website": "https://www.irs.gov",
        "forms": ["Form 8858 (Information Return of U.S. Persons With Respect to Foreign Disregarded Entities (FDEs) and Foreign Branches (FBs))"],
        "instructions_current": "https://www.irs.gov/instructions/i8858",
        "instructions_prior_pattern": "https://www.irs.gov/pub/irs-prior/i8858--{year}.pdf",
        "notes": (
            "FDE/FB information return. Watch: who-must-file expansions, "
            "Schedule C-1 (Section 987 gain/loss) changes — especially "
            "adoption of the final Section 987 regulations — Schedule J and M "
            "changes, dormant-entity relief, foreign branch category rules."
        ),
    },
]

# (code, name, agency, website, main corporate forms, regime notes)
_STATES = [
    ("al", "Alabama", "Alabama Department of Revenue", "https://www.revenue.alabama.gov",
     ["Form 20C", "Form 20C-C (consolidated)"],
     "Separate filing with elective consolidated returns. Federal income tax deduction allowed — watch changes to the FIT deduction and to Alabama addback rules."),
    ("ak", "Alaska", "Alaska Department of Revenue, Tax Division", "https://tax.alaska.gov",
     ["Form 6000"],
     "Mandatory water's-edge combined reporting (worldwide for oil & gas). Alaska piggybacks the IRC with modifications — watch IRC conformity date changes."),
    ("az", "Arizona", "Arizona Department of Revenue", "https://azdor.gov",
     ["Form 120", "Form 120A"],
     "Separate/consolidated/combined options. Watch sales-factor and service-sourcing changes and the corporate rate."),
    ("ar", "Arkansas", "Arkansas Department of Finance and Administration", "https://www.dfa.arkansas.gov",
     ["Form AR1100CT"],
     "Separate reporting. Watch rate reductions (frequent recent legislation), apportionment, and NOL carryforward rules."),
    ("ca", "California", "California Franchise Tax Board", "https://www.ftb.ca.gov",
     ["Form 100", "Form 100W (water's-edge)", "Schedule R (apportionment)"],
     "Unitary combined reporting with water's-edge election. Fixed-date IRC conformity (currently 1/1/2015 with piecemeal updates) — most federal changes do NOT flow through automatically. Watch NOL suspensions, credit caps, market-based sourcing rules, and Schedule R changes."),
    ("co", "Colorado", "Colorado Department of Revenue", "https://tax.colorado.gov",
     ["Form DR 0112"],
     "Combined reporting (tested-membership rules replaced 3-of-6 test in 2026 forms era). Rolling IRC conformity. Watch tax-haven/foreign-income addbacks and single-sales-factor sourcing."),
    ("ct", "Connecticut", "Connecticut Department of Revenue Services", "https://portal.ct.gov/drs",
     ["Form CT-1120", "Form CT-1120CU (combined unitary)"],
     "Mandatory unitary combined reporting. Watch capital base tax phase-out, surtax extensions, and NOL/credit utilization limits."),
    ("de", "Delaware", "Delaware Division of Revenue", "https://revenue.delaware.gov",
     ["Form 1100"],
     "Separate reporting, three-factor apportionment history — watch factor weighting and sourcing changes."),
    ("dc", "District of Columbia", "DC Office of Tax and Revenue", "https://otr.cfo.dc.gov",
     ["Form D-20"],
     "Combined reporting. Watch ballpark fee, QHTC incentive changes, and apportionment sourcing."),
    ("fl", "Florida", "Florida Department of Revenue", "https://floridarevenue.com",
     ["Form F-1120"],
     "Separate reporting, fixed-date IRC conformity updated annually — the annual conformity bill and required addbacks (e.g., bonus depreciation spread) are the biggest YoY items."),
    ("ga", "Georgia", "Georgia Department of Revenue", "https://dor.georgia.gov",
     ["Form 600"],
     "Separate reporting. Annual IRC conformity legislation with specific decoupling (e.g., Section 174, bonus depreciation) — watch the conformity bill summary in the instructions."),
    ("hi", "Hawaii", "Hawaii Department of Taxation", "https://tax.hawaii.gov",
     ["Form N-30"],
     "Separate/combined unitary. Watch IRC conformity updates and credit changes."),
    ("id", "Idaho", "Idaho State Tax Commission", "https://tax.idaho.gov",
     ["Form 41"],
     "Water's-edge combined reporting. Watch rate changes and IRC conformity."),
    ("il", "Illinois", "Illinois Department of Revenue", "https://tax.illinois.gov",
     ["Form IL-1120", "Schedule UB (combined)"],
     "Unitary combined (non-unitary businesses excluded). Rolling conformity with significant decoupling (GILTI/NCTI, FDII, bonus depreciation, NOL caps). Watch Schedule M addition/subtraction changes and the foreign/80-20 company rules."),
    ("in", "Indiana", "Indiana Department of Revenue", "https://www.in.gov/dor",
     ["Form IT-20"],
     "Separate reporting, single sales factor, market-based sourcing. Watch rate step-downs and IRC conformity date updates."),
    ("ia", "Iowa", "Iowa Department of Revenue", "https://tax.iowa.gov",
     ["Form IA 1120"],
     "Separate/consolidated. Watch contingent rate reductions (revenue triggers) and conformity."),
    ("ks", "Kansas", "Kansas Department of Revenue", "https://www.ksrevenue.gov",
     ["Form K-120"],
     "Combined reporting for unitary groups. Rolling conformity. Watch rate changes and apportionment election (single sales factor transition)."),
    ("ky", "Kentucky", "Kentucky Department of Revenue", "https://revenue.ky.gov",
     ["Form 720"],
     "Mandatory unitary combined (elective consolidated). Watch LLET changes, rate triggers, and NOL sharing rules."),
    ("la", "Louisiana", "Louisiana Department of Revenue", "https://revenue.louisiana.gov",
     ["Form CIFT-620"],
     "Separate reporting. Major 2025 reform: flat 5.5% rate, repeal of franchise tax (2026), full expensing — watch the reform's phase-ins in each year's instructions."),
    ("me", "Maine", "Maine Revenue Services", "https://www.maine.gov/revenue",
     ["Form 1120ME"],
     "Unitary combined reporting. Watch IRC conformity legislation and Maine capital investment credit changes."),
    ("md", "Maryland", "Comptroller of Maryland", "https://www.marylandtaxes.gov",
     ["Form 500"],
     "Separate reporting (combined reporting repeatedly proposed — watch for adoption). Watch single sales factor phase-in completion and addback rules."),
    ("ma", "Massachusetts", "Massachusetts Department of Revenue", "https://www.mass.gov/orgs/massachusetts-department-of-revenue",
     ["Form 355", "Form 355U (combined)"],
     "Mandatory unitary combined. Single sales factor for all industries (2025). Watch apportionment regs, financial institution excise changes."),
    ("mi", "Michigan", "Michigan Department of Treasury", "https://www.michigan.gov/taxes",
     ["Form 4891 (CIT Annual Return)"],
     "Unitary combined filing. Watch flow-through entity tax interactions and sourcing rules."),
    ("mn", "Minnesota", "Minnesota Department of Revenue", "https://www.revenue.state.mn.us",
     ["Form M4"],
     "Unitary combined. Watch GILTI/NCTI and foreign-income inclusion changes, dividend received deduction changes, and NOL limitation (70%) rules."),
    ("ms", "Mississippi", "Mississippi Department of Revenue", "https://www.dor.ms.gov",
     ["Form 83-105"],
     "Separate/combined options. Watch franchise tax phase-out schedule and full-expensing conformity."),
    ("mo", "Missouri", "Missouri Department of Revenue", "https://dor.mo.gov",
     ["Form MO-1120"],
     "Separate reporting, single sales factor, optional consolidated. Watch rate reduction triggers and federal income tax deduction changes."),
    ("mt", "Montana", "Montana Department of Revenue", "https://mtrevenue.gov",
     ["Form CIT"],
     "Water's-edge election over worldwide combined. Watch apportionment and conformity changes."),
    ("ne", "Nebraska", "Nebraska Department of Revenue", "https://revenue.nebraska.gov",
     ["Form 1120N"],
     "Unitary combined. Watch rate step-downs (scheduled reductions) and sourcing rules."),
    ("nv", "Nevada", "Nevada Department of Taxation", "https://tax.nv.gov",
     ["Commerce Tax Return"],
     "No corporate income tax. Monitor Commerce Tax (gross receipts) instructions: rate schedules by NAICS, filing thresholds, and Modified Business Tax credit interactions."),
    ("nh", "New Hampshire", "New Hampshire Department of Revenue Administration", "https://www.revenue.nh.gov",
     ["Form NH-1120 (BPT)", "Form BT-Summary"],
     "Business Profits Tax with combined reporting plus Business Enterprise Tax. Watch rate changes, NOL rules, and the interplay of BPT/BET credits."),
    ("nj", "New Jersey", "New Jersey Division of Taxation", "https://www.nj.gov/treasury/taxation",
     ["Form CBT-100", "Form CBT-100U (combined)"],
     "Mandatory unitary combined. Very active YoY changes: CBT surtax / Corporate Transit Fee, GILTI/NCTI treatment, dividend exclusions, market sourcing regs. Read the CBT-100U instructions changes closely every year."),
    ("nm", "New Mexico", "New Mexico Taxation and Revenue Department", "https://www.tax.newmexico.gov",
     ["Form CIT-1"],
     "Mandatory combined (water's-edge default; worldwide election). Watch rate bracket changes and single sales factor rules."),
    ("ny", "New York", "New York State Department of Taxation and Finance", "https://www.tax.ny.gov",
     ["Form CT-3", "Form CT-3-A (combined)"],
     "Article 9-A combined reporting, customer-based sourcing. Watch business capital base rates, MTA surcharge rate (set annually by regulation), PTET interactions, and the annual corporate tax reform regulation updates. New York City is covered by a separate agent (state-nyc)."),
    ("nc", "North Carolina", "North Carolina Department of Revenue", "https://www.ncdor.gov",
     ["Form CD-405"],
     "Separate reporting. Corporate rate phase-out to 0% (scheduled step-downs through 2030) — confirm each year's rate. Watch franchise tax base changes."),
    ("nd", "North Dakota", "North Dakota Office of State Tax Commissioner", "https://www.tax.nd.gov",
     ["Form 40"],
     "Worldwide combined with water's-edge election. Watch rate and conformity changes."),
    ("oh", "Ohio", "Ohio Department of Taxation", "https://tax.ohio.gov",
     ["Commercial Activity Tax (CAT) returns"],
     "No corporate income tax. Monitor CAT instructions: exclusion amount changes (major 2024-2025 increases), annual-filer elimination, rate/base changes."),
    ("ok", "Oklahoma", "Oklahoma Tax Commission", "https://oklahoma.gov/tax.html",
     ["Form 512"],
     "Separate/consolidated election. Watch full-expensing conformity and rate legislation."),
    ("or", "Oregon", "Oregon Department of Revenue", "https://www.oregon.gov/dor",
     ["Form OR-20"],
     "Unitary consolidated. ALSO monitor the separate Corporate Activity Tax (CAT) — its instructions change independently. Watch market sourcing and listed-jurisdiction (tax haven) rules."),
    ("pa", "Pennsylvania", "Pennsylvania Department of Revenue", "https://www.pa.gov/agencies/revenue",
     ["Form RCT-101"],
     "Separate reporting. Corporate rate step-downs (9.99% phasing to 4.99% by 2031) — confirm each year's rate. Watch economic nexus rules, NOL cap increases (2025+ legislation), and market sourcing."),
    ("ri", "Rhode Island", "Rhode Island Division of Taxation", "https://tax.ri.gov",
     ["Form RI-1120C"],
     "Mandatory unitary combined. Watch single sales factor sourcing and minimum tax changes."),
    ("sc", "South Carolina", "South Carolina Department of Revenue", "https://dor.sc.gov",
     ["Form SC1120"],
     "Separate reporting. Watch apportionment litigation-driven changes (forced combination rules) and conformity."),
    ("sd", "South Dakota", "South Dakota Department of Revenue", "https://dor.sd.gov",
     ["Bank Franchise Tax Return"],
     "No corporate income tax. Monitor bank franchise tax instructions only; note any new business taxes."),
    ("tn", "Tennessee", "Tennessee Department of Revenue", "https://www.tn.gov/revenue",
     ["Form FAE170 (Franchise & Excise)"],
     "Franchise and excise tax. Major recent change: property-base repeal for franchise tax (2024). Watch single sales factor, excise conformity, and F&E exemption changes."),
    ("tx", "Texas", "Texas Comptroller of Public Accounts", "https://comptroller.texas.gov",
     ["Franchise Tax Report (Form 05-158 et al.)"],
     "No corporate income tax; franchise (margin) tax with mandatory combined reporting. Watch no-tax-due threshold changes, compensation deduction cap (indexed), and EZ computation limits."),
    ("ut", "Utah", "Utah State Tax Commission", "https://tax.utah.gov",
     ["Form TC-20"],
     "Water's-edge combined. Watch rate changes (recent annual cuts) and sourcing."),
    ("vt", "Vermont", "Vermont Department of Taxes", "https://tax.vermont.gov",
     ["Form CO-411"],
     "Unitary combined. Recent shift to single sales factor and repeal of throwback — verify current-year status. Watch minimum tax tiers."),
    ("va", "Virginia", "Virginia Department of Taxation", "https://www.tax.virginia.gov",
     ["Form 500"],
     "Separate reporting (unitary combined report was informational only — watch for adoption). Annual fixed-date conformity bill with decoupling — read the conformity summary every year."),
    ("wa", "Washington", "Washington State Department of Revenue", "https://dor.wa.gov",
     ["Business & Occupation (B&O) excise returns"],
     "No corporate income tax. Monitor B&O tax changes: rate/surcharge legislation (major 2025 changes), service-rate tiers, and the 7% capital gains excise for entities' owners where relevant."),
    ("wv", "West Virginia", "West Virginia Tax Division", "https://tax.wv.gov",
     ["Form CIT-120"],
     "Unitary combined. Watch rate legislation and single sales factor sourcing."),
    ("wi", "Wisconsin", "Wisconsin Department of Revenue", "https://www.revenue.wi.gov",
     ["Form 4", "Form 6 (combined)"],
     "Combined reporting. Fixed-date conformity updated by legislation — watch the conformity update and addback/modification schedule changes."),
    ("wy", "Wyoming", "Wyoming Department of Revenue", "https://revenue.wyo.gov",
     [],
     "No corporate income tax and no gross receipts tax. Monitor for newly enacted business taxes only; expect most reviews to report no changes."),
]

STATES = [
    {
        "id": f"state-{code}",
        "name": name,
        "kind": "state",
        "agency": agency,
        "website": website,
        "forms": forms,
        "instructions_current": None,
        "instructions_prior_pattern": None,
        "notes": notes,
    }
    for code, name, agency, website, forms, notes in _STATES
]

LOCAL = [
    {
        "id": "state-nyc",
        "name": "New York City",
        "kind": "local",
        "agency": "New York City Department of Finance",
        "website": "https://www.nyc.gov/site/finance",
        "forms": ["Form NYC-2", "Form NYC-2A (combined)"],
        "instructions_current": None,
        "instructions_prior_pattern": None,
        "notes": (
            "NYC Business Corporation Tax is separate from New York State "
            "Article 9-A and changes on its own schedule. Watch customer-based "
            "sourcing phase-ins, capital base differences from the state, and "
            "GCT (Form NYC-3L) for S corporations, which NYC still taxes."
        ),
    },
]

JURISDICTIONS = FEDERAL + STATES + LOCAL

BY_ID = {j["id"]: j for j in JURISDICTIONS}

# ---------------------------------------------------------------------------
# Legislation-monitoring layer.
#
# Separate agent set with its own cadence: form-instruction reviews happen
# annually, legislation monitoring runs throughout the year. Federal is a
# single legislative jurisdiction (one Congress affects all four federal
# forms); states and NYC map 1:1 to the form layer.
# ---------------------------------------------------------------------------

LEGIS_FEDERAL = {
    "id": "legis-federal",
    "name": "Federal — Legislation",
    "kind": "federal",
    "agency": "United States Congress / Internal Revenue Service",
    "website": "https://www.congress.gov",
    "sources": [
        "https://www.congress.gov (enacted public laws; filter to revenue/tax)",
        "https://www.irs.gov/newsroom (IRS implementation guidance and news)",
        "https://home.treasury.gov (Treasury press releases)",
        "https://www.jct.gov (Joint Committee on Taxation explanations)",
    ],
    "notes": (
        "Track enacted public laws amending the Internal Revenue Code with "
        "corporate income tax impact, plus major IRS implementation guidance "
        "(revenue procedures, notices) that changes how corporations comply "
        "with new law. Map every provision to the federal forms it touches "
        "(1120, 5471, 8865, 8858, and their schedules)."
    ),
    # form-layer jurisdictions whose returns this legislation feeds into
    "related_form_jurisdictions": [
        "federal-1120", "federal-5471", "federal-8865", "federal-8858",
    ],
}


def _legis_from_form_jurisdiction(j: dict) -> dict:
    return {
        "id": "legis-" + j["id"].removeprefix("state-"),
        "name": f"{j['name']} — Legislation",
        "kind": j["kind"],
        "agency": j["agency"],
        "website": j["website"],
        "sources": [
            f"{j['website']} (revenue agency news / law-change summaries)",
            "State legislature bill-status site (enrolled/chaptered bills)",
            "Governor's office bill-signing announcements",
            "Revenue agency annual legislative summary publication, if issued",
        ],
        "notes": j["notes"],
        "related_form_jurisdictions": [j["id"]],
    }


LEGIS_JURISDICTIONS = [LEGIS_FEDERAL] + [
    _legis_from_form_jurisdiction(j) for j in STATES + LOCAL
]

LEGIS_BY_ID = {j["id"]: j for j in LEGIS_JURISDICTIONS}
