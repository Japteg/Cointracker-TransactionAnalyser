import logging
from analyzer.base_transaction_analyzer import BaseTransactionAnalyzer
from data_exporter.data_exporter_base import DataExporterBase
from external_data_providers.external_data_provider_base_client import ExternalDataProviderBaseClient

logger = logging.getLogger(__name__)

class CoinTrackerService:
    def __init__(self, data_provider_client: ExternalDataProviderBaseClient, transaction_analyzer: BaseTransactionAnalyzer, data_exporter: DataExporterBase):
        # I have use composition to make it more flexible and easy to extend
        self.data_provider_client = data_provider_client
        self.transaction_analyzer = transaction_analyzer
        self.data_exporter = data_exporter

    def generate_transaction_report(self, address: str):
        """
        Generate a transaction report for a given address
        """
        # Get all the transaction data using the external client
        raw_data = self.data_provider_client.get_all_transactions(address=address)

        logger.info("Initializing transaction analyzer...")
        processed_transactions = self.transaction_analyzer.analyze(raw_data)

        logger.info("Initializing CSV exporter...")
        export_path = self.data_exporter.export(processed_transactions, address)

        print(f"\nTransactions exported to: {export_path}")
        logger.info("Transaction analysis completed successfully")