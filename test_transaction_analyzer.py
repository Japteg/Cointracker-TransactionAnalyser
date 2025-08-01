#!/usr/bin/env python3
"""
Test Suite for Ethereum Transaction Analyzer
===========================================

Comprehensive tests covering critical functionality and edge cases.
"""

import pytest
import pandas as pd
import json
import tempfile
import os
from unittest.mock import Mock, patch, mock_open
from pathlib import Path
import responses

# Import the modules to test
from external_data_providers.etherscan_api_client import EtherscanApiClient
from transaction_analyzer import TransactionAnalyzer
from csv_exporter import CSVExporter
from config import Config


class TestEtherscanApiClient:
    """Test cases for Etherscan API client."""
    
    @pytest.fixture
    def client(self):
        return EtherscanApiClient("test_api_key")
    
    @pytest.fixture
    def sample_normal_transaction(self):
        return {
            'hash': '0x123abc',
            'timeStamp': '1640995200',  # 2022-01-01 00:00:00
            'from': '0xfrom123',
            'to': '0xto456',
            'value': '1000000000000000000',  # 1 ETH in Wei
            'gasUsed': '21000',
            'gasPrice': '20000000000',  # 20 Gwei
            'isError': '0',
            'blockNumber': '13916166',
            'transactionIndex': '5'
        }
    
    @responses.activate
    def test_get_normal_transactions_success(self, client, sample_normal_transaction):
        """Test successful fetching of normal transactions."""
        responses.add(
            responses.GET,
            'https://api.etherscan.io/api',
            json={'status': '1', 'result': [sample_normal_transaction]},
            status=200
        )
        
        result = client.get_normal_transactions('0xtest123')
        
        assert len(result) == 1
        assert result[0]['hash'] == '0x123abc'
        assert result[0]['value'] == '1000000000000000000'
    
    @responses.activate
    def test_api_error_handling(self, client):
        """Test API error handling."""
        responses.add(
            responses.GET,
            'https://api.etherscan.io/api',
            json={'status': '0', 'message': 'Invalid API Key'},
            status=200
        )
        
        with pytest.raises(Exception, match="API Error: Invalid API Key"):
            client.get_normal_transactions('0xtest123')
    
    @responses.activate
    def test_rate_limit_handling(self, client):
        """Test rate limit handling with retry."""
        # First call hits rate limit
        responses.add(
            responses.GET,
            'https://api.etherscan.io/api',
            json={'status': '0', 'message': 'Max rate limit reached'},
            status=200
        )
        # Second call succeeds
        responses.add(
            responses.GET,
            'https://api.etherscan.io/api',
            json={'status': '1', 'result': []},
            status=200
        )
        
        result = client.get_normal_transactions('0xtest123')
        assert result == []
    
    @responses.activate
    def test_no_transactions_found(self, client):
        """Test handling when no transactions are found."""
        responses.add(
            responses.GET,
            'https://api.etherscan.io/api',
            json={'status': '0', 'message': 'No transactions found'},
            status=200
        )
        
        result = client.get_normal_transactions('0xtest123')
        assert result == []
    
    def test_invalid_api_key(self):
        """Test that invalid API key is handled."""
        with pytest.raises(Exception):
            client = EtherscanApiClient("")
            # This would fail when making actual API calls


