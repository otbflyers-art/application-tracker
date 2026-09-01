import pytest

from ib_tracker.classify import classify_role


@pytest.mark.parametrize(
    "title,expected",
    [
        ("Investment Banking Analyst - Healthcare", "Investment Banking"),
        ("Investment Banking - Technology - Analyst", "Investment Banking"),
        ("Investment Banking – Equity Capital Markets – Analyst", "Investment Banking"),
        ("M&A Analyst, Consumer & Retail", "Investment Banking"),
        ("Global Markets Full Time Analyst Program", "Markets / Sales & Trading"),
        ("Sales & Trading Analyst - Fixed Income", "Markets / Sales & Trading"),
        ("Equity Research Analyst - TMT", "Research"),
        ("Credit Research Analyst", "Research"),
        ("2027 Full-Time Analyst Program", "FT Analyst Program (verify division)"),
        ("Graduate Analyst Program - London", "FT Analyst Program (verify division)"),
    ],
)
def test_classify_positive(title, expected):
    assert classify_role(title, class_year="2027") == expected


@pytest.mark.parametrize(
    "title",
    [
        "Investment Banking Summer Analyst",
        "Investment Banking Intern",
        "Investment Banking Associate",
        "Investment Banking Vice President",
        "Wealth Management Analyst",
        "Business Analyst - Capital Markets Technology",
        "Middle Office Analyst",
        "Data Analyst, Risk",
        "Technology Analyst - IT Support",
    ],
)
def test_classify_negative(title):
    assert classify_role(title, class_year="2027") is None


def test_restructuring_group_title_classifies_as_ib():
    title = "Investment Banking Restructuring Group Analyst"
    assert classify_role(title, class_year="2027") == "Investment Banking"


def test_bare_restructuring_analyst_is_caught_by_markets_substring_quirk():
    # "restructuring analyst" contains the substring "structuring analyst",
    # which is also a Markets/S&T context keyword (for "structuring analyst"
    # roles on trading desks). Inherited from the original classifier —
    # documented here so a future keyword-list change doesn't silently flip it.
    assert classify_role("Restructuring Analyst", class_year="2027") == "Markets / Sales & Trading"


def test_sector_overlap_exclude_yields_to_explicit_ib_context():
    # "Technology" reads like the SECTOR_OVERLAP excludes, but this is a real
    # IB coverage-group title (Tech is a coverage vertical, not IT).
    title = "Investment Banking - Technology - Analyst"
    assert classify_role(title, class_year="2027") == "Investment Banking"


def test_class_year_keyword_is_dynamic():
    # "<year> analyst" is only matched for the *configured* class year, but
    # generic phrasing like "analyst program" matches regardless of year.
    assert classify_role("2028 Analyst", class_year="2028") == "FT Analyst Program (verify division)"
    assert classify_role("2028 Analyst", class_year="2027") is None
    assert classify_role("2028 Analyst Program", class_year="2027") == "FT Analyst Program (verify division)"


def test_description_is_considered():
    assert classify_role("Analyst", description="") is None
    assert classify_role("Analyst", description="Join our Investment Banking team") == "Investment Banking"
