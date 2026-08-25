from typing import Any, Dict, List, Optional
from ads_api.client import ADSClient

class ExportService:
    """
    Service for exporting ADS literature records into various bibliographic and citation formats.
    """
    SUPPORTED_FORMATS = [
        "bibtex", "bibtexabs", "ads", "endnote", "procite", "ris",
        "refworks", "medlars", "dcxml", "refxml", "refabsxml",
        "aastex", "icarus", "mnras", "soph", "votable", "custom"
    ]

    def __init__(self, client: Optional[ADSClient] = None):
        self.client = client or ADSClient()

    def export(
        self,
        bibcodes: List[str],
        format_name: str = "bibtex",
        sort: Optional[str] = None,
        custom_format: Optional[str] = None
    ) -> str:
        """
        Export records in the specified format.
        
        :param bibcodes: List of bibcode strings
        :param format_name: Export format (e.g. 'bibtex', 'ris', 'endnote', 'aastex', 'custom')
        :param sort: Optional sort order, e.g. 'date desc', 'author asc'
        :param custom_format: Required if format_name is 'custom', string template with formatting codes.
        :return: Formatted string containing the exported bibliography/data.
        """
        fmt = format_name.lower().strip()
        if fmt not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format '{fmt}'. Supported formats are: {', '.join(self.SUPPORTED_FORMATS)}")

        if fmt == "custom" and not custom_format:
            raise ValueError("custom_format template string is required when format_name is 'custom'.")

        payload: Dict[str, Any] = {
            "bibcode": [b.strip() for b in bibcodes if b.strip()]
        }
        if sort:
            payload["sort"] = sort
        if custom_format:
            payload["format"] = custom_format

        res = self.client.post(f"export/{fmt}", json_data=payload)
        data = res.json()
        return data.get("export", "")