class TestTransactionAnalyzer:
    """Test cases for transaction analyzer."""
    
    @pytest.fixture
    def analyzer(self):
        return TransactionAnalyzer()
    
    @pytest.fixture
    def sample_raw_data(self):
        return {
            'normal': [{
                'hash': '0x123abc',
                'timeStamp': '1640995200',
                'from': '0xfrom123',
                'to': '0xto456',
                'value': '1000000000000000000',
                'gasUsed': '21000',
                'gasPrice': '20000000000',
                'isError': '0',
                'blockNumber': '13916166'
            }],
            'internal': [],
            'erc20': [{
                'hash': '0x456def',
                'timeStamp': '1640995300',
                'from': '0xfrom789',
                'to': '0xto012',
                'value': '100000000',  # 100 tokens with 6 decimals
                'contractAddress': '0xusdc',
                'tokenSymbol': 'USDC',
                'tokenName': 'USD Coin',
                'tokenDecimal': '6',
                'gasUsed': '65000',
                'gasPrice': '15000000000'
            }],
            'erc721': [],
            'erc1155': []
        }
    
    def test_wei_to_eth_conversion(self, analyzer):
        """Test Wei to ETH conversion accuracy."""
        # 1 ETH = 10^18 Wei
        assert analyzer._convert_wei_to_eth('1000000000000000000') == '1'
        assert analyzer._convert_wei_to_eth('500000000000000000') == '0.5'
        assert analyzer._convert_wei_to_eth('1') == '0.000000000000000001'
        assert analyzer._convert_wei_to_eth('0') == '0'
        assert analyzer._convert_wei_to_eth('') == '0'
    
    def test_timestamp_conversion(self, analyzer):
        """Test Unix timestamp to datetime conversion."""
        # 2022-01-01 00:00:00 UTC
        result = analyzer._convert_timestamp('1640995200')
        assert '2022-01-01' in result
        
        # Invalid timestamp
        assert analyzer._convert_timestamp('invalid') == ''
        assert analyzer._convert_timestamp('') == ''
    
    def test_gas_fee_calculation(self, analyzer):
        """Test gas fee calculation."""
        # 21000 gas * 20 Gwei = 0.00042 ETH
        gas_fee = analyzer._calculate_gas_fee('21000', '20000000000')
        assert gas_fee == '0.00042'
        
        # Edge cases
        assert analyzer._calculate_gas_fee('0', '20000000000') == '0'
        assert analyzer._calculate_gas_fee('21000', '0') == '0'
        assert analyzer._calculate_gas_fee('', '') == '0'
    
    def test_process_normal_transaction(self, analyzer):
        """Test processing of normal transactions."""
        tx = {
            'hash': '0x123abc',
            'timeStamp': '1640995200',
            'from': '0xfrom123',
            'to': '0xto456',
            'value': '1000000000000000000',
            'gasUsed': '21000',
            'gasPrice': '20000000000',
            'isError': '0',
            'blockNumber': '13916166'
        }
        
        result = analyzer._process_normal_transaction(tx)
        
        assert result['transaction_hash'] == '0x123abc'
        assert result['transaction_type'] == 'ETH Transfer'
        assert result['asset_symbol_name'] == 'ETH'
        assert result['value_amount'] == '1'
        assert result['gas_fee_eth'] == '0.00042'
        assert result['is_error'] == False
    
    def test_process_erc20_transfer(self, analyzer):
        """Test processing of ERC-20 token transfers."""
        tx = {
            'hash': '0x456def',
            'timeStamp': '1640995300',
            'from': '0xfrom789',
            'to': '0xto012',
            'value': '100000000',  # 100 tokens with 6 decimals
            'contractAddress': '0xusdc',
            'tokenSymbol': 'USDC',
            'tokenName': 'USD Coin',
            'tokenDecimal': '6',
            'gasUsed': '65000',
            'gasPrice': '15000000000'
        }
        
        result = analyzer._process_erc20_transfer(tx)
        
        assert result['transaction_hash'] == '0x456def'
        assert result['transaction_type'] == 'ERC-20 Transfer'
        assert result['asset_symbol_name'] == 'USDC'
        assert result['asset_contract_address'] == '0xusdc'
        assert result['value_amount'] == '100'  # 100000000 / 10^6
        assert result['token_name'] == 'USD Coin'
    
    def test_analyze_transactions(self, analyzer, sample_raw_data):
        """Test comprehensive transaction analysis."""
        result = analyzer.analyze_transactions(sample_raw_data)
        
        assert len(result) == 2  # 1 normal + 1 ERC-20
        
        # Check normal transaction
        normal_tx = next(tx for tx in result if tx['transaction_type'] == 'ETH Transfer')
        assert normal_tx['value_amount'] == '1'
        
        # Check ERC-20 transaction
        erc20_tx = next(tx for tx in result if tx['transaction_type'] == 'ERC-20 Transfer')
        assert erc20_tx['asset_symbol_name'] == 'USDC'
    
    def test_get_transaction_summary(self, analyzer, sample_raw_data):
        """Test transaction summary generation."""
        analyzer.analyze_transactions(sample_raw_data)
        summary = analyzer.get_transaction_summary()
        
        assert summary['total_transactions'] == 2
        assert 'ETH Transfer' in summary['transaction_type_counts']
        assert 'ERC-20 Transfer' in summary['transaction_type_counts']
        assert 'total_gas_fees_eth' in summary
    
    def test_empty_data_handling(self, analyzer):
        """Test handling of empty transaction data."""
        result = analyzer.analyze_transactions({})
        assert result == []
        
        summary = analyzer.get_transaction_summary()
        assert summary == {}


