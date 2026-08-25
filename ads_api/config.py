import os
from pathlib import Path
from dotenv import load_dotenv

# Automatically look for .env in current working dir and parent dirs
load_dotenv()
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

def get_ads_token(token: str = None) -> str:
    """
    Retrieve ADS token from argument, environment variables, or .env file.
    Priority:
      1. Explicit function argument
      2. ADS_DEV_KEY
      3. ADS_API_TOKEN
      4. ADS_TOKEN
    """
    if token:
        return token
    
    token = os.getenv("ADS_DEV_KEY") or os.getenv("ADS_API_TOKEN") or os.getenv("ADS_TOKEN")
    if not token:
        raise ValueError(
            "ADS API Token is missing. Please set ADS_DEV_KEY or ADS_API_TOKEN in .env or environment variable, "
            "or pass it directly. You can obtain one at https://ui.adsabs.harvard.edu/user/settings/token"
        )
    return token.strip()

API_BASE_URL = os.getenv("ADS_API_BASE_URL", "https://api.adsabs.harvard.edu/v1")
