"""HTTP helpers and session configuration."""

from __future__ import annotations

import random
import time
from typing import Optional

import requests


def safe_get(
    session: requests.Session,
    url: str,
    retries: int = 2,
    timeout: int = 15,
    user_agent: Optional[str] = None,
) -> requests.Response:
    """
    Make an HTTP GET request with retry logic and proper headers.
    """
    headers = {
        "User-Agent": user_agent or "OlympediaBulkScraper/1.1 (+https://example.com)",
        "Accept-Language": "en;q=0.9",
    }

    for attempt in range(retries + 1):
        try:
            response = session.get(url, headers=headers, timeout=timeout)
            return response
        except requests.RequestException as e:
            if attempt == retries:
                raise e
            time.sleep(1.0 + random.random())
