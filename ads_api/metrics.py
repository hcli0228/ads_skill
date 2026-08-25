from typing import Any, Dict, List, Optional
from ads_api.client import ADSClient

class MetricsService:
    """
    Service for calculating detailed bibliometric and citation metrics for a collection of bibcodes.
    """
    def __init__(self, client: Optional[ADSClient] = None):
        self.client = client or ADSClient()

    def get_metrics(
        self,
        bibcodes: List[str],
        types: Optional[List[str]] = None,
        histograms: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Retrieve metrics for a list of bibcodes.
        
        :param bibcodes: List of bibcode strings
        :param types: List of metrics types to include:
                      ['basic', 'citations', 'indicators', 'histograms', 'timeseries'].
                      If None, all types are returned.
        :param histograms: Optional subset of histograms:
                           ['publications', 'reads', 'downloads', 'citations']
        """
        if not bibcodes:
            return {}

        payload: Dict[str, Any] = {"bibcodes": [b.strip() for b in bibcodes if b.strip()]}
        if types:
            payload["types"] = types
        if histograms:
            payload["histograms"] = histograms

        res = self.client.post("metrics", json_data=payload)
        return res.json()

    def summarize_metrics(self, bibcodes: List[str]) -> Dict[str, Any]:
        """
        Helper method to retrieve and produce a clean summary of key metrics
        (papers count, citations, h-index, g-index, m-index, etc.).
        """
        raw = self.get_metrics(bibcodes)
        basic = raw.get("basic stats", {})
        basic_ref = raw.get("basic stats refereed", {})
        citations = raw.get("citation stats", {})
        citations_ref = raw.get("citation stats refereed", {})
        indicators = raw.get("indicators", {})
        indicators_ref = raw.get("indicators refereed", {})

        return {
            "total_papers": basic.get("number of papers", len(bibcodes)),
            "refereed_papers": basic_ref.get("number of papers", 0),
            "normalized_paper_count": basic.get("normalized paper count", 0.0),
            "total_citations": citations.get("total number of citations", 0),
            "refereed_citations": citations_ref.get("total number of citations", 0),
            "normalized_citations": citations.get("normalized number of citations", 0.0),
            "self_citations": citations.get("number of self-citations", 0),
            "citing_papers": citations.get("number of citing papers", 0),
            "average_citations": citations.get("average number of citations", 0.0),
            "median_citations": citations.get("median number of citations", 0.0),
            "h_index": indicators.get("h", 0),
            "g_index": indicators.get("g", 0),
            "m_index": indicators.get("m", 0.0),
            "i10_index": indicators.get("i10", 0),
            "i100_index": indicators.get("i100", 0),
            "tore_index": indicators.get("tore", 0.0),
            "read10_index": indicators.get("read10", 0.0),
            "skipped_bibcodes": raw.get("skipped bibcodes", [])
        }
