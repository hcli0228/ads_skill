from typing import Any, Dict, List, Optional
from ads_api.client import ADSClient

class CitationHelperService:
    """
    Service for providing paper recommendations and discovering missing co-citations based on input bibcodes.
    Uses 'friends of friends' co-citation network analysis.
    """
    def __init__(self, client: Optional[ADSClient] = None):
        self.client = client or ADSClient()

    def get_recommendations(self, bibcodes: List[str], num_recommendations: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get recommended papers based on co-citation analysis for a list of input bibcodes.
        Note: Citation helper requires at least 2 input bibcodes to find intersection.
        
        :param bibcodes: List of at least 2 bibcodes.
        :param num_recommendations: Optional maximum number of recommendations to return.
        """
        cleaned = [b.strip() for b in bibcodes if b.strip()]
        if not cleaned:
            return []
        if len(cleaned) < 2:
            raise ValueError("Citation Helper requires at least 2 bibcodes to find overlapping co-citations.")

        payload = {
            "bibcodes": cleaned
        }
        res = self.client.post("citation_helper", json_data=payload)
        data = res.json()
        if isinstance(data, list):
            if num_recommendations and num_recommendations > 0:
                return data[:num_recommendations]
            return data
        return data
