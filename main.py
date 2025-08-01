#!/usr/bin/env python3
"""
Ethereum Transaction Analyzer
============================

A comprehensive tool for fetching, analyzing, and exporting Ethereum wallet transaction history.

Features:
- Fetches all transaction types (Normal, Internal, ERC-20, ERC-721, ERC-1155)
- Categorizes and processes transaction data
- Exports to CSV with all required fields
- Comprehensive error handling and logging
- Rate limiting and API management
- Extensible architecture
"""

import argparse
import sys
import logging
from pathlib import Path
import re

from analyzer.transaction_analyzer import EthereumTransactionAnalyzer
from data_exporter.csv_exporter import CSVExporter

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import get_config
from external_data_providers.etherscan_api_client import EtherscanApiClient

logger = logging.getLogger(__name__)


def validate_ethereum_address(address: str) -> bool:
    """Validate Ethereum address format."""
    if not address:
        return False

    # Check if it starts with 0x prefix
    if not (address.startswith("0x") or address.startswith("0X")):
        return False

    # Remove 0x prefix for validation
    hex_part = address[2:]

    # Check if it's 40 characters long and contains only hex characters
    return len(hex_part) == 40 and bool(re.match(r"^[0-9a-fA-F]+$", hex_part))


def main():
    """Main entry point for the transaction analyzer."""

    # Set up command line argument parser
    parser = argparse.ArgumentParser(
        description="Ethereum Transaction Analyzer - Fetch, analyze, and export wallet transaction history"
    )
    parser.add_argument(
        "--address",
        required=True,
        help="Ethereum wallet address to analyze (must include 0x prefix)",
    )

    # Parse command line arguments
    args = parser.parse_args()

    # Validate the address
    if not validate_ethereum_address(args.address):
        print(f"Error: Invalid Ethereum address '{args.address}'")
        print("Please provide a valid 42-character hexadecimal address with 0x prefix")
        return 1

    try:
        config = get_config()
        config.setup_logging()

        logger.info(f"Starting transaction analysis for address: {args.address}")

        logger.info("Initializing Etherscan API client...")
        etherscan_client = EtherscanApiClient(config.config["etherscan"]["api_key"])

        raw_data = etherscan_client.get_all_transactions(address=args.address)

        logger.info("Initializing transaction analyzer...")
        analyzer = EthereumTransactionAnalyzer()
        processed_transactions = analyzer.analyze(raw_data)

        logger.info("Initializing CSV exporter...")
        exporter = CSVExporter()
        export_path = exporter.export(processed_transactions.model_dump(), args.address)

        print(f"\nTransactions exported to: {export_path}")
        logger.info("Transaction analysis completed successfully")
        return 0

    except Exception as e:
        logger.error(f"Error during transaction analysis: {str(e)}")
        print(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
