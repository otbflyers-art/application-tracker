import json

import pytest
import responses

from ib_tracker.fetchers import (
    FetchContext,
    fetch_eightfold,
    fetch_greenhouse,
    fetch_jibeapply,
    fetch_lever,
    fetch_oracle,
    fetch_rss,
    fetch_workday,
)


@pytest.fixture
def ctx():
    import requests

    return FetchContext(class_year="2027", search_terms=["investment banking analyst", "2027"], session=requests.Session())


@responses.activate
def test_fetch_workday_classifies_and_dedupes(ctx):
    responses.add(
        responses.POST,
        "https://tb.wd1.myworkdayjobs.com/wday/cxs/tb/External/jobs",
        json={
            "jobPostings": [
                {"title": "Investment Banking Analyst", "externalPath": "/job/1", "locationsText": "NYC", "postedOn": "Today"},
                {"title": "Investment Banking Associate", "externalPath": "/job/2"},  # excluded: associate
            ]
        },
        status=200,
    )
    jobs = fetch_workday(ctx, "Test Bank", "tb", 1, "External")
    # Two search terms hit the same mocked endpoint/response, so the IB
    # Analyst posting should be deduped down to a single result.
    assert len(jobs) == 1
    job = jobs[0]
    assert job["bank"] == "Test Bank"
    assert job["title"] == "Investment Banking Analyst"
    assert job["division"] == "Investment Banking"
    assert job["link"] == "https://tb.wd1.myworkdayjobs.com/en-US/External/job/1"
    assert job["source"] == "Workday"


@responses.activate
def test_fetch_workday_handles_error_response(ctx):
    responses.add(
        responses.POST,
        "https://tb.wd1.myworkdayjobs.com/wday/cxs/tb/External/jobs",
        body="not json",
        status=500,
    )
    assert fetch_workday(ctx, "Test Bank", "tb", 1, "External") == []


@responses.activate
def test_fetch_oracle(ctx):
    responses.add(
        responses.GET,
        "https://example.oraclecloud.com/hcmRestApi/resources/latest/recruitingCEJobRequisitions",
        json={
            "items": [
                {"requisitionList": [
                    {"Title": "Investment Banking Analyst - M&A", "Id": "123", "PrimaryLocation": "NYC", "PostedDate": "2027-01-01"},
                ]}
            ]
        },
        status=200,
    )
    jobs = fetch_oracle(ctx, "Test Bank", "example.oraclecloud.com")
    assert len(jobs) == 1
    assert jobs[0]["link"].endswith("/job/123")
    assert jobs[0]["source"] == "Oracle Cloud HCM"


@responses.activate
def test_fetch_greenhouse(ctx):
    responses.add(
        responses.GET,
        "https://boards-api.greenhouse.io/v1/boards/testco/jobs",
        json={"jobs": [
            {"title": "Investment Banking Analyst", "absolute_url": "https://boards.greenhouse.io/testco/1",
             "location": {"name": "NYC"}, "updated_at": "2027-01-01T00:00:00", "departments": [{"name": "IB"}]},
            {"title": "Software Engineer", "absolute_url": "https://boards.greenhouse.io/testco/2"},
        ]},
        status=200,
    )
    jobs = fetch_greenhouse(ctx, "Test Bank", "testco")
    assert len(jobs) == 1
    assert jobs[0]["title"] == "Investment Banking Analyst"
    assert jobs[0]["source"] == "Greenhouse"


@responses.activate
def test_fetch_lever(ctx):
    responses.add(
        responses.GET,
        "https://api.lever.co/v0/postings/testco",
        json=[
            {"text": "Investment Banking Analyst", "hostedUrl": "https://jobs.lever.co/testco/1",
             "categories": {"team": "IB", "location": "NYC"}},
            {"text": "Marketing Manager", "hostedUrl": "https://jobs.lever.co/testco/2"},
        ],
        status=200,
    )
    jobs = fetch_lever(ctx, "Test Bank", "testco")
    assert len(jobs) == 1
    assert jobs[0]["source"] == "Lever"


@responses.activate
def test_fetch_eightfold_dedupes_across_terms(ctx):
    responses.add(
        responses.GET,
        "https://tb.eightfold.ai/api/apply/v2/jobs",
        json={"positions": [{"name": "Investment Banking Analyst", "id": "1", "location": "NYC"}]},
        status=200,
    )
    jobs = fetch_eightfold(ctx, "Test Bank", "tb", "tb.com")
    assert len(jobs) == 1


@responses.activate
def test_fetch_jibeapply_paginates_and_filters(ctx):
    responses.add(
        responses.GET,
        "https://portal.example.com/api/jobs",
        json={
            "jobs": [
                {"data": {"title": "Investment Banking Analyst", "slug": "ib-analyst", "city": "NYC", "state": "NY"}},
                {"data": {"title": "Marketing Coordinator", "slug": "marketing"}},
            ],
            "totalCount": 2,
        },
        status=200,
    )
    jobs = fetch_jibeapply(ctx, "Test Bank", "portal.example.com")
    assert len(jobs) == 1
    assert jobs[0]["link"] == "https://portal.example.com/jobs/ib-analyst"


@responses.activate
def test_fetch_rss(ctx):
    xml = """<?xml version="1.0"?>
    <rss><channel>
      <item><title>Investment Banking Analyst</title><link>https://example.com/1</link></item>
      <item><title>Barista</title><link>https://example.com/2</link></item>
    </channel></rss>"""
    responses.add(responses.GET, "https://example.com/feed.xml", body=xml, status=200, content_type="application/xml")
    jobs = fetch_rss(ctx, "Test Bank", "https://example.com/feed.xml")
    assert len(jobs) == 1
    assert jobs[0]["link"] == "https://example.com/1"
