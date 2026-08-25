from typing import Any, Dict, List, Optional
from ads_api.client import ADSClient

class ResolverService:
    """
    Service for resolving external links, DOIs, arXiv eprints, and publisher sources for bibcodes.
    """
    def __init__(self, client: Optional[ADSClient] = None):
        self.client = client or ADSClient()

    def get_links(self, bibcode: str) -> Dict[str, Any]:
        """
        Get all external links and resolver targets for a given bibcode.
        """
        res = self.client.get(f"resolver/{bibcode}")
        return res.json()

    def get_link_type(self, bibcode: str, link_type: str = "abstract") -> Dict[str, Any]:
        """
        Get specific link target (e.g. 'abstract', 'article', 'preprint', 'citations', 'references', 'data').
        """
        res = self.client.get(f"resolver/{bibcode}/{link_type}")
        return res.json()
