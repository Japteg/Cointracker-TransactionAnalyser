from typing import Any, Dict
import time
import requests
import logging

logger = logging.getLogger(__name__)


class ApiClient:
    MAX_RETRIES = 3

    def get(
        self,
        url: str,
        params: Dict[str, Any],
        headers: Dict[str, Any] = {},
        timeout: int = 30,
    ) -> Dict[str, Any]:
        for attempt in range(self.MAX_RETRIES):
            try:
                response = requests.get(url, params=params, timeout=timeout)
                response.raise_for_status()
                data = response.json()
                return data
            except requests.RequestException as e:
                logger.error(f"Request failed (attempt {attempt + 1}): {str(e)}")
                # Exponential backoff
                time.sleep(2**attempt)

        raise Exception("Max retries exceeded")
