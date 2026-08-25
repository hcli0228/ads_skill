import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import requests
from ads_api.client import ADSClient, ADSError

class DownloaderService:
    """
    Service for downloading fulltext papers strictly from:
    1. ADS Scanned/Hosted articles (ADS_PDF / ADS_SCAN on articles.adsabs.harvard.edu)
    3. Publisher Open Access articles (PUB_PDF via ADS Resolver / Link Gateway)
    
    * Explicitly excludes arXiv / EPRINT preprints (Route 2).
    * Handles anti-bot / Cloudflare challenge detection and magic-byte PDF validation.
    """

    DEFAULT_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        "Referer": "https://ui.adsabs.harvard.edu/",
    }

    def __init__(self, client: Optional[ADSClient] = None, timeout: int = 15):
        self.client = client or ADSClient()
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(self.DEFAULT_HEADERS)

    def _try_download_stream(self, url: str, output_file: Path) -> Dict[str, Any]:
        """
        Attempt to stream and validate a PDF URL.
        Rejects HTML challenge pages, captcha blocks, and paywalled responses.
        """
        try:
            resp = self.session.get(url, allow_redirects=True, timeout=self.timeout, stream=True)
            if resp.status_code != 200:
                return {
                    "success": False,
                    "reason": f"HTTP {resp.status_code} (服务器拒绝访问、链接失效或需要付费订阅)"
                }

            # Check initial bytes for valid PDF header (%PDF-)
            first_chunk = resp.raw.read(1024)
            if not first_chunk.startswith(b"%PDF"):
                # Usually an anti-bot challenge (Cloudflare/Akamai) or HTML paywall page
                return {
                    "success": False,
                    "reason": "目标网站拦截了下载请求（返回 HTML/反爬验证页面）或未提供直接 PDF 资源"
                }

            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, "wb") as f:
                f.write(first_chunk)
                for chunk in resp.iter_content(chunk_size=65536):
                    if chunk:
                        f.write(chunk)

            file_size_kb = output_file.stat().st_size / 1024
            return {
                "success": True,
                "size_kb": file_size_kb,
                "filepath": str(output_file.resolve())
            }
        except requests.Timeout:
            return {
                "success": False,
                "reason": f"请求超时（超过 {self.timeout} 秒，可能被目标服务器防火墙拦截）"
            }
        except requests.RequestException as e:
            return {
                "success": False,
                "reason": f"网络请求异常: {str(e)}"
            }

    def download(self, bibcode: str, output_dir: str = "./downloads", filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Download a paper PDF for a given bibcode strictly via Route 1 (ADS Scanned) or Route 3 (Publisher OA).
        Excludes arXiv preprints.
        """
        clean_bibcode = bibcode.strip()
        out_dir = Path(output_dir)
        fname = filename or f"{clean_bibcode.replace('/', '_')}.pdf"
        target_file = out_dir / fname

        failed_details: List[str] = []

        # ==========================================
        # Route 1: Direct ADS Scanned/Classic Archive
        # ==========================================
        ads_scan_url = f"https://articles.adsabs.harvard.edu/pdf/{clean_bibcode}"
        res1 = self._try_download_stream(ads_scan_url, target_file)
        if res1["success"]:
            return {
                "bibcode": clean_bibcode,
                "status": "success",
                "source": "ADS_PDF (NASA ADS 官方扫描文献库)",
                "filepath": res1["filepath"],
                "size_kb": f"{res1['size_kb']:.1f} KB",
                "message": "下载成功：已从 NASA ADS 官方扫描文献库获取全文 PDF。"
            }
        failed_details.append(f"途径 1 (ADS 官方扫描件): {res1['reason']}")

        # ==========================================
        # Route 3: Publisher Open Access (PUB_PDF)
        # ==========================================
        candidate_urls: List[tuple] = []
        
        # 1. Query ADS Resolver ESOURCE
        try:
            esource_res = self.client.get(f"resolver/{clean_bibcode}/esource").json()
            records = esource_res.get("links", {}).get("records", [])
            for r in records:
                link_type = r.get("link_type", "").upper()
                url = r.get("url", "")
                # Strictly only match PUB_PDF or ADS_PDF (ignore EPRINT/ARXIV)
                if "PUB_PDF" in link_type:
                    candidate_urls.append(("PUB_PDF (出版商开放获取直链)", url))
                elif "ADS_PDF" in link_type or "ADS_SCAN" in link_type:
                    candidate_urls.append(("ADS_PDF (ADS 托管)", url))
        except (ADSError, Exception):
            pass

        # 2. Fallback to ADS Link Gateway PUB_PDF
        gateway_pub_url = f"https://ui.adsabs.harvard.edu/link_gateway/{clean_bibcode}/PUB_PDF"
        candidate_urls.append(("PUB_PDF (ADS Gateway 出版商跳转)", gateway_pub_url))

        # Try all publisher candidate URLs
        for source_name, url in candidate_urls:
            res_pub = self._try_download_stream(url, target_file)
            if res_pub["success"]:
                return {
                    "bibcode": clean_bibcode,
                    "status": "success",
                    "source": source_name,
                    "filepath": res_pub["filepath"],
                    "size_kb": f"{res_pub['size_kb']:.1f} KB",
                    "message": f"下载成功：已从 {source_name} 获取全文 PDF。"
                }
            failed_details.append(f"{source_name}: {res_pub['reason']}")

        # Both routes failed
        return {
            "bibcode": clean_bibcode,
            "status": "failed",
            "message": "无法下载该文献全文：已排除 arXiv 预印本，途径 1（ADS 扫描库）与途径 3（出版商开放获取）均未能获取有效 PDF（可能受付费墙限制或网站反爬验证拦截）。",
            "details": failed_details
        }
