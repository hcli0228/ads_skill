from typing import Any, Dict, List, Optional
from ads_api.client import ADSClient

class JournalService:
    """
    Service for querying ADS Journals database (JournalsDB) metadata, holdings, and ISSN mapping.
    """
    def __init__(self, client: Optional[ADSClient] = None):
        self.client = client or ADSClient()

    def get_summary(self, bibstem: str) -> Dict[str, Any]:
        """
        Get complete summary for a publication by bibstem (case-sensitive, e.g. 'ApJ', 'PASJ').
        """
        res = self.client.get(f"journals/summary/{bibstem}")
        return res.json()

    def search_journal(self, text: str) -> Dict[str, Any]:
        """
        Search for journals containing the given text in name or abbreviation.
        """
        res = self.client.get(f"journals/journal/{text}")
        return res.json()

    def search_by_issn(self, issn: str) -> Dict[str, Any]:
        """
        Return the ADS bibstem for a journal matching the given ISSN.
        """
        res = self.client.get(f"journals/issn/{issn}")
        return res.json()

    def get_holdings(self, bibstem: str, volume: str) -> Dict[str, Any]:
        """
        Generate a list of available electronic sources for a given bibstem and volume.
        """
        res = self.client.get(f"journals/holdings/{bibstem}/{volume}")
        return res.json()

    def get_refsource(self, bibstem: str) -> Dict[str, Any]:
        """
        Generate a list of citation data sources on a per-volume basis for a given bibstem.
        """
        res = self.client.get(f"journals/refsource/{bibstem}")
        return res.json()
