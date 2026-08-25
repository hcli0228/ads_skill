import pytest
import os
import sys
from pathlib import Path

# Add root directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ads_api import ADS, ADSClient, ADSError

@pytest.fixture(scope="session")
def ads():
    return ADS()

def test_client_init(ads):
    assert ads.client.token is not None
    assert len(ads.client.token) > 10

def test_search_simple(ads):
    res = ads.search.query(q="author:Hawking", rows=3, fl=["title", "bibcode", "citation_count", "year"])
    assert "num_found" in res
    assert res["num_found"] > 0
    assert len(res["docs"]) > 0
    doc = res["docs"][0]
    assert "bibcode" in doc
    assert "title" in doc
    assert "citation_count" in doc

def test_search_qtree(ads):
    res = ads.search.qtree(q="author:Hawking black hole")
    assert "qtree" in res

def test_bigquery(ads):
    bibcodes = ["1975CMaPh..43..199H", "1974Natur.248...30H"]
    res = ads.search.bigquery(bibcodes=bibcodes, fl=["bibcode", "title", "citation_count"])
    assert res["num_found"] >= 2
    assert len(res["docs"]) >= 2
    found_bibs = [d["bibcode"] for d in res["docs"]]
    assert "1975CMaPh..43..199H" in found_bibs

def test_metrics(ads):
    bibcodes = ["1975CMaPh..43..199H", "1974Natur.248...30H"]
    metrics = ads.metrics.summarize_metrics(bibcodes)
    assert metrics["total_papers"] == 2
    assert metrics["total_citations"] > 10000
    assert metrics["h_index"] >= 2
    assert "i10_index" in metrics

def test_export_bibtex(ads):
    bibcodes = ["1975CMaPh..43..199H"]
    bibtex = ads.export.export(bibcodes, format_name="bibtex")
    assert "@ARTICLE" in bibtex
    assert "1975CMaPh..43..199H" in bibtex
    assert "Hawking" in bibtex

def test_export_custom(ads):
    bibcodes = ["1975CMaPh..43..199H"]
    template = "%H (%Y): %T [%R]"
    res = ads.export.export(bibcodes, format_name="custom", custom_format=template)
    assert "Hawking" in res
    assert "1975" in res
    assert "1975CMaPh..43..199H" in res

def test_journal_summary(ads):
    res = ads.journals.get_summary("ApJ")
    assert "summary" in res
    summary = res["summary"]
    assert "master" in summary
    assert summary["master"]["bibstem"] == "ApJ"

def test_citation_helper(ads):
    bibcodes = ["1975CMaPh..43..199H", "1974Natur.248...30H"]
    recs = ads.citation_helper.get_recommendations(bibcodes, num_recommendations=5)
    assert isinstance(recs, list)
    assert len(recs) > 0
    assert "bibcode" in recs[0]

def test_resolver(ads):
    bibcode = "1975CMaPh..43..199H"
    links = ads.resolver.get_links(bibcode)
    assert "links" in links or "action" in links or isinstance(links, dict)