class TestCSVExporter:
    """Test cases for CSV exporter."""
    
    @pytest.fixture
    def exporter(self):
        return CSVExporter()
    
    @pytest.fixture
    def extended_exporter(self):
        return CSVExporter(include_extended_columns=True)
    
    @pytest.fixture
    def sample_transactions(self):
        return [
            {
                'transaction_hash': '0x123abc',
                'date_time': '2022-01-01 00:00:00',
                'from_address': '0xfrom123',
                'to_address': '0xto456',
                'transaction_type': 'ETH Transfer',
                'asset_contract_address': '',
                'asset_symbol_name': 'ETH',
                'token_id': '',
                'value_amount': '1.0',
                'gas_fee_eth': '0.00042',
                'block_number': '13916166',
                'is_error': False
            },
            {
                'transaction_hash': '0x456def',
                'date_time': '2022-01-01 01:00:00',
                'from_address': '0xfrom789',
                'to_address': '0xto012',
                'transaction_type': 'ERC-20 Transfer',
                'asset_contract_address': '0xusdc',
                'asset_symbol_name': 'USDC',
                'token_id': '',
                'value_amount': '100.0',
                'gas_fee_eth': '0.00098',
                'block_number': '13916167',
                'is_error': False
            }
        ]
    
    def test_validate_data(self, exporter, sample_transactions):
        """Test data validation before export."""
        validated = exporter._validate_data(sample_transactions)
        
        assert len(validated) == 2
        assert all('transaction_hash' in tx for tx in validated)
        assert all(tx['transaction_hash'].startswith('0x') for tx in validated)
    
    def test_sanitize_filename(self, exporter):
        """Test filename sanitization."""
        assert exporter._sanitize_filename('test<>file') == 'test__file'
        assert exporter._sanitize_filename('test|file*') == 'test_file_'
        assert exporter._sanitize_filename('___test___') == 'test'
    
    def test_generate_filename(self, exporter):
        """Test filename generation."""
        filename = exporter._generate_filename('0x123abc456def')
        assert filename.endswith('.csv')
        assert '0x123a...6def' in filename
        
        custom_filename = exporter._generate_filename('0x123', 'my_custom_name')
        assert custom_filename == 'my_custom_name.csv'
    
    def test_export_to_csv(self, exporter, sample_transactions):
        """Test CSV export functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = exporter.export_to_csv(
                sample_transactions,
                temp_dir,
                '0x123abc456def'
            )
            
            assert os.path.exists(csv_path)
            assert csv_path.endswith('.csv')
            
            # Read and verify CSV content
            df = pd.read_csv(csv_path)
            assert len(df) == 2
            assert 'transaction_hash' in df.columns
            assert df.iloc[0]['asset_symbol_name'] in ['ETH', 'USDC']
    
    def test_export_with_extended_columns(self, extended_exporter, sample_transactions):
        """Test CSV export with extended columns."""
        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = extended_exporter.export_to_csv(
                sample_transactions,
                temp_dir,
                '0x123abc456def'
            )
            
            df = pd.read_csv(csv_path)
            assert 'block_number' in df.columns
            assert 'is_error' in df.columns
    
    def test_export_empty_data(self, exporter):
        """Test handling of empty data export."""
        with pytest.raises(ValueError, match="No transactions provided"):
            exporter.export_to_csv([], '/tmp', '0x123')
    
    def test_export_summary_report(self, exporter, sample_transactions):
        """Test summary report generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            summary_path = exporter.export_summary_report(
                sample_transactions,
                temp_dir,
                '0x123abc456def'
            )
            
            assert os.path.exists(summary_path)
            assert summary_path.endswith('.txt')
            
            # Read and verify summary content
            with open(summary_path, 'r') as f:
                content = f.read()
                assert 'Transaction Analysis Summary' in content
                assert '0x123abc456def' in content


