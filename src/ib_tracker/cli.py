"""Command-line entry point: `ib-tracker init|check|update`."""

from __future__ import annotations

import argparse
import warnings
from pathlib import Path

from .config import Config, DEFAULT_LOG_PATH, DEFAULT_SEEN_PATH, DEFAULT_TRACKER_PATH
from .pipeline import run_check, run_init, run_update


def _add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--class-year", default="2027", help="Class year to search for (default: 2027)")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ib-tracker",
        description="Find and track investment-banking full-time analyst openings across bank career sites.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Create a fresh tracker Excel workbook")
    _add_common_args(p_init)
    p_init.add_argument("--tracker", type=Path, default=DEFAULT_TRACKER_PATH, help="Path to the tracker .xlsx file")
    p_init.add_argument("--force", action="store_true", help="Overwrite an existing tracker file")

    p_check = sub.add_parser("check", help="Print live openings to the console (no Excel file needed)")
    _add_common_args(p_check)
    p_check.add_argument("--show-laterals", action="store_true", help="Also print non-class-year analyst matches")
    p_check.add_argument("--seen", type=Path, default=DEFAULT_SEEN_PATH, help="Path to the seen-links JSON file")

    p_update = sub.add_parser("update", help="Fetch new openings and write them into the tracker workbook")
    _add_common_args(p_update)
    p_update.add_argument("--tracker", type=Path, default=DEFAULT_TRACKER_PATH, help="Path to the tracker .xlsx file")
    p_update.add_argument("--log", type=Path, default=DEFAULT_LOG_PATH, help="Path to the JSON run-log file")
    p_update.add_argument("--dry-run", action="store_true", help="Print findings without writing to the tracker")

    return parser


def main(argv: list[str] | None = None) -> int:
    warnings.filterwarnings("ignore")  # suppress urllib3 OpenSSL notice on macOS

    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "init":
        cfg = Config(class_year=args.class_year, tracker_path=args.tracker)
        run_init(cfg, force=args.force)
        return 0

    if args.command == "check":
        cfg = Config(class_year=args.class_year, seen_path=args.seen)
        run_check(cfg, show_laterals=args.show_laterals)
        return 0

    if args.command == "update":
        cfg = Config(class_year=args.class_year, tracker_path=args.tracker, log_path=args.log)
        run_update(cfg, dry_run=args.dry_run)
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
