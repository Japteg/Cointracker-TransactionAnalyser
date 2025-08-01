from abc import ABC, abstractmethod
from typing import Any, List, Dict
import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)


class DataExporterBase(ABC):
    """Base class for data exporters."""

    # This can also be made configurable, but for now I am hardcoding it
    OUTPUT_DIRECTORY = "transaction_reports"

    def __init__(self, columns: List[str]):
        self.columns = columns

    @abstractmethod
    def export(self, transactions: List[Dict[str, Any]], address: str) -> str:
        """Export data to a file."""
        pass

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to remove invalid characters."""
        # Remove or replace invalid characters
        sanitized = re.sub(r'[<>:"/\\|?*]', "_", filename)
        # Remove multiple consecutive underscores
        sanitized = re.sub(r"_{2,}", "_", sanitized)
        # Remove leading/trailing underscores and dots
        sanitized = sanitized.strip("_.")

        return sanitized

    def _validate_data(
        self, transactions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Validate and clean transaction data before export."""
        if not transactions:
            logger.warning("No transactions provided for validation")
            return []

        validated_transactions = []

        for i, tx in enumerate(transactions):
            try:
                # Ensure all required columns exist
                validated_tx = {}

                for column in self.columns:
                    value = tx.get(column, "")

                    if column == "date_time":
                        # Validate date format
                        if value:
                            try:
                                # Try to parse the date to ensure it's valid
                                datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
                            except ValueError:
                                logger.warning(
                                    f"Invalid date format in transaction {i}: {value}"
                                )
                                value = ""

                    validated_tx[column] = str(value) if value is not None else ""

                validated_transactions.append(validated_tx)

            except Exception as e:
                logger.error(f"Error validating transaction {i}: {str(e)}")
                continue

        logger.info(
            f"Validated {len(validated_transactions)} transactions out of {len(transactions)}"
        )
        return validated_transactions

    def _generate_filename(self, address: str) -> str:
        """Generate a descriptive filename for the CSV export."""
        # Use address and timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        short_address = (
            address[:6] + "..." + address[-4:] if len(address) > 10 else address
        )
        base_name = f"eth_transactions_{short_address}_{timestamp}"
        return f"{base_name}.csv"
