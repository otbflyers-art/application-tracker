"""Bank registry: every bank we can query automatically, plus the ones we
can't (no public job-search API) that need to be checked by hand.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from . import fetchers


@dataclass(frozen=True)
class BankSource:
    name: str
    category: str
    platform: str
    fetch: Callable[..., list[dict]]
    kwargs: dict[str, Any] = field(default_factory=dict)
    careers_url: str = ""
    # True for banks whose only public feed is their lateral/experienced-hire
    # board (their campus/new-grad recruiting isn't separately scrapeable).
    # A bare "Investment Banking Analyst" title there is ambiguous — it could
    # be backfilling an experienced seat — so seniority.is_entry_level()
    # additionally requires an explicit campus/class-year signal for these.
    requires_entry_signal: bool = False


@dataclass(frozen=True)
class ManualBank:
    name: str
    category: str
    note: str
    careers_url: str


# ══════════════════════════════════════════════════════════════════════════
# Banks with a scrapeable public job-search API.
# ══════════════════════════════════════════════════════════════════════════
BANKS: list[BankSource] = [
    # ── Bulge Bracket ────────────────────────────────────────────────────
    BankSource("Morgan Stanley", "Bulge Bracket", "Workday", fetchers.fetch_workday,
               {"tenant": "ms", "wd_num": 5, "site": "External"},
               "https://www.morganstanley.com/people-opportunities/students-graduates"),
    BankSource("J.P. Morgan", "Bulge Bracket", "Oracle Cloud HCM", fetchers.fetch_oracle,
               {"host": "jpmc.fa.oraclecloud.com"},
               "https://careers.jpmorgan.com/us/en/students/programs/investment-banking-analyst"),
    BankSource("Bank of America", "Bulge Bracket", "Workday", fetchers.fetch_workday,
               {"tenant": "ghr", "wd_num": 1, "site": "Lateral-US"},
               "https://campus.bankofamerica.com", requires_entry_signal=True),
    BankSource("Citi", "Bulge Bracket", "Workday", fetchers.fetch_workday,
               {"tenant": "citi", "wd_num": 5, "site": "2"},
               "https://jobs.citi.com/category/banking-full-time-analyst"),
    BankSource("Barclays", "Bulge Bracket", "Workday", fetchers.fetch_workday,
               {"tenant": "barclays", "wd_num": 3, "site": "External_Career_Site_Barclays"},
               "https://search.jobs.barclays/category/investment-banking"),
    BankSource("Deutsche Bank", "Bulge Bracket", "Workday", fetchers.fetch_workday,
               {"tenant": "db", "wd_num": 3, "site": "DBWebsite"},
               "https://www.db.com/careers/en/grad/role-search/investment-banking.html"),
    BankSource("Wells Fargo", "Bulge Bracket", "Workday", fetchers.fetch_workday,
               {"tenant": "wf", "wd_num": 1, "site": "WellsFargoJobs"},
               "https://www.wellsfargo.com/about/careers/college"),
    BankSource("RBC Capital Markets", "Bulge Bracket", "Workday", fetchers.fetch_workday,
               {"tenant": "rbc", "wd_num": 3, "site": "RBCEARLYTALENT1"},
               "https://jobs.rbc.com/us/en/students"),
    BankSource("Jefferies", "Bulge Bracket", "Oracle Cloud HCM", fetchers.fetch_oracle,
               {"host": "hdid.fa.us2.oraclecloud.com"},
               "https://www.jefferies.com/careers/campus-recruiting"),

    # ── Elite Boutiques ──────────────────────────────────────────────────
    BankSource("PJT Partners", "Elite Boutique", "Workday", fetchers.fetch_workday,
               {"tenant": "pjtpartners", "wd_num": 1, "site": "Careers"},
               "https://pjtpartners.wd1.myworkdayjobs.com/PJT"),
    BankSource("Moelis & Company", "Elite Boutique", "Workday", fetchers.fetch_workday,
               {"tenant": "moelis", "wd_num": 1, "site": "Experienced-Hires"},
               "https://moelis.wd1.myworkdayjobs.com/Experienced-Hires", requires_entry_signal=True),
    BankSource("Guggenheim Securities", "Elite Boutique", "Workday", fetchers.fetch_workday,
               {"tenant": "guggenheim", "wd_num": 1, "site": "Guggenheim_Careers_Campus"},
               "https://guggenheim.wd1.myworkdayjobs.com/Guggenheim_Careers_Campus"),
    BankSource("Perella Weinberg Partners", "Elite Boutique", "Workday", fetchers.fetch_workday,
               {"tenant": "pwp", "wd_num": 1, "site": "PWP_Experienced_Opportunities"},
               "https://pwp.wd1.myworkdayjobs.com/PWP_Experienced_Opportunities", requires_entry_signal=True),
    BankSource("Rothschild & Co", "Elite Boutique", "Workday", fetchers.fetch_workday,
               {"tenant": "rothschildandco", "wd_num": 3, "site": "Rothschildandco_Lateral"},
               "https://www.rothschildandco.com/en/careers/graduate", requires_entry_signal=True),
    BankSource("Lazard", "Elite Boutique", "Oracle Cloud HCM", fetchers.fetch_oracle,
               {"host": "icbpjb.fa.ocs.oraclecloud.com"},
               "https://lazard.wd1.myworkdayjobs.com/lazard"),

    # ── Middle Market ────────────────────────────────────────────────────
    BankSource("Houlihan Lokey", "Middle Market", "Workday", fetchers.fetch_workday,
               {"tenant": "hl", "wd_num": 1, "site": "Lateral"},
               "https://hl.wd1.myworkdayjobs.com/Lateral", requires_entry_signal=True),
    BankSource("Piper Sandler", "Middle Market", "Workday", fetchers.fetch_workday,
               {"tenant": "pipersandler", "wd_num": 501, "site": "Piper_Sandler_Careers"},
               "https://pipersandler.wd501.myworkdayjobs.com/Piper_Sandler_Careers"),
    BankSource("TD Cowen", "Middle Market", "Workday", fetchers.fetch_workday,
               {"tenant": "td", "wd_num": 3, "site": "TD_Bank_Careers"},
               "https://td.wd3.myworkdayjobs.com/TD_Bank_Careers"),
    BankSource("Lincoln International", "Middle Market", "Greenhouse", fetchers.fetch_greenhouse,
               {"gh_slug": "lincolninternational"},
               "https://www.lincolninternational.com/careers"),
    BankSource("Solomon Partners", "Middle Market", "Greenhouse", fetchers.fetch_greenhouse,
               {"gh_slug": "solomonpartnersprofessionals"},
               "https://www.solomonpartners.com/careers"),
    BankSource("Stifel", "Middle Market", "JibeApply", fetchers.fetch_jibeapply,
               {"portal_host": "join.stifel.com"},
               "https://join.stifel.com"),
    BankSource("Leerink Partners", "Middle Market", "Workday", fetchers.fetch_workday,
               {"tenant": "leerink", "wd_num": 5, "site": "leerinkpartners"},
               "https://www.leerink.com/careers"),

    # ── Foreign Banks ────────────────────────────────────────────────────
    BankSource("Macquarie", "Foreign Bank", "Workday", fetchers.fetch_workday,
               {"tenant": "mq", "wd_num": 3, "site": "CareersatMQ"},
               "https://www.macquarie.com/us/en/careers/graduates.html"),
    BankSource("Mizuho (+ Greenhill)", "Foreign Bank", "Workday", fetchers.fetch_workday,
               {"tenant": "mizuho", "wd_num": 1, "site": "mizuhoamericas"},
               "https://www.mizuhogroup.com/careers"),
    BankSource("HSBC", "Foreign Bank", "Eightfold AI", fetchers.fetch_eightfold,
               {"tenant": "hsbc", "domain": "hsbc.com"},
               "https://www.hsbc.com/careers/students-and-graduates"),
    BankSource("MUFG", "Foreign Bank", "Workday", fetchers.fetch_workday,
               {"tenant": "mufgub", "wd_num": 3, "site": "MUFG-Careers"},
               "https://careers.mufgamericas.com"),
    BankSource("Scotiabank", "Foreign Bank", "RSS Feed", fetchers.fetch_rss,
               {"feed_url": "https://jobs.scotiabank.com/sitemap.xml"},
               "https://jobs.scotiabank.com"),

    # ── Restructuring Advisory ───────────────────────────────────────────
    BankSource("Alvarez & Marsal", "Restructuring Advisory", "Workday", fetchers.fetch_workday,
               {"tenant": "alvarezandmarsal", "wd_num": 1, "site": "alvarezandmarsalp"},
               "https://www.alvarezandmarsal.com/careers"),
    BankSource("Ankura", "Restructuring Advisory", "Workday", fetchers.fetch_workday,
               {"tenant": "ankura", "wd_num": 5, "site": "Ankura"},
               "https://ankura.com/careers"),
    BankSource("Harris Williams", "Restructuring Advisory", "Workday", fetchers.fetch_workday,
               {"tenant": "pnc", "wd_num": 5, "site": "HarrisWilliams"},
               "https://www.harriswilliams.com/careers"),
    BankSource("Portage Point", "Restructuring Advisory", "Lever", fetchers.fetch_lever,
               {"lever_slug": "portagepointpartners"},
               "https://www.portagepointpartners.com/careers"),
    BankSource("Accordion", "Restructuring Advisory", "Greenhouse", fetchers.fetch_greenhouse,
               {"gh_slug": "accordion"},
               "https://www.accordion.com/careers"),
    BankSource("Kroll", "Restructuring Advisory", "Oracle Cloud HCM", fetchers.fetch_oracle,
               {"host": "hcxs.fa.us2.oraclecloud.com"},
               "https://www.kroll.com/en/careers"),
]

# ══════════════════════════════════════════════════════════════════════════
# Banks with no public job-search API. These do not expose a public
# Workday/Lever/Greenhouse endpoint that could be verified (custom portals,
# Oracle Cloud HCM, SAP SuccessFactors, Eightfold AI, or Tal.net). They're
# excluded from automated fetching to avoid silently reporting "no openings"
# when the real answer is "never checked". Re-check periodically in case a
# firm migrates to a scrapeable ATS.
# ══════════════════════════════════════════════════════════════════════════
NO_PUBLIC_API: list[ManualBank] = [
    ManualBank("Goldman Sachs", "Bulge Bracket",
               "No public API — Workday CXS returns 422 for all known site slugs",
               "https://www.goldmansachs.com/careers/students"),
    ManualBank("UBS", "Bulge Bracket",
               "No public API — Workday CXS returns 422 for all known site slugs",
               "https://www.ubs.com/careers/en/students.html"),
    ManualBank("Evercore", "Elite Boutique",
               "No public API — uses Tal.net (JS-rendered, auth-walled), not Lever",
               "https://evercore.tal.net/candidate/jobboard/vacancy/2/adv/"),
    ManualBank("Centerview Partners", "Elite Boutique",
               "No public API — custom ASP.NET form, not on Greenhouse",
               "https://www.centerviewpartners.com/careers"),
    ManualBank("Greenhill", "Elite Boutique",
               "Acquired by Mizuho (2023) — roles now posted under the Mizuho listing",
               "https://www.greenhill.com/careers"),
    ManualBank("Qatalyst Partners", "Elite Boutique",
               "No public job board — recruiting is email/referral-based (uscareers@qatalyst.com)",
               "https://www.qatalyst.com"),
    ManualBank("Needham & Company", "Middle Market",
               "No public API — Tal.net job board is CAPTCHA-protected (Oleeo bot check)",
               "https://www.needhamco.com/careers/"),
    ManualBank("Nomura", "Foreign Bank",
               "No public API — SAP SuccessFactors career site is auth-walled",
               "https://www.nomura.com/americas/careers"),
    ManualBank("BNP Paribas", "Foreign Bank",
               "No public API — uses Tal.net (JS-rendered, auth-walled), not Greenhouse",
               "https://careers.bnpparibas.com"),
    ManualBank("AlixPartners", "Restructuring Advisory",
               "No public API — job search portal is a JS-rendered SPA with no accessible feed",
               "https://www.alixpartners.com/careers/entry-level"),
]
