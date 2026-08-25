import io
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ads_api import ADS

@pytest.fixture
def ads():
    return ADS(token="mock_token_for_test")

def test_downloader_success_ads_pdf(ads, tmp_path):
    bibcode = "1965ApJ...142..419P"
    mock_pdf_content = b"%PDF-1.5 fake pdf content for testing"
    
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.raw = io.BytesIO(mock_pdf_content)
    mock_resp.iter_content = MagicMock(return_value=[b""])

    with patch.object(ads.downloader.session, "get", return_value=mock_resp):
        result = ads.downloader.download(bibcode, output_dir=str(tmp_path))
        assert result["status"] == "success"
        assert "NASA ADS 官方扫描文献库" in result["source"]
        assert Path(result["filepath"]).exists()
        assert Path(result["filepath"]).read_bytes() == mock_pdf_content

def test_downloader_rejects_html_and_fails_cleanly(ads, tmp_path):
    bibcode = "2014JGRA..119...36O"
    
    # 1. First call (ADS scan) returns 403
    resp_403 = MagicMock()
    resp_403.status_code = 403
    
    # 2. Resolver esource returns no records
    mock_esource = MagicMock()
    mock_esource.json.return_value = {"links": {"records": []}}

    # 3. Third call (Gateway PUB_PDF) returns HTML challenge
    html_content = b"<html><head><title>Cloudflare Challenge</title></head><body>Please verify</body></html>"
    resp_html = MagicMock()
    resp_html.status_code = 200
    resp_html.raw = io.BytesIO(html_content)

    def side_effect(url, **kwargs):
        if "articles.adsabs.harvard.edu" in url:
            return resp_403
        elif "resolver" in url:
            return mock_esource
        elif "link_gateway" in url:
            return resp_html
        return resp_403

    with patch.object(ads.downloader.session, "get", side_effect=side_effect), \
         patch.object(ads.downloader.client, "get", return_value=mock_esource):
        result = ads.downloader.download(bibcode, output_dir=str(tmp_path))
        assert result["status"] == "failed"
        assert "无法下载该文献全文" in result["message"]
