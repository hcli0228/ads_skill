import time
import logging
from typing import Any, Dict, Optional, Union
import requests
from ads_api.config import API_BASE_URL, get_ads_token

logger = logging.getLogger("ads_api")

class ADSError(Exception):
    """Base exception for ADS API errors."""
    def __init__(self, message: str, status_code: Optional[int] = None, response_body: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body

class ADSRateLimitError(ADSError):
    """Raised when ADS API rate limit (429) is exceeded."""
    pass

class ADSAuthError(ADSError):
    """Raised when authentication fails (401/403)."""
    pass

class ADSClient:
    """
    Core HTTP Client for interacting with the NASA ADS Developer API.
    Handles Bearer token auth, rate limits, retries, and headers.
    """
    def __init__(self, token: Optional[str] = None, base_url: str = API_BASE_URL, timeout: int = 30):
        self.token = get_ads_token(token)
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
        self.last_rate_limit: Optional[Dict[str, Any]] = None

    def _update_rate_limit(self, response: requests.Response):
        self.last_rate_limit = {
            "limit": response.headers.get("X-RateLimit-Limit"),
            "remaining": response.headers.get("X-RateLimit-Remaining"),
            "reset": response.headers.get("X-RateLimit-Reset"),
        }

    def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Union[Dict[str, Any], list]] = None,
        headers: Optional[Dict[str, str]] = None,
        max_retries: int = 3,
        backoff_factor: float = 1.5,
    ) -> requests.Response:
        """
        Execute an HTTP request against the ADS API with retry logic for transient issues.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        req_headers = dict(self.session.headers)
        if headers:
            req_headers.update(headers)

        for attempt in range(1, max_retries + 1):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                    headers=req_headers,
                    timeout=self.timeout
                )
                self._update_rate_limit(response)

                if response.status_code == 200:
                    return response
                elif response.status_code == 401 or response.status_code == 403:
                    raise ADSAuthError(f"Authentication failed: {response.text}", response.status_code, response.text)
                elif response.status_code == 429:
                    reset_time = response.headers.get("X-RateLimit-Reset", "unknown")
                    if attempt < max_retries:
                        sleep_sec = backoff_factor ** attempt
                        logger.warning(f"Rate limit exceeded (429). Retrying in {sleep_sec:.1f}s...")
                        time.sleep(sleep_sec)
                        continue
                    raise ADSRateLimitError(f"Rate limit exceeded. Reset at: {reset_time}", 429, response.text)
                elif response.status_code >= 500:
                    if attempt < max_retries:
                        sleep_sec = backoff_factor ** attempt
                        time.sleep(sleep_sec)
                        continue
                    raise ADSError(f"ADS server error ({response.status_code}): {response.text}", response.status_code, response.text)
                else:
                    raise ADSError(f"ADS API error ({response.status_code}): {response.text}", response.status_code, response.text)

            except requests.RequestException as e:
                if attempt < max_retries:
                    time.sleep(backoff_factor ** attempt)
                    continue
                raise ADSError(f"Network error communicating with ADS API: {str(e)}")

        raise ADSError(f"Request failed after {max_retries} attempts.")

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> requests.Response:
        return self.request("GET", endpoint, params=params, **kwargs)

    def post(self, endpoint: str, json_data: Optional[Union[Dict[str, Any], list]] = None, params: Optional[Dict[str, Any]] = None, **kwargs) -> requests.Response:
        return self.request("POST", endpoint, params=params, json_data=json_data, **kwargs)

    def put(self, endpoint: str, json_data: Optional[Union[Dict[str, Any], list]] = None, **kwargs) -> requests.Response:
        return self.request("PUT", endpoint, json_data=json_data, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        return self.request("DELETE", endpoint, **kwargs)

    def get_rate_limit(self) -> Dict[str, Any]:
        """Return the most recent rate limit information received from ADS."""
        return self.last_rate_limit or {}
