import pytest

from ib_tracker.location import is_us_posting


@pytest.mark.parametrize(
    "loc,title",
    [
        ("New York, New York, United States of America", "Investment Banking Analyst"),
        ("New York, NY, United States", "Investment Banking Analyst"),
        ("Houston TX", "Investment Banking Analyst"),
        ("", "2027 CIB Investment Banking Analyst Program - Early Careers (CA)"),
        ("Chicago, IL", "Investment Banking Analyst"),
        ("", "Investment Banking Analyst"),  # no signal either way -> benefit of the doubt
    ],
)
def test_us_postings_are_kept(loc, title):
    assert is_us_posting(loc, title) is True


@pytest.mark.parametrize(
    "loc,title",
    [
        ("Toronto, Canada", "Canada Investment Banking Analyst - Toronto"),
        ("Mumbai, Maharashtra, India", "Investment Banking Analyst - Officer"),
        ("Seoul, Korea, Republic Of", "Investment Banking Analyst - C11 - SEOUL"),
        ("Amsterdam", "Investment Banking Analyst (F/M/X)"),
        ("Dubai, United Arab Emirates", "Banking, Investment Banking, Full Time Analyst, Dubai, UAE 2026"),
        ("", "Frankfurt Off-Cycle Analyst Programme"),
        ("London, United Kingdom", "Investment Banking Analyst"),
        ("Hong Kong, Hong Kong", "Senior Analyst, M&A, Investment Banking"),
        ("", "Mizuho | Greenhill – Investment Banking Analyst – Frankfurt (immediate start)"),
    ],
)
def test_non_us_postings_are_dropped(loc, title):
    assert is_us_posting(loc, title) is False


def test_new_mexico_is_not_confused_with_mexico():
    assert is_us_posting("Albuquerque, New Mexico, United States", "Investment Banking Analyst") is True


def test_mexico_city_is_dropped():
    assert is_us_posting("Ciudad De Mexico Distrito Federal Mexico", "Full time Analyst - Mexico") is False
