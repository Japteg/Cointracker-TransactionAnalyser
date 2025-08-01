import logging
from typing import List, Dict, Any

from analyzer.base_transaction_analyzer import BaseTransactionAnalyzer
from domain_models import (
    TransactionDomainModel,
    EthereumTransactionType,
    TransactionListDomainModel,
)
from utils import calculate_gas_fee, convert_timestamp, convert_wei_to_eth


logger = logging.getLogger(__name__)


class EthereumTransactionAnalyzer(BaseTransactionAnalyzer):
    """
    Analyzes and categorizes Ethereum transactions from various sources.
    Responsible for
    - Assigning the correct transaction type
    - Calculating gas fee
    - Formatting date time
    - Calculating value amount in eth
    This class should implement all the processing and calculation logic.
    The output can be used by exporter class to save the data
    """

    # Standard transaction types
    TRANSACTION_TYPES_DISPLAY_NAMES = {
        EthereumTransactionType.NORMAL.value: "ETH Transfer",
        EthereumTransactionType.ERC20.value: "ERC-20 Transfer",
        EthereumTransactionType.ERC721.value: "ERC-721 Transfer",
        EthereumTransactionType.ERC1155.value: "ERC-1155 Transfer",
        EthereumTransactionType.INTERNAL.value: "Internal Transfer",
    }

    @staticmethod
    def _process_transaction(
        tx: Dict[str, Any], transaction_type: str
    ) -> TransactionDomainModel:
        """
        Process an Ethereum transaction.
        Returns a structured domain model of the transaction.
        """
        return TransactionDomainModel(
            transaction_hash=tx.get("hash", ""),
            date_time=convert_timestamp(tx.get("timeStamp", "")),
            from_address=tx.get("from", ""),
            to_address=tx.get("to", ""),
            transaction_type=transaction_type,
            contract_address=tx.get("contractAddress", ""),
            asset_symbol="ETH"
            if transaction_type == "ETH Transfer"
            else tx.get("tokenSymbol", ""),
            asset_name=tx.get("tokenName", ""),
            token_id=tx.get("tokenID", ""),
            value_amount_eth=convert_wei_to_eth(tx.get("value", "0")),
            gas=tx.get("gas", "0"),
            gas_price=tx.get("gasPrice", "0"),
            gas_used=tx.get("gasUsed", "0"),
            gas_fee_eth=calculate_gas_fee(
                tx.get("gasUsed", "0"), tx.get("gasPrice", "0")
            ),
            is_error=tx.get("isError", "0") == "1",
        )

    def analyze(
        self, raw_transaction_data: Dict[str, List[Dict[str, Any]]]
    ) -> TransactionListDomainModel:
        """Analyze and categorize all transaction types."""
        print("\n\n--------------------------------")
        print("Starting transaction analysis...\n")

        processed_transactions = []

        for tx_type, transactions in raw_transaction_data.items():
            if tx_type in self.TRANSACTION_TYPES_DISPLAY_NAMES:
                print(f"Processing {len(transactions)} {tx_type} transactions")

                for tx in transactions:
                    try:
                        processed_tx = self._process_transaction(
                            tx, self.TRANSACTION_TYPES_DISPLAY_NAMES[tx_type]
                        )
                        processed_transactions.append(processed_tx)
                    except Exception as e:
                        logger.error(
                            f"Error processing {tx_type} transaction {tx.get('hash', 'unknown')}: {str(e)}"
                        )
                        continue

        print(
            f"Successfully processed {len(processed_transactions)} total transactions"
        )
        print("--------------------------------\n\n")

        return TransactionListDomainModel(root=processed_transactions)
