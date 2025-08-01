from typing import List, Dict, Any
import logging
from api_client import ApiClient
from domain_models import EthereumTransactionType
from external_data_providers.external_data_provider_base_client import ExternalDataProviderBaseClient

logger = logging.getLogger(__name__)


class EtherscanApiClient(ExternalDataProviderBaseClient):
    """Etherscan API client for fetching Ethereum transaction data."""
    
    BASE_URL = "https://api.etherscan.io/api"

    TRANSACTION_ACTIONS = {
        EthereumTransactionType.ERC20.value: 'tokentx',
        EthereumTransactionType.ERC721.value: 'tokennfttx',
        EthereumTransactionType.ERC1155.value: 'token1155tx',
        EthereumTransactionType.NORMAL.value: 'txlist',
        EthereumTransactionType.INTERNAL.value: 'txlistinternal',
    }
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.api_client = ApiClient()
    
    def _get_transactions(self, address: str, action: str, transaction_type: str, page: int = 1, offset: int = 10000, sort: str = 'asc') -> List[Dict[str, Any]]:
        transactions = []
        start_block = 0
        batch_number = 1
        while True:
            print(f"---- Transaction type: {transaction_type.upper()}, Fetching batch {batch_number} of transactions for {address} ----")
            params = {
                'module': 'account',
                'action': action,
                'address': address,
                'startblock': start_block,
                'endblock': "latest",
                'page': page,
                'offset': offset,
                'sort': sort,
                "apiKey": self.api_key
            }
            response = self.api_client.get(self.BASE_URL, params)
            result = response.get('result', [])
            transactions.extend(result)
            
            # If the number of transactions is less than the offset, we have fetched all transactions
            if len(result) < offset:
                break

            last_block_number = int(result[-1].get('blockNumber'))
            if last_block_number == start_block:
                break
            # Start block for the next batch
            start_block = last_block_number + 1
            batch_number += 1
        print(f"---- Completed fetching transactions of type: {transaction_type.upper()}, Fetched {len(transactions)} transactions ----")
        return transactions
    
    def get_all_transactions(self, address: str, max_transactions: int = 10000) -> Dict[str, List[Dict[str, Any]]]:
        """Fetch all types of transactions for an address."""
        logger.info(f"Starting comprehensive transaction fetch for {address}")
        
        try:
            results = {}

            for txn_type, action in self.TRANSACTION_ACTIONS.items():
                results[txn_type] = self._get_transactions(address, action, txn_type)
            
            total_txns = sum(len(txns) for txns in results.values())
            logger.info(f"Successfully fetched {total_txns} total transactions")
            
            return results
            
        except Exception as e:
            logger.error(f"Error fetching transactions for {address}: {str(e)}")
            raise
