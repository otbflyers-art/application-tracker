import pytest

from ib_tracker.seniority import is_entry_level


@pytest.mark.parametrize(
    "title",
    [
        "Investment Banking Senior Analyst",
        "Investment Banking Senior Analyst | Technology",
        "Investment Banking Analyst II",
        "Analyst 2, Investment Banking",
        "Assistant Vice President, Investment Banking",
        "Principal, Investment Banking Coverage",
    ],
)
def test_seniority_keywords_are_excluded(title):
    assert is_entry_level(title) is False


@pytest.mark.parametrize(
    "title",
    [
        "Investment Banking Analyst",
        "2027 Full-Time Analyst Program",
        "Investment Banking Analyst - Healthcare",
    ],
)
def test_ordinary_entry_titles_pass_without_a_signal_requirement(title):
    assert is_entry_level(title, requires_entry_signal=False) is True


def test_ambiguous_title_from_a_lateral_board_is_dropped_without_a_signal():
    # A bare title with no campus/year marker, from a bank whose only
    # public feed is its lateral/experienced-hire board — too ambiguous.
    assert is_entry_level(
        "Investment Banking Analyst, Media - Los Angeles",
        requires_entry_signal=True,
    ) is False


def test_ambiguous_title_from_a_lateral_board_passes_with_a_class_year_signal():
    assert is_entry_level(
        "Investment Banking Analyst Program 2027",
        class_year="2027",
        requires_entry_signal=True,
    ) is True


def test_ambiguous_title_from_a_lateral_board_passes_with_campus_keyword():
    assert is_entry_level(
        "Investment Banking Analyst - Campus Recruiting",
        requires_entry_signal=True,
    ) is True


def test_seniority_keyword_wins_even_with_an_entry_signal():
    assert is_entry_level(
        "Investment Banking Senior Analyst Program 2027",
        class_year="2027",
        requires_entry_signal=True,
    ) is False
