"""Heuristic US/non-US location filter for job postings.

ATS platforms return location in wildly different shapes (a full "City,
State, United States of America" string from Workday, "City, ST" from
Oracle Cloud, just city + state with no country from JibeApply, nothing at
all from RSS/Lever some of the time). This combines whatever location text
is available with the job title — international postings almost always
name the city or country somewhere, e.g. "Canada Investment Banking
Analyst - Toronto" — and matches against country/city keywords, the same
keyword-heuristic style as classify.py's role matching (with the same
caveat: it's a heuristic, not a geocoder, and can be fooled by a US town
that shares a name with a foreign city, e.g. Vienna, VA).
"""

from __future__ import annotations

import re

US_STATE_ABBREVS = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID",
    "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS",
    "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK",
    "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV",
    "WI", "WY", "DC",
}

# Country names and unambiguous non-US financial-hub cities that show up in
# these banks' postings. `mexico` excludes "New Mexico" via a negative
# lookbehind since these banks do have US offices there.
NON_US_PATTERNS = [
    r"\bcanada\b", r"\btoronto\b", r"\bvancouver\b", r"\bmontreal\b",
    r"\bunited kingdom\b", r"\blondon\b", r"\bedinburgh\b",
    r"\bireland\b", r"\bdublin\b",
    r"\bgermany\b", r"\bfrankfurt\b", r"\bmunich\b", r"\bberlin\b",
    r"\bfrance\b", r"\bparis\b",
    r"\bspain\b", r"\bmadrid\b", r"\bbarcelona\b",
    r"\bitaly\b", r"\bmilan\b",
    r"\bnetherlands\b", r"\bamsterdam\b",
    r"\bswitzerland\b", r"\bzurich\b", r"\bgeneva\b",
    r"\bpoland\b", r"\bwarsaw\b",
    r"\bindia\b", r"\bmumbai\b", r"\bdelhi\b", r"\bbangalore\b", r"\bbengaluru\b",
    r"\bhyderabad\b", r"\bgurgaon\b", r"\bgurugram\b", r"\bpune\b", r"\bchennai\b",
    r"\bchina\b", r"\bshanghai\b", r"\bbeijing\b", r"\bshenzhen\b",
    r"\bhong kong\b",
    r"\bjapan\b", r"\btokyo\b",
    r"\bkorea\b", r"\bseoul\b",
    r"\bsingapore\b",
    r"\baustralia\b", r"\bsydney\b", r"\bmelbourne\b",
    r"\bunited arab emirates\b", r"\bdubai\b", r"\babu dhabi\b", r"\buae\b",
    r"\bqatar\b", r"\bdoha\b",
    r"\bsaudi arabia\b", r"\briyadh\b",
    r"(?<!new )\bmexico\b",
    r"\bbrazil\b", r"\bs[aã]o paulo\b",
    r"\bcolombia\b", r"\bbogot[aá]\b",
    r"\bargentina\b", r"\bbuenos aires\b",
    r"\bphilippines\b", r"\bmanila\b",
    r"\bindonesia\b", r"\bjakarta\b",
    r"\bmalaysia\b", r"\bkuala lumpur\b",
    r"\bthailand\b", r"\bbangkok\b",
    r"\bvietnam\b",
    r"\bsouth africa\b", r"\bjohannesburg\b",
    r"\bisrael\b", r"\btel aviv\b",
    r"\bluxembourg\b",
    r"\bbelgium\b", r"\bbrussels\b",
    r"\bsweden\b", r"\bstockholm\b",
    r"\bdenmark\b", r"\bcopenhagen\b",
    r"\bnorway\b", r"\boslo\b",
    r"\bportugal\b", r"\blisbon\b",
    r"\baustria\b", r"\bvienna\b",
]

_NON_US_RE = re.compile("|".join(NON_US_PATTERNS), re.IGNORECASE)
_US_MARKER_RE = re.compile(r"united states|u\.s\.a\.?|\busa\b", re.IGNORECASE)
_STATE_SUFFIX_RE = re.compile(r"\b(" + "|".join(sorted(US_STATE_ABBREVS)) + r")\b")


def is_us_posting(loc: str = "", title: str = "") -> bool:
    """Best-effort guess at whether a posting is US-based, from whatever
    location text and title are available. Defaults to keeping a posting
    when there's genuinely no signal either way (empty location, no
    recognizable place name in the title)."""
    text = f"{loc} {title}"
    if _NON_US_RE.search(text):
        return False
    if _US_MARKER_RE.search(text):
        return True
    if _STATE_SUFFIX_RE.search(loc.upper()):
        return True
    return not loc.strip()
