"""Role classification: decide whether a job posting is a target full-time
analyst role, and which division it belongs to.

Markets/Research are checked before Investment Banking so titles like "CIB
Markets Full Time Analyst Program" land in Markets despite containing IB
keywords.
"""

from __future__ import annotations

# Keywords that confirm a role is specifically IB (not just any FT analyst)
IB_KEYWORDS = [
    "investment banking analyst",
    "ibd analyst",
    "global banking analyst",
    "m&a analyst",
    "restructuring analyst",
    "leveraged finance analyst",
    "financial sponsors analyst",
    "capital markets analyst",
    "healthcare investment banking analyst",
    "technology investment banking analyst",
    "corporate finance analyst",
    "financial advisory analyst",
    "banking analyst",
]

# Generic FT-analyst-program phrasing with no division named. These are worth
# tracking (a "<year> Full-Time Analyst Program" could be IB) but can't be
# division-tagged from the title alone — they get a verify-me division label.
# The active class year is appended at classification time.
GENERIC_FT_KEYWORDS = [
    "full-time analyst",
    "full time analyst",
    "first year analyst",
    "first-year analyst",
    "graduate analyst",
    "analyst program",
]

# Broader IB context phrases. Combined with the word "analyst" appearing
# anywhere in the title, these catch common non-contiguous title formats that
# IB_KEYWORDS misses, e.g. "Investment Banking - Technology - Analyst" or
# "Investment Banking – Equity Capital Markets – Analyst" (JPMorgan's whole
# job title scheme is built this way, and it's a common pattern industry-wide).
IB_CONTEXT_KEYWORDS = [
    "investment banking",
    "investment bank -",
    "investment bank –",
    "ibd",
    "mergers & acquisitions",
    "mergers and acquisitions",
    "leveraged finance",
    "restructuring",
    "financial sponsors",
    "capital markets",
    "corporate finance",
    "financial advisory",
    "global banking",
]

EXCLUDE_KEYWORDS = [
    "summer analyst",
    "intern",
    "internship",
    "associate",
    "vice president",
    "director",
    "managing director",
    "experienced",
    "lateral",
    "wealth management",
    "commercial banking",
    "operations",
    "compliance",
    "risk",
    "audit",
    "private banking",
    "private bank",
    # "Capital Markets" as a business-unit name also covers IT/ops titles at
    # some banks (e.g. Scotiabank's "Business Analyst Specialist (Capital
    # Markets Technology)") that aren't investment banking analyst roles.
    "technical analyst",
    "business analyst",
    "capital markets technology",
    "corporate actions",
    # Middle/back-office roles that share front-office division names
    "middle office",
    "back office",
    "settlement",
    "product control",
    "sales support",
    "support team",
    " vp ",
]

# Excludes that only apply when the title does NOT also explicitly say
# "investment banking" — otherwise these wrongly drop real IB coverage-group
# titles like "Investment Banking - Technology - Analyst" (Tech is an IB
# coverage vertical, not the IT department) or "... - Software - Analyst".
SECTOR_OVERLAP_EXCLUDES = [
    "technology analyst",
    "data analyst",
    "quantitative analyst",
    "software",
    "engineer",
]

# Sales & Trading / Markets context phrases (analyst must also appear in title)
MARKETS_CONTEXT_KEYWORDS = [
    "sales and trading",
    "sales & trading",
    "global markets",
    "markets analyst",
    "markets full time analyst",
    "markets full-time analyst",
    "trading analyst",
    "fixed income",
    "equity derivatives",
    "securitized products",
    "electronic trading",
    "commodities",
    "structuring analyst",
]

# Research context phrases (analyst must also appear in title)
RESEARCH_CONTEXT_KEYWORDS = [
    "equity research",
    "credit research",
    "investment research",
    "macro research",
    "research analyst",
    "research full time analyst",
    "research full-time analyst",
    "research program",
]


def classify_role(title: str, description: str = "", class_year: str = "") -> str | None:
    """Return the division a posting belongs to, or None if it's not a target."""
    t = (title + " " + description).lower()
    if any(ex in t for ex in EXCLUDE_KEYWORDS):
        return None
    if "analyst" in t:
        if any(kw in t for kw in MARKETS_CONTEXT_KEYWORDS):
            return "Markets / Sales & Trading"
        if any(kw in t for kw in RESEARCH_CONTEXT_KEYWORDS):
            return "Research"
    if "investment bank" not in t and any(ex in t for ex in SECTOR_OVERLAP_EXCLUDES):
        return None
    if any(kw in t for kw in IB_KEYWORDS):
        return "Investment Banking"
    if "analyst" in t and any(kw in t for kw in IB_CONTEXT_KEYWORDS):
        return "Investment Banking"
    generic_keywords = GENERIC_FT_KEYWORDS
    if class_year:
        generic_keywords = [*GENERIC_FT_KEYWORDS, f"{class_year} analyst"]
    if any(kw in t for kw in generic_keywords):
        return "FT Analyst Program (verify division)"
    return None


def is_target_role(title: str, description: str = "", class_year: str = "") -> bool:
    return classify_role(title, description, class_year) is not None