class TestConfig:
    """Test cases for configuration management."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = Config()
        
        assert config.get('etherscan.rate_limit_delay') == 0.2
        assert config.get('export.max_transactions_per_type') == 10000
        assert config.get('logging.level') == 'INFO'
    
    def test_config_file_loading(self):
        """Test loading configuration from file."""
        sample_config = {
            'etherscan': {
                'api_key': 'test_key_123',
                'rate_limit_delay': 0.5
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_config, f)
            config_file = f.name
        
        try:
            config = Config(config_file)
            assert config.get('etherscan.api_key') == 'test_key_123'
            assert config.get('etherscan.rate_limit_delay') == 0.5
        finally:
            os.unlink(config_file)
    
    def test_environment_variable_override(self):
        """Test environment variable configuration override."""
        with patch.dict(os.environ, {'ETHERSCAN_API_KEY': 'env_test_key'}):
            config = Config()
            assert config.get('etherscan.api_key') == 'env_test_key'
    
    def test_config_validation(self):
        """Test configuration validation."""
        # Valid config
        config = Config()
        config.set('etherscan.api_key', 'valid_api_key')
        assert config.validate_config() == True
        
        # Invalid config
        config.set('etherscan.api_key', '')
        assert config.validate_config() == False
    
    def test_dot_notation_access(self):
        """Test dot notation configuration access."""
        config = Config()
        
        # Get with dot notation
        assert config.get('etherscan.rate_limit_delay') == 0.2
        assert config.get('nonexistent.key', 'default') == 'default'
        
        # Set with dot notation
        config.set('test.nested.value', 'test_value')
        assert config.get('test.nested.value') == 'test_value'


# Integration Tests
class TestIntegration:
    """Integration tests for the complete system."""
    
    @responses.activate
    def test_end_to_end_flow(self):
        """Test complete end-to-end transaction analysis flow."""
        # Mock API responses
        responses.add(
            responses.GET,
            'https://api.etherscan.io/api',
            json={'status': '1', 'result': [{
                'hash': '0x123abc',
                'timeStamp': '1640995200',
                'from': '0xfrom123',
                'to': '0xto456',
                'value': '1000000000000000000',
                'gasUsed': '21000',
                'gasPrice': '20000000000',
                'isError': '0',
                'blockNumber': '13916166'
            }]},
            status=200
        )
        
        # Set up components
        client = EtherscanApiClient('test_api_key')
        analyzer = TransactionAnalyzer()
        exporter = CSVExporter()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Fetch data
            raw_data = client.get_all_transactions('0xtest123', max_transactions=1000)
            
            # Analyze transactions
            processed_transactions = analyzer.analyze_transactions(raw_data)
            assert len(processed_transactions) >= 1
            
            # Export to CSV
            csv_path = exporter.export_to_csv(
                processed_transactions,
                temp_dir,
                '0xtest123'
            )
            
            # Verify output
            assert os.path.exists(csv_path)
            df = pd.read_csv(csv_path)
            assert len(df) >= 1
            assert df.iloc[0]['transaction_type'] == 'ETH Transfer'


# Performance and Edge Case Tests
class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_large_numbers(self):
        """Test handling of very large numbers."""
        analyzer = TransactionAnalyzer()
        
        # Very large Wei amount
        large_wei = '1000000000000000000000000'  # 1 million ETH
        result = analyzer._convert_wei_to_eth(large_wei)
        assert result == '1000000'
    
    def test_malformed_data(self):
        """Test handling of malformed transaction data."""
        analyzer = TransactionAnalyzer()
        
        malformed_tx = {
            'hash': 'invalid_hash',
            'timeStamp': 'invalid_timestamp',
            'value': 'not_a_number'
        }
        
        # Should not crash, should handle gracefully
        result = analyzer._process_normal_transaction(malformed_tx)
        assert result['transaction_hash'] == 'invalid_hash'
        assert result['value_amount'] == '0'  # Default for invalid number
    
    def test_network_timeout_simulation(self):
        """Test network timeout handling."""
        with patch('requests.Session.get') as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout()
            
            client = EtherscanApiClient('test_api_key')
            with pytest.raises(Exception):
                client.get_normal_transactions('0xtest123')


if __name__ == '__main__':
    # Run the tests
    pytest.main([__file__, '-v', '--cov=.', '--cov-report=html']) 