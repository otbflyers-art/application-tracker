"""Runtime configuration for the IB tracker."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

DEFAULT_TRACKER_PATH = Path("IB_FT_Analyst_Recruiting_Tracker.xlsx")
DEFAULT_LOG_PATH = Path("ib_tracker_update_log.json")
DEFAULT_SEEN_PATH = Path("ib_checker_seen.json")

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)

HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "application/json, text/html, */*",
}

REQUEST_TIMEOUT = 15
BANK_PAUSE_SECONDS = 0.3
TERM_PAUSE_SECONDS = 0.2


@dataclass
class Config:
    """Everything a run needs that a user might reasonably want to override."""

    class_year: str = "2027"
    tracker_path: Path = DEFAULT_TRACKER_PATH
    log_path: Path = DEFAULT_LOG_PATH
    seen_path: Path = DEFAULT_SEEN_PATH

    @property
    def search_terms(self) -> list[str]:
        """Terms each keyword-search fetcher queries. Board-dump fetchers (Lever,
        Greenhouse, RSS, JibeApply) ignore this and filter their full listings.
        The class year catches class-year-titled FT programs in any division."""
        return [
            "investment banking analyst",
            "global markets analyst",
            "equity research analyst",
            self.class_year,
        ]
