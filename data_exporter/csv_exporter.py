import pandas as pd
import csv
import os
import logging

from data_exporter.data_exporter_base import DataExporterBase
from domain_models import TransactionListDomainModel

logger = logging.getLogger(__name__)


class CSVExporter(DataExporterBase):
    """Exports transaction data to CSV format with proper formatting and validation."""

    # Standard CSV columns as per requirements
    CSV_COLUMNS = [
        "transaction_hash",
        "date_time",
        "from_address",
        "to_address",
        "transaction_type",
        "contract_address",
        "asset_symbol",
        "asset_name",
        "token_id",
        "value_amount_eth",
        "gas_fee_eth",
    ]

    def __init__(self):
        super().__init__(self.CSV_COLUMNS)

    def export(self, transactions: TransactionListDomainModel, address: str) -> str:
        """Export transactions to CSV file."""
        # Prepare output directory
        output_directory_path = f"./{self.OUTPUT_DIRECTORY}"
        os.makedirs(output_directory_path, exist_ok=True)

        # Generate filename
        filename = self._generate_filename(address)
        full_path = os.path.join(output_directory_path, filename)

        try:
            # Convert to DataFrame
            # df = pd.DataFrame(validated_transactions)
            df = pd.DataFrame(transactions.model_dump())

            # Ensure columns are in the correct order
            df = df.reindex(columns=self.CSV_COLUMNS, fill_value="")

            # Export to CSV
            df.to_csv(
                full_path, index=False, quoting=csv.QUOTE_MINIMAL, encoding="utf-8"
            )

            logger.info(
                f"Successfully exported {len(transactions.root)} transactions to ./{self.OUTPUT_DIRECTORY}/{filename}"
            )

            # Log summary statistics
            self._log_export_summary(df, address)

            return full_path

        except Exception as e:
            logger.error(f"Error exporting to CSV: {str(e)}")
            raise

    def _log_export_summary(self, df: pd.DataFrame, address: str):
        """Log summary statistics of the exported data."""
        try:
            total_transactions = len(df)

            # Count by transaction type
            type_counts = df["transaction_type"].value_counts().to_dict()

            # Date range
            date_range = ""
            if "date_time" in df.columns and not df["date_time"].empty:
                valid_dates = df[df["date_time"] != ""]["date_time"]
                if not valid_dates.empty:
                    earliest = valid_dates.min()
                    latest = valid_dates.max()
                    date_range = f" (from {earliest} to {latest})"

            # Total gas fees
            total_gas_fees = 0
            if "gas_fee_eth" in df.columns:
                try:
                    gas_fees = pd.to_numeric(df["gas_fee_eth"], errors="coerce").fillna(
                        0
                    )
                    total_gas_fees = gas_fees.sum()
                except Exception as err:
                    logger.warning(f"Error calculating total gas fee. Error: {err}")

            # All these print statements can be extracted out to a common utility
            # but not doing that for now due to time constraints
            print("\n\n--------------------------------")
            print(f"Export summary for {address}:")
            print(f"- Total transactions: {total_transactions}{date_range}")
            print(f"- Transaction types:")
            for txn_type, count in type_counts.items():
                print(f"   -{txn_type}: {count}")
            print(f"- Total gas fees: {total_gas_fees:.6f} ETH")
            print("--------------------------------\n\n")

        except Exception as e:
            logger.warning(f"Could not generate export summary: {str(e)}")
