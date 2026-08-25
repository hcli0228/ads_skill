"""
ADS API Toolkit - Python interface to NASA Astrophysics Data System (ADS) Developer API.
"""

from ads_api.client import ADSClient, ADSError, ADSRateLimitError, ADSAuthError
from ads_api.search import SearchService
from ads_api.metrics import MetricsService
from ads_api.export import ExportService
from ads_api.libraries import LibraryService
from ads_api.journals import JournalService
from ads_api.resolver import ResolverService
from ads_api.citation_helper import CitationHelperService

class ADS:
    """
    Unified NASA ADS API Manager combining all services.
    """
    def __init__(self, token: str = None, timeout: int = 30):
        self.client = ADSClient(token=token, timeout=timeout)
        self.search = SearchService(self.client)
        self.metrics = MetricsService(self.client)
        self.export = ExportService(self.client)
        self.libraries = LibraryService(self.client)
        self.journals = JournalService(self.client)
        self.resolver = ResolverService(self.client)
        self.citation_helper = CitationHelperService(self.client)

    @property
    def rate_limit(self):
        return self.client.get_rate_limit()

__all__ = [
    "ADS",
    "ADSClient",
    "SearchService",
    "MetricsService",
    "ExportService",
    "LibraryService",
    "JournalService",
    "ResolverService",
    "CitationHelperService",
    "ADSError",
    "ADSRateLimitError",
    "ADSAuthError",
]
