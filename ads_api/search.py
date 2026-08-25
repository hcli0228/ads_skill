from typing import Any, Dict, List, Optional, Union
from ads_api.client import ADSClient

DEFAULT_FIELDS = ["bibcode", "title", "author", "year", "pubdate", "citation_count", "doctype", "doi"]

class SearchService:
    """
    Search service interface for querying ADS literature and parsing query AST.
    """
    def __init__(self, client: Optional[ADSClient] = None):
        self.client = client or ADSClient()

    def query(
        self,
        q: str,
        fl: Optional[Union[str, List[str]]] = None,
        sort: Optional[str] = None,
        rows: int = 10,
        start: int = 0,
        fq: Optional[str] = None,
        raw: bool = False
    ) -> Dict[str, Any]:
        """
        Execute a standard Solr query against ADS.
        
        :param q: Query string (e.g. 'author:"Hawking, S." year:1970-1980')
        :param fl: Field list (e.g. 'title,bibcode,citation_count' or ['title', 'bibcode'])
        :param sort: Sort field and direction (e.g. 'citation_count desc', 'date desc')
        :param rows: Number of results to return (max typically 2000)
        :param start: Offset pagination index
        :param fq: Filter query for facet/subset filtering
        :param raw: If True, returns full raw JSON response; otherwise returns docs and summary
        """
        if fl is None:
            fl_str = ",".join(DEFAULT_FIELDS)
        elif isinstance(fl, list):
            fl_str = ",".join(fl)
        else:
            fl_str = fl

        params: Dict[str, Any] = {
            "q": q,
            "fl": fl_str,
            "rows": rows,
            "start": start,
        }
        if sort:
            params["sort"] = sort
        if fq:
            params["fq"] = fq

        res = self.client.get("search/query", params=params)
        data = res.json()

        if raw:
            return data

        response_meta = data.get("response", {})
        return {
            "num_found": response_meta.get("numFound", 0),
            "start": response_meta.get("start", 0),
            "rows_returned": len(response_meta.get("docs", [])),
            "docs": response_meta.get("docs", []),
            "rate_limit": self.client.get_rate_limit()
        }

    def bigquery(
        self,
        bibcodes: List[str],
        q: str = "*:*",
        fl: Optional[Union[str, List[str]]] = None,
        rows: Optional[int] = None,
        start: int = 0,
        sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a BigQuery request to fetch metadata for a list of up to 2000 bibcodes.
        
        :param bibcodes: List of bibcode strings
        :param q: Base query (default: '*:*')
        :param fl: Field list
        :param rows: Number of rows (defaults to len(bibcodes))
        :param start: Offset
        :param sort: Sort field
        """
        if not bibcodes:
            return {"num_found": 0, "docs": [], "rows_returned": 0}

        if len(bibcodes) > 2000:
            raise ValueError(f"BigQuery supports at most 2000 bibcodes per request (got {len(bibcodes)}).")

        if fl is None:
            fl_str = ",".join(DEFAULT_FIELDS)
        elif isinstance(fl, list):
            fl_str = ",".join(fl)
        else:
            fl_str = fl

        params: Dict[str, Any] = {
            "q": q,
            "fl": fl_str,
            "rows": rows if rows is not None else len(bibcodes),
            "start": start,
        }
        if sort:
            params["sort"] = sort

        # ADS bigquery accepts 'big-query/csv' formatted string: "bibcode\n<code1>\n<code2>..."
        payload = "bibcode\n" + "\n".join(b.strip() for b in bibcodes if b.strip())
        
        url = f"{self.client.base_url}/search/bigquery"
        headers = {
            "Authorization": f"Bearer {self.client.token}",
            "Content-Type": "big-query/csv"
        }
        res = self.client.session.post(url, params=params, data=payload, headers=headers, timeout=self.client.timeout)
        self.client._update_rate_limit(res)
        
        if res.status_code != 200:
            from ads_api.client import ADSError
            raise ADSError(f"BigQuery failed ({res.status_code}): {res.text}", res.status_code, res.text)

        data = res.json()
        response_meta = data.get("response", {})
        return {
            "num_found": response_meta.get("numFound", 0),
            "start": response_meta.get("start", 0),
            "rows_returned": len(response_meta.get("docs", [])),
            "docs": response_meta.get("docs", []),
            "rate_limit": self.client.get_rate_limit()
        }

    def qtree(self, q: str) -> Dict[str, Any]:
        """
        Return the parsed Query Tree (Abstract Syntax Tree / AST) for a given query string.
        """
        res = self.client.get("search/qtree", params={"q": q})
        return res.json()
