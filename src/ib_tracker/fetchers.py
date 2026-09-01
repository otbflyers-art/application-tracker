"""ATS-specific fetchers.

Each fetch_* function queries one public job-search API/feed and returns a
list of dicts: {bank, title, division, loc, posted, link, source}.
All of them are pure functions of a FetchContext plus their own ATS-specific
arguments — no shared mutable state — so they're easy to call directly or
mock out in tests.
"""

from __future__ import annotations

import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from html.parser import HTMLParser

import requests

from . import classify
from .config import REQUEST_TIMEOUT, TERM_PAUSE_SECONDS


@dataclass
class FetchContext:
    class_year: str
    search_terms: list[str]
    session: requests.Session


def safe_get(session: requests.Session, url: str, **kwargs) -> requests.Response | None:
    try:
        r = session.get(url, timeout=REQUEST_TIMEOUT, **kwargs)
        r.raise_for_status()
        return r
    except Exception:
        return None


def _classify(ctx: FetchContext, title: str, description: str = "") -> str | None:
    return classify.classify_role(title, description, class_year=ctx.class_year)


def fetch_workday(ctx: FetchContext, bank_name: str, tenant: str, wd_num, site: str) -> list[dict]:
    """Workday public CXS job search endpoint.

    tenant = short tenant slug, e.g. 'ms' for Morgan Stanley
    wd_num = the Workday cluster number, e.g. 5 (host is {tenant}.wd{wd_num}.myworkdayjobs.com)
    site   = the career site name within the tenant, e.g. 'External' (varies per company)
    """
    host = f"{tenant}.wd{wd_num}.myworkdayjobs.com"
    base = f"https://{host}/wday/cxs/{tenant}/{site}/jobs"
    results, seen = [], set()
    for term in ctx.search_terms:
        payload = {"appliedFacets": {}, "limit": 20, "offset": 0, "searchText": term}
        try:
            r = ctx.session.post(base, json=payload, timeout=REQUEST_TIMEOUT)
            data = r.json()
            for job in data.get("jobPostings", []):
                title = job.get("title", "")
                ext_url = job.get("externalPath", "")
                division = _classify(ctx, title)
                if not division or ext_url in seen:
                    continue
                seen.add(ext_url)
                results.append({
                    "bank": bank_name,
                    "title": title,
                    "division": division,
                    "loc": job.get("locationsText", ""),
                    "posted": job.get("postedOn", ""),
                    "link": f"https://{host}/en-US/{site}{ext_url}" if ext_url else "",
                    "source": "Workday",
                })
        except Exception:
            pass
        time.sleep(TERM_PAUSE_SECONDS)
    return results


def fetch_oracle(ctx: FetchContext, bank_name: str, host: str, site_number: str = "CX_1") -> list[dict]:
    """Oracle Fusion Cloud Recruiting (Candidate Experience) public REST API.

    host = the oraclecloud.com hostname, e.g. 'jpmc.fa.oraclecloud.com'
    Requires expand=requisitionList to get the actual job list, not just facets.
    """
    url = f"https://{host}/hcmRestApi/resources/latest/recruitingCEJobRequisitions"
    results, seen = [], set()
    for term in ctx.search_terms:
        params = {
            "finder": f"findReqs;siteNumber={site_number},limit=20,offset=0,keyword={term}",
            "expand": "requisitionList",
        }
        r = safe_get(ctx.session, url, params=params)
        if not r:
            continue
        try:
            for item in r.json().get("items", []):
                for job in item.get("requisitionList", []):
                    title = job.get("Title", "")
                    job_id = job.get("Id", "")
                    division = _classify(ctx, title)
                    if not division or job_id in seen:
                        continue
                    seen.add(job_id)
                    results.append({
                        "bank": bank_name,
                        "title": title,
                        "division": division,
                        "loc": job.get("PrimaryLocation", ""),
                        "posted": job.get("PostedDate", ""),
                        "link": f"https://{host}/hcmUI/CandidateExperience/en/sites/{site_number}/job/{job_id}",
                        "source": "Oracle Cloud HCM",
                    })
        except Exception:
            pass
        time.sleep(TERM_PAUSE_SECONDS)
    return results


def fetch_greenhouse(ctx: FetchContext, bank_name: str, gh_slug: str) -> list[dict]:
    """Greenhouse public job board API."""
    r = safe_get(ctx.session, f"https://boards-api.greenhouse.io/v1/boards/{gh_slug}/jobs?content=true")
    results = []
    if not r:
        return results
    try:
        for job in r.json().get("jobs", []):
            title = job.get("title", "")
            departments = job.get("departments") or [{}]
            dept = departments[0].get("name", "")
            division = _classify(ctx, title, dept)
            if not division:
                continue
            results.append({
                "bank": bank_name,
                "title": title,
                "division": division,
                "loc": (job.get("location") or {}).get("name", ""),
                "posted": job.get("updated_at", "")[:10],
                "link": job.get("absolute_url", ""),
                "source": "Greenhouse",
            })
    except Exception:
        pass
    return results


def fetch_lever(ctx: FetchContext, bank_name: str, lever_slug: str) -> list[dict]:
    """Lever public jobs API."""
    r = safe_get(ctx.session, f"https://api.lever.co/v0/postings/{lever_slug}?mode=json")
    results = []
    if not r:
        return results
    try:
        for job in r.json():
            title = job.get("text", "")
            team = job.get("categories", {}).get("team", "")
            division = _classify(ctx, title, team)
            if not division:
                continue
            results.append({
                "bank": bank_name,
                "title": title,
                "division": division,
                "loc": job.get("categories", {}).get("location", ""),
                "posted": "",
                "link": job.get("hostedUrl", ""),
                "source": "Lever",
            })
    except Exception:
        pass
    return results


