from decimal import Decimal, InvalidOperation
from datetime import datetime
import logging

from constants import ETH_TO_WEI_MULTIPLIER


logger = logging.getLogger(__name__)


def convert_wei_to_eth(wei_value: str) -> str:
    """Convert Wei to ETH with proper decimal handling."""
    try:
        if not wei_value or wei_value == '0':
            return '0'
        
        # Convert to Decimal for precise arithmetic
        wei_decimal = Decimal(str(wei_value))
        eth_decimal = wei_decimal / ETH_TO_WEI_MULTIPLIER
        
        # Format to avoid scientific notation and trailing zeros
        return f"{eth_decimal:.18f}".rstrip('0').rstrip('.')
        
    except (InvalidOperation, ValueError) as e:
        logger.warning(f"Error converting Wei to ETH: {wei_value}, error: {e}")
        return '0'


def convert_timestamp(timestamp: str) -> str:
    """Convert Unix timestamp to readable datetime string."""
    try:
        if not timestamp:
            return ''
        
        dt = datetime.fromtimestamp(int(timestamp))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
        
    except (ValueError, OSError) as e:
        logger.warning(f"Error converting timestamp: {timestamp}, error: {e}")
        return ''


def calculate_gas_fee(gas_used: str, gas_price: str) -> str:
    """Calculate total gas fee in ETH."""
    try:
        if not gas_used or not gas_price:
            return '0'
        
        gas_used_decimal = Decimal(str(gas_used))
        gas_price_decimal = Decimal(str(gas_price))
        
        # Gas fee in Wei = gas_used * gas_price
        gas_fee_wei = gas_used_decimal * gas_price_decimal
        
        # Convert to ETH
        return convert_wei_to_eth(str(gas_fee_wei))
        
    except (InvalidOperation, ValueError) as e:
        logger.warning(f"Error calculating gas fee: gas_used={gas_used}, gas_price={gas_price}, error: {e}")
        return '0'