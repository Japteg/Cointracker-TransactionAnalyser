import pytest
from unittest.mock import Mock, patch

from analyzer.transaction_analyzer import EthereumTransactionAnalyzer
from domain_models import (
    TransactionDomainModel,
    EthereumTransactionType,
    TransactionListDomainModel,
)


class TestEthereumTransactionAnalyzer:
    """Test suite for EthereumTransactionAnalyzer class."""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance for testing."""
        return EthereumTransactionAnalyzer()

    @pytest.fixture
    def sample_eth_transaction(self):
        """Sample ETH transaction data from Etherscan API."""
        return {
            "hash": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
            "timeStamp": "1640995200",
            "from": "0xfrom1234567890abcdef1234567890abcdef12345678",
            "to": "0xto1234567890abcdef1234567890abcdef123456789",
            "value": "1000000000000000000",
            "gas": "21000",
            "gasPrice": "20000000000",
            "gasUsed": "21000",
            "isError": "0",
            "contractAddress": "",
        }

    @pytest.fixture
    def sample_erc20_transaction(self):
        """Sample ERC-20 transaction data from Etherscan API."""
        return {
            "hash": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
            "timeStamp": "1640995260",
            "from": "0xfrom1234567890abcdef1234567890abcdef12345678",
            "to": "0xto1234567890abcdef1234567890abcdef123456789",
            "value": "1000000000000000000000",
            "gas": "65000",
            "gasPrice": "15000000000",
            "gasUsed": "45000",
            "isError": "0",
            "contractAddress": "0xcontract1234567890abcdef1234567890abcdef12",
            "tokenSymbol": "USDC",
            "tokenName": "USD Coin",
        }

    @pytest.fixture
    def sample_raw_data(self, sample_eth_transaction, sample_erc20_transaction):
        """Sample raw transaction data grouped by type."""
        return {
            "normal": [sample_eth_transaction],
            "erc20": [sample_erc20_transaction],
            "internal": [],
            "erc721": [],
            "erc1155": [],
        }

    @patch("analyzer.transaction_analyzer.convert_timestamp")
    @patch("analyzer.transaction_analyzer.convert_wei_to_eth")
    @patch("analyzer.transaction_analyzer.calculate_gas_fee")
    def test_process_transaction_eth_transfer(
        self,
        mock_gas_fee,
        mock_wei_to_eth,
        mock_timestamp,
        analyzer,
        sample_eth_transaction,
    ):
        """Test processing of ETH transfer transaction."""
        # Mock utility function returns
        mock_timestamp.return_value = "2022-01-01 00:00:00"
        mock_wei_to_eth.return_value = "1.0"
        mock_gas_fee.return_value = "0.00042"

        result = analyzer._process_transaction(sample_eth_transaction, "ETH Transfer")

        # Verify the result is a TransactionDomainModel
        assert isinstance(result, TransactionDomainModel)

        # Verify all fields are correctly mapped
        assert result.transaction_hash == sample_eth_transaction["hash"]
        assert result.date_time == "2022-01-01 00:00:00"
        assert result.from_address == sample_eth_transaction["from"]
        assert result.to_address == sample_eth_transaction["to"]
        assert result.transaction_type == "ETH Transfer"
        assert result.contract_address == ""
        assert result.asset_symbol == "ETH"  # Should be ETH for ETH transfers
        assert result.asset_name == ""
        assert result.token_id == ""
        assert result.value_amount_eth == "1.0"
        assert result.gas == "21000"
        assert result.gas_price == "20000000000"
        assert result.gas_used == "21000"
        assert result.gas_fee_eth == "0.00042"
        assert result.is_error is False

        # Verify utility functions were called with correct parameters
        mock_timestamp.assert_called_once_with("1640995200")
        mock_wei_to_eth.assert_called_once_with("1000000000000000000")
        mock_gas_fee.assert_called_once_with("21000", "20000000000")

    @patch("analyzer.transaction_analyzer.convert_timestamp")
    @patch("analyzer.transaction_analyzer.convert_wei_to_eth")
    @patch("analyzer.transaction_analyzer.calculate_gas_fee")
    def test_process_transaction_erc20_transfer(
        self,
        mock_gas_fee,
        mock_wei_to_eth,
        mock_timestamp,
        analyzer,
        sample_erc20_transaction,
    ):
        """Test processing of ERC-20 transfer transaction."""
        # Mock utility function returns
        mock_timestamp.return_value = "2022-01-01 00:01:00"
        mock_wei_to_eth.return_value = "1000.0"
        mock_gas_fee.return_value = "0.000675"

        result = analyzer._process_transaction(
            sample_erc20_transaction, "ERC-20 Transfer"
        )

        # Verify the result
        assert isinstance(result, TransactionDomainModel)
        assert result.transaction_type == "ERC-20 Transfer"
        assert result.contract_address == sample_erc20_transaction["contractAddress"]
        assert result.asset_symbol == "USDC"  # Should use tokenSymbol for ERC-20
        assert result.asset_name == "USD Coin"
        assert result.is_error is False

    @patch("analyzer.transaction_analyzer.convert_timestamp")
    @patch("analyzer.transaction_analyzer.convert_wei_to_eth")
    @patch("analyzer.transaction_analyzer.calculate_gas_fee")
    def test_process_transaction_with_error(
        self,
        mock_gas_fee,
        mock_wei_to_eth,
        mock_timestamp,
        analyzer,
        sample_eth_transaction,
    ):
        """Test processing of failed transaction."""
        sample_eth_transaction["isError"] = "1"

        mock_timestamp.return_value = "2022-01-01 00:00:00"
        mock_wei_to_eth.return_value = "1.0"
        mock_gas_fee.return_value = "0.00042"

        result = analyzer._process_transaction(sample_eth_transaction, "ETH Transfer")

        assert result.is_error is True

    @patch("analyzer.transaction_analyzer.convert_timestamp")
    @patch("analyzer.transaction_analyzer.convert_wei_to_eth")
    @patch("analyzer.transaction_analyzer.calculate_gas_fee")
    def test_process_transaction_missing_fields(
        self, mock_gas_fee, mock_wei_to_eth, mock_timestamp, analyzer
    ):
        """Test processing transaction with missing fields."""
        incomplete_tx = {"hash": "0x123"}  # Only hash provided

        mock_timestamp.return_value = ""
        mock_wei_to_eth.return_value = "0"
        mock_gas_fee.return_value = "0"

        result = analyzer._process_transaction(incomplete_tx, "ETH Transfer")

        # Should handle missing fields gracefully with defaults
        assert result.transaction_hash == "0x123"
        assert result.from_address == ""
        assert result.to_address == ""
        assert result.gas == "0"
        assert result.gas_price == "0"
        assert result.gas_used == "0"
        assert result.is_error is False  # Default when isError is missing

    def test_analyze_successful(self, analyzer, sample_raw_data):
        """Test successful analysis of transaction data."""
        with patch.object(analyzer, "_process_transaction") as mock_process:
            # Mock _process_transaction to return mock domain models
            mock_tx1 = Mock(spec=TransactionDomainModel)
            mock_tx2 = Mock(spec=TransactionDomainModel)
            mock_process.side_effect = [mock_tx1, mock_tx2]

            result = analyzer.analyze(sample_raw_data)

            # Verify result is TransactionListDomainModel
            assert isinstance(result, TransactionListDomainModel)
            assert len(result.root) == 2

            # Verify _process_transaction was called for each transaction
            assert mock_process.call_count == 2
            mock_process.assert_any_call(sample_raw_data["normal"][0], "ETH Transfer")
            mock_process.assert_any_call(sample_raw_data["erc20"][0], "ERC-20 Transfer")

    def test_analyze_with_processing_errors(
        self, analyzer, sample_raw_data
    ):
        """Test analysis when some transactions fail to process."""
        with patch.object(analyzer, "_process_transaction") as mock_process:
            # First transaction succeeds, second fails
            mock_tx = Mock(spec=TransactionDomainModel)
            mock_process.side_effect = [mock_tx, Exception("Processing error")]

            result = analyzer.analyze(sample_raw_data)

            # Should return only the successful transaction
            assert isinstance(result, TransactionListDomainModel)
            assert len(result.root) == 1
            assert result.root[0] == mock_tx

    def test_analyze_empty_data(self, analyzer):
        """Test analysis with empty transaction data."""
        empty_data = {}

        result = analyzer.analyze(empty_data)

        assert isinstance(result, TransactionListDomainModel)
        assert len(result.root) == 0

    def test_analyze_unknown_transaction_types(self, analyzer):
        """Test analysis with unknown transaction types."""
        unknown_data = {
            "unknown_type": [{"hash": "0x123"}],
            "another_unknown": [{"hash": "0x456"}],
        }

        result = analyzer.analyze(unknown_data)

        # Should ignore unknown transaction types
        assert isinstance(result, TransactionListDomainModel)
        assert len(result.root) == 0


class TestEthereumTransactionAnalyzerIntegration:
    """Integration tests with real utility functions (not mocked)."""

    @pytest.fixture
    def analyzer(self):
        return EthereumTransactionAnalyzer()

    def test_process_transaction_integration(self, analyzer):
        """Integration test with real utility functions."""
        sample_tx = {
            "hash": "0x1234567890abcdef",
            "timeStamp": "1640995200",
            "from": "0xfrom123",
            "to": "0xto456",
            "value": "1000000000000000000",  # 1 ETH
            "gas": "21000",
            "gasPrice": "20000000000",
            "gasUsed": "21000",
            "isError": "0",
        }

        result = analyzer._process_transaction(sample_tx, "ETH Transfer")

        assert result.value_amount_eth == "1"
        assert result.gas_fee_eth == "0.00042"  # 21000 * 20000000000 / 10^18