def fetch_eightfold(ctx: FetchContext, bank_name: str, tenant: str, domain: str) -> list[dict]:
    """Eightfold AI public candidate-facing job search API."""
    url = f"https://{tenant}.eightfold.ai/api/apply/v2/jobs"
    results, seen = [], set()
    for term in ctx.search_terms:
        r = safe_get(ctx.session, url, params={"domain": domain, "query": term, "limit": 20})
        if not r:
            continue
        try:
            for job in r.json().get("positions", []):
                title = job.get("name", "")
                job_id = job.get("id", "")
                division = _classify(ctx, title, job.get("department", "") or "")
                if not division or job_id in seen:
                    continue
                seen.add(job_id)
                results.append({
                    "bank": bank_name,
                    "title": title,
                    "division": division,
                    "loc": job.get("location", ""),
                    "posted": "",
                    "link": f"https://{tenant}.eightfold.ai/careers/job?domain={domain}&pid={job_id}",
                    "source": "Eightfold AI",
                })
        except Exception:
            pass
        time.sleep(TERM_PAUSE_SECONDS)
    return results


def fetch_jibeapply(ctx: FetchContext, bank_name: str, portal_host: str) -> list[dict]:
    """JibeApply/iCIMS careers portal JSON API (e.g. join.stifel.com).
    The keyword param is ignored by the API, so fetch all pages and filter locally."""
    results = []
    offset = 0
    while True:
        r = safe_get(ctx.session, f"https://{portal_host}/api/jobs", params={"limit": 50, "page": offset // 50 + 1})
        if not r:
            break
        try:
            data = r.json()
        except Exception:
            break
        jobs = data.get("jobs", [])
        if not jobs:
            break
        for j in jobs:
            d = j.get("data", j)
            title = d.get("title", "")
            category = d.get("category", "") if isinstance(d.get("category"), str) else ""
            division = _classify(ctx, title, category)
            if not division:
                continue
            slug = d.get("slug", "") or str(d.get("req_id", ""))
            results.append({
                "bank": bank_name,
                "title": title,
                "division": division,
                "loc": f"{d.get('city', '')} {d.get('state', '')}".strip(),
                "posted": (d.get("posted_date", "") or "")[:10],
                "link": f"https://{portal_host}/jobs/{slug}",
                "source": "JibeApply",
            })
        offset += 50
        if offset >= data.get("totalCount", 0):
            break
    return results


def fetch_rss(ctx: FetchContext, bank_name: str, feed_url: str) -> list[dict]:
    """Generic Google-Jobs-style RSS/XML job feed (<item><title>/<link>)."""
    results = []
    r = safe_get(ctx.session, feed_url)
    if not r:
        return results
    try:
        for item in ET.fromstring(r.content).iter("item"):
            title = (item.findtext("title") or "").strip()
            division = _classify(ctx, title)
            if not division:
                continue
            results.append({
                "bank": bank_name,
                "title": title,
                "division": division,
                "loc": "",
                "posted": "",
                "link": (item.findtext("link") or "").strip(),
                "source": "RSS Feed",
            })
    except Exception:
        pass
    return results


def fetch_smartrecruiters(ctx: FetchContext, bank_name: str, company_id: str) -> list[dict]:
    """SmartRecruiters public API."""
    r = safe_get(ctx.session, f"https://api.smartrecruiters.com/v1/companies/{company_id}/postings?limit=100")
    results = []
    if not r:
        return results
    try:
        for job in r.json().get("content", []):
            title = job.get("name", "")
            dept = job.get("department", {}).get("label", "")
            division = _classify(ctx, title, dept)
            if not division:
                continue
            results.append({
                "bank": bank_name,
                "title": title,
                "division": division,
                "loc": "",
                "posted": job.get("releasedDate", ""),
                "link": f"https://jobs.smartrecruiters.com/{company_id}/{job.get('id', '')}",
                "source": "SmartRecruiters",
            })
    except Exception:
        pass
    return results


class _ICIMSJobParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.jobs = []
        self._in_title = False
        self._current = {}

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a" and "iCIMS_JobsTable" in attrs.get("class", ""):
            self._current = {"href": attrs.get("href", "")}
            self._in_title = True

    def handle_data(self, data):
        if self._in_title and data.strip():
            self._current["title"] = data.strip()
            self._in_title = False
            self.jobs.append(self._current)


def fetch_icims(ctx: FetchContext, bank_name: str, client_id: str, search_term: str = "investment banking analyst") -> list[dict]:
    """iCIMS job search (used by some banks). Returns HTML, parsed for job titles/links."""
    url = (
        f"https://careers.icims.com/jobs/search"
        f"?ss=1&searchKeyword={requests.utils.quote(search_term)}"
        f"&in_clientid={client_id}"
    )
    r = safe_get(ctx.session, url)
    results = []
    if not r:
        return results
    parser = _ICIMSJobParser()
    parser.feed(r.text)
    for job in parser.jobs:
        title = job.get("title", "")
        division = _classify(ctx, title)
        if not division:
            continue
        results.append({
            "bank": bank_name,
            "title": title,
            "division": division,
            "loc": "",
            "posted": "",
            "link": job.get("href", ""),
            "source": "iCIMS",
        })
    return results
