import logging
from typing import List, Dict, Any
from datetime import datetime
from decimal import Decimal, InvalidOperation

from analyzer.base_transaction_analyzer import BaseTransactionAnalyzer

logger = logging.getLogger(__name__)


class EthereumTransactionAnalyzer(BaseTransactionAnalyzer):
    """Analyzes and categorizes Ethereum transactions from various sources."""
    
    # Standard transaction types
    TRANSACTION_TYPES = {
        'normal': 'ETH Transfer',
        'erc20': 'ERC-20 Transfer', 
        'erc721': 'ERC-721 Transfer',
        'erc1155': 'ERC-1155 Transfer',
        'internal': 'Internal Transfer',
        'contract_interaction': 'Contract Interaction'
    }
    
    def __init__(self):
        self.processed_transactions = []
    
    def _convert_wei_to_eth(self, wei_value: str) -> str:
        """Convert Wei to ETH with proper decimal handling."""
        try:
            if not wei_value or wei_value == '0':
                return '0'
            
            # Convert to Decimal for precise arithmetic
            wei_decimal = Decimal(str(wei_value))
            eth_decimal = wei_decimal / Decimal('1000000000000000000')  # 1 ETH = 10^18 Wei
            
            # Format to avoid scientific notation and trailing zeros
            return f"{eth_decimal:.18f}".rstrip('0').rstrip('.')
            
        except (InvalidOperation, ValueError) as e:
            logger.warning(f"Error converting Wei to ETH: {wei_value}, error: {e}")
            return '0'
    
    def _convert_timestamp(self, timestamp: str) -> str:
        """Convert Unix timestamp to readable datetime string."""
        try:
            if not timestamp:
                return ''
            
            dt = datetime.fromtimestamp(int(timestamp))
            return dt.strftime('%Y-%m-%d %H:%M:%S')
            
        except (ValueError, OSError) as e:
            logger.warning(f"Error converting timestamp: {timestamp}, error: {e}")
            return ''
    
    def _calculate_gas_fee(self, gas_used: str, gas_price: str) -> str:
        """Calculate total gas fee in ETH."""
        try:
            if not gas_used or not gas_price:
                return '0'
            
            gas_used_decimal = Decimal(str(gas_used))
            gas_price_decimal = Decimal(str(gas_price))
            
            # Gas fee in Wei = gas_used * gas_price
            gas_fee_wei = gas_used_decimal * gas_price_decimal
            
            # Convert to ETH
            return self._convert_wei_to_eth(str(gas_fee_wei))
            
        except (InvalidOperation, ValueError) as e:
            logger.warning(f"Error calculating gas fee: gas_used={gas_used}, gas_price={gas_price}, error: {e}")
            return '0'
    
    def _process_transaction(self, tx: Dict[str, Any], transaction_type: str) -> Dict[str, Any]:
        """Process an Ethereum transaction."""
        return {
            'transaction_hash': tx.get('hash', ''),
            'date_time': self._convert_timestamp(tx.get('timeStamp', '')),
            'from_address': tx.get('from', ''),
            'to_address': tx.get('to', ''),
            'transaction_type': transaction_type,
            'asset_contract_address': tx.get('contractAddress', ''),
            'asset_symbol_name': 'ETH',
            'token_id': '',  # Not applicable for ETH
            'value_amount': self._convert_wei_to_eth(tx.get('value', '0')),
            'gas_fee_eth': self._calculate_gas_fee(tx.get('gasUsed', '0'), tx.get('gasPrice', '0')),
            'block_number': tx.get('blockNumber', ''),
            'transaction_index': tx.get('transactionIndex', ''),
            'input_data': tx.get('input', ''),
            'is_error': tx.get('isError', '0') == '1'
        }

    def analyze(self, raw_transaction_data: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Analyze and categorize all transaction types."""
        print("\n\n--------------------------------")
        print("Starting transaction analysis...\n")
        
        processed_transactions = []
        
        for tx_type, transactions in raw_transaction_data.items():
            if tx_type in self.TRANSACTION_TYPES:
                print(f"Processing {len(transactions)} {tx_type} transactions")
                
                for tx in transactions:
                    try:
                        processed_tx = self._process_transaction(tx, self.TRANSACTION_TYPES[tx_type])
                        processed_transactions.append(processed_tx)
                    except Exception as e:
                        logger.error(f"Error processing {tx_type} transaction {tx.get('hash', 'unknown')}: {str(e)}")
                        continue
        
        print(f"Successfully processed {len(processed_transactions)} total transactions")
        print("--------------------------------\n\n")
        self.processed_transactions = processed_transactions
        
        return processed_transactions