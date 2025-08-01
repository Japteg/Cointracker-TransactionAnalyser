import pandas as pd
import csv
import os
import logging
from typing import List, Dict, Any

from data_exporter.data_exporter_base import DataExporterBase

logger = logging.getLogger(__name__)


class CSVExporter(DataExporterBase):
    """Exports transaction data to CSV format with proper formatting and validation."""
    
    # Standard CSV columns as per requirements
    CSV_COLUMNS = [
        'transaction_hash',
        'date_time', 
        'from_address',
        'to_address',
        'transaction_type',
        'asset_contract_address',
        'asset_symbol_name',
        'token_id',
        'value_amount',
        'gas_fee_eth'
    ]

    def __init__(self):
        super().__init__(self.CSV_COLUMNS)
    
    def export(self, transactions: List[Dict[str, Any]], address: str) -> str:
        """Export transactions to CSV file."""
        if not transactions:
            raise ValueError("No transactions provided for export")
        
        # Validate transaction data
        validated_transactions = self._validate_data(transactions)
        
        # Prepare output directory
        output_directory_path = f"./{self.OUTPUT_DIRECTORY}"
        os.makedirs(output_directory_path, exist_ok=True)
        
        # Generate filename
        filename = self._generate_filename(address)
        full_path = os.path.join(output_directory_path, filename)
        
        try:
            # Convert to DataFrame for easier manipulation
            df = pd.DataFrame(validated_transactions)
            
            # Ensure columns are in the correct order
            df = df.reindex(columns=self.CSV_COLUMNS, fill_value='')
            
            # Export to CSV
            df.to_csv(full_path, index=False, quoting=csv.QUOTE_MINIMAL, encoding='utf-8')
            
            logger.info(f"Successfully exported {len(validated_transactions)} transactions to ./{self.OUTPUT_DIRECTORY}/{filename}")
            
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
            type_counts = df['transaction_type'].value_counts().to_dict()
            
            # Date range
            date_range = ""
            if 'date_time' in df.columns and not df['date_time'].empty:
                valid_dates = df[df['date_time'] != '']['date_time']
                if not valid_dates.empty:
                    earliest = valid_dates.min()
                    latest = valid_dates.max()
                    date_range = f" (from {earliest} to {latest})"
            
            # Total gas fees
            total_gas_fees = 0
            if 'gas_fee_eth' in df.columns:
                try:
                    gas_fees = pd.to_numeric(df['gas_fee_eth'], errors='coerce').fillna(0)
                    total_gas_fees = gas_fees.sum()
                except:
                    pass
            
            print("\n\n--------------------------------")
            print(f"Export summary for {address}:")
            print(f"- Total transactions: {total_transactions}{date_range}")
            print(f"- Transaction types: {type_counts}")
            print(f"- Total gas fees: {total_gas_fees:.6f} ETH")
            print("--------------------------------\n\n")
            
        except Exception as e:
            logger.warning(f"Could not generate export summary: {str(e)}")