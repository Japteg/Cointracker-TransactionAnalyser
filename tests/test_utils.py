from decimal import Decimal
from unittest.mock import patch

from utils import convert_wei_to_eth, convert_timestamp, calculate_gas_fee


class TestConvertWeiToEth:
    """Test suite for convert_wei_to_eth utility function."""

    def test_convert_zero_wei(self):
        """Test conversion of 0 Wei."""
        assert convert_wei_to_eth("0") == "0"
        assert convert_wei_to_eth("") == "0"

    def test_convert_one_eth_in_wei(self):
        """Test conversion of 1 ETH worth of Wei."""
        one_eth_wei = "1000000000000000000"  # 10^18
        result = convert_wei_to_eth(one_eth_wei)
        assert result == "1"

    def test_convert_fractional_eth(self):
        """Test conversion of fractional ETH amounts."""
        half_eth_wei = "500000000000000000"  # 0.5 ETH
        result = convert_wei_to_eth(half_eth_wei)
        assert result == "0.5"

    def test_convert_small_amount(self):
        """Test conversion of very small Wei amounts."""
        small_wei = "1"  # 1 Wei = 10^-18 ETH
        result = convert_wei_to_eth(small_wei)
        # Should be 0.000000000000000001 but trailing zeros removed
        assert result == "0.000000000000000001"

    def test_convert_large_amount(self):
        """Test conversion of large Wei amounts."""
        large_wei = "1000000000000000000000"  # 1000 ETH
        result = convert_wei_to_eth(large_wei)
        assert result == "1000"

    def test_convert_with_precision(self):
        """Test conversion maintaining precision."""
        # 1.123456789012345678 ETH in Wei
        precise_wei = "1123456789012345678"
        result = convert_wei_to_eth(precise_wei)
        assert result == "1.123456789012345678"

    def test_convert_removes_trailing_zeros(self):
        """Test that trailing zeros are removed."""
        # 1.1 ETH in Wei (with trailing zeros when converted)
        wei_with_trailing = "1100000000000000000"
        result = convert_wei_to_eth(wei_with_trailing)
        assert result == "1.1"

    @patch("utils.logger")
    def test_convert_invalid_wei_value(self, mock_logger):
        """Test handling of invalid Wei values."""
        result = convert_wei_to_eth("invalid")
        assert result == "0"
        mock_logger.warning.assert_called_once()

    @patch("utils.logger")
    def test_convert_none_value(self, mock_logger):
        """Test handling of None value."""
        result = convert_wei_to_eth(None)
        assert result == "0"

    def test_convert_decimal_input(self):
        """Test conversion with Decimal input."""
        result = convert_wei_to_eth(str(Decimal("1000000000000000000")))
        assert result == "1"


class TestCalculateGasFee:
    """Test suite for calculate_gas_fee utility function."""

    def test_calculate_standard_gas_fee(self):
        """Test calculation of standard gas fee."""
        gas_used = "21000"  # Standard ETH transfer
        gas_price = "20000000000"  # 20 Gwei
        result = calculate_gas_fee(gas_used, gas_price)
        # 21000 * 20000000000 = 420000000000000 Wei = 0.00042 ETH
        assert result == "0.00042"

    def test_calculate_high_gas_fee(self):
        """Test calculation of high gas fee."""
        gas_used = "100000"  # Complex transaction
        gas_price = "100000000000"  # 100 Gwei
        result = calculate_gas_fee(gas_used, gas_price)
        # 100000 * 100000000000 = 10000000000000000 Wei = 0.01 ETH
        assert result == "0.01"

    def test_calculate_zero_gas_fee(self):
        """Test calculation with zero gas."""
        assert calculate_gas_fee("0", "20000000000") == "0"
        assert calculate_gas_fee("21000", "0") == "0"
        assert calculate_gas_fee("0", "0") == "0"

    def test_calculate_empty_values(self):
        """Test calculation with empty values."""
        assert calculate_gas_fee("", "20000000000") == "0"
        assert calculate_gas_fee("21000", "") == "0"
        assert calculate_gas_fee("", "") == "0"
