# IB Full-Time Application Tracker

Finds live investment-banking full-time analyst openings across ~30 banks'
public career-site APIs and keeps an Excel tracker (`IB_FT_Analyst_Recruiting_Tracker.xlsx`)
up to date, so the spreadsheet stays your single source of truth for what's
open, what you've applied to, and what's still worth checking by hand.

No API keys needed — every endpoint queried is public.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Usage

**Create the tracker workbook (once):**

```bash
ib-tracker init --class-year 2027
```

This creates `IB_FT_Analyst_Recruiting_Tracker.xlsx` in the current
directory with three sheets — `Master Job Tracker`, `Bank Coverage
Universe`, and `Search Log` — with the bank universe pre-populated.

**Update the tracker (run regularly, e.g. daily via cron/launchd):**

```bash
ib-tracker update                # writes new openings into the tracker
ib-tracker update --dry-run      # preview what would be added, no writes
```

Every run appends any newly found openings to `Master Job Tracker`, updates
each bank's row in `Bank Coverage Universe` with when it was last checked,
and logs the run to `Search Log` (and to `ib_tracker_update_log.json`, the
last 90 runs).

**Or just check the console, no spreadsheet involved:**

```bash
ib-tracker check                 # print what's live right now
ib-tracker check --show-laterals # also print non-class-year matches
```

Repeat runs of `check` flag postings that are new since the last run
(tracked in `ib_checker_seen.json`, which is safe to delete to reset).

All three commands accept `--class-year YYYY` (default `2027`).

## How it works

- `src/ib_tracker/classify.py` — keyword-based classifier that decides
  whether a job title/description is a target full-time analyst role, and
  which division it belongs to (Investment Banking, Markets / Sales &
  Trading, Research, or an unclear "verify division" bucket).
- `src/ib_tracker/fetchers.py` — one function per ATS platform (Workday,
  Oracle Cloud HCM, Greenhouse, Lever, Eightfold AI, JibeApply, RSS,
  SmartRecruiters, iCIMS), each returning a plain list of job dicts.
- `src/ib_tracker/banks.py` — the registry of ~30 banks with a scrapeable
  public API, plus a list of banks with none (no accessible feed — these
  are surfaced with a careers-page link to check by hand).
- `src/ib_tracker/excel_io.py` — the tracker workbook's layout, styling,
  and read/write helpers.
- `src/ib_tracker/pipeline.py` — ties it together: `run_init`, `run_check`,
  `run_update`.
- `src/ib_tracker/cli.py` — the `ib-tracker` command-line entry point.

A bank's endpoint can change slugs when it migrates ATS platforms — if a
bank in `Bank Coverage Universe` stops finding anything for a long stretch,
check `src/ib_tracker/banks.py` for that bank's `kwargs` against its current
careers site.

## Tests

```bash
pytest
```

`test_fetchers.py` mocks HTTP with `responses`, so it runs offline against
each ATS platform's known response shape.

## Notes

- The generated `.xlsx`, `ib_tracker_update_log.json`, and
  `ib_checker_seen.json` files are personal data (which banks you're
  tracking, application status, notes) — they're gitignored, not committed.
- Some banks (Goldman Sachs, UBS, Evercore, Centerview, etc.) don't expose a
  public job-search API; they're listed in `NO_PUBLIC_API` with a note on
  why and a link to check by hand.
