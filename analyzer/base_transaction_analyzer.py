from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseTransactionAnalyzer(ABC):
    """Base class for transaction analyzers."""

    @abstractmethod
    def analyze(self, raw_transaction_data: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        pass