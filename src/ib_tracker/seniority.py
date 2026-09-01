"""Entry-level filter: keep postings aimed at new/upcoming graduates,
drop ones that read like they want a candidate who already has full-time
experience.

Two layers, both title-based (the only text reliably available across
every ATS platform — most search APIs return just a title, not a full job
description):

1. A stronger set of seniority keywords than classify.py's EXCLUDE_KEYWORDS
   (which only catches obvious titles like "Associate" or "Vice
   President") — this also catches "Senior Analyst" and numbered analyst
   tiers ("Analyst II"), which in IB mean a promoted 2nd/3rd-year analyst,
   not a new hire.
2. For banks whose only public feed is their lateral/experienced-hire
   board (see banks.BankSource.requires_entry_signal), a bare "Investment
   Banking Analyst" title there is ambiguous — it could be backfilling an
   experienced seat rather than hiring for a class-year program — so those
   postings also need an explicit campus/entry signal (a class year,
   "analyst program", "campus", "graduate", "class of ...") before they
   count.
"""

from __future__ import annotations

EXPERIENCE_EXCLUDE_KEYWORDS = [
    "senior analyst",
    "analyst ii",
    "analyst 2",
    "analyst iii",
    "analyst 3",
    "assistant vice president",
    " avp ",
    "svp",
    "senior vice president",
    "principal",
    "team lead",
]

ENTRY_SIGNAL_KEYWORDS = [
    "analyst program",
    "full-time analyst",
    "full time analyst",
    "campus",
    "graduate",
    "new grad",
    "early career",
    "early careers",
    "class of",
    "university",
    "undergraduate",
    "first year analyst",
    "first-year analyst",
]


def is_entry_level(title: str, description: str = "", *, class_year: str = "", requires_entry_signal: bool = False) -> bool:
    """True unless the title/description reads like a lateral/experienced
    posting, or (for banks flagged `requires_entry_signal`) there's no
    explicit campus/class-year signal to disambiguate it from one."""
    text = f"{title} {description}".lower()
    if any(kw in text for kw in EXPERIENCE_EXCLUDE_KEYWORDS):
        return False
    if requires_entry_signal:
        signals = ENTRY_SIGNAL_KEYWORDS + ([class_year] if class_year else [])
        if not any(sig in text for sig in signals):
            return False
    return True
