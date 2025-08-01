from abc import ABC, abstractmethod
from typing import List, Dict, Any


class ExternalDataProviderBaseClient(ABC):
    """Base class for external data providers."""

    def __init__(self, api_key: str):
        self.api_key = api_key

    @abstractmethod
    def get_all_transactions(
        self, address: str, max_transactions: int = 10000
    ) -> Dict[str, List[Dict[str, Any]]]:
        pass
