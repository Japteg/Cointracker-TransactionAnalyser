# Ethereum Transaction Analyzer

A comprehensive script for fetching, analyzing, and exporting Ethereum wallet transaction history. This tool efficiently handles large datasets by implementing API batching and provides detailed transaction analysis across multiple Ethereum transaction types.

## 🚀 Features

- **Comprehensive Transaction Coverage**: Fetches all Ethereum transaction types
  - Normal ETH transfers
  - Internal transactions
  - ERC-20 token transfers
  - ERC-721 NFT transfers
  - ERC-1155 multi-token transfers
- **API Batching**: Efficiently handles large transaction histories
- **Analysis**: Categorizes and processes transaction data with gas fee calculations
- **CSV Export**: Exports to structured CSV format with detailed transaction information

## 🏗️ Project Architecture

### High-Level Overview

The Ethereum Transaction Analyzer follows a modular, extensible architecture designed for scalability and maintainability:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   main.py       │    │  Configuration   │    │  CLI Interface  │
│  (Entry Point)  │────│     Manager      │────│   & Validation  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │
         ▼
┌────────────────────────────────────────────────────────────────┐
│                    Data Fetching Layer                         │
├─────────────────┐    ┌──────────────────┐    ┌─────────────────┤
│ Etherscan API   │    │   API Batching   │    │  Rate Limiting  │
│    Client       │────│    & Pagination  │────│   & Retries     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │
         ▼
┌────────────────────────────────────────────────────────────────┐
│                    Analysis Layer                              │
├─────────────────┐    ┌──────────────────┐    ┌─────────────────┤
│  Transaction    │    │   Data Models    │    │    Utility      │
│    Analyzer     │────│  & Validation    │────│   Functions     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │
         ▼
┌────────────────────────────────────────────────────────────────┐
│                    Export Layer                                │
├─────────────────┐    ┌──────────────────┐    ┌─────────────────┤
│   CSV Exporter  │    │  Data Formatting │    │  File Management│
│                 │────│   & Validation   │────│   & Storage     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### API Batching Strategy

The system implements sophisticated API batching to efficiently handle large transaction histories:

#### 1. **Multi-Type Fetching**
```python
# Fetches each transaction type in separate API calls
TRANSACTION_TYPES = {
    'normal': 'txlist',           # Regular ETH transfers
    'internal': 'txlistinternal', # Internal transactions
    'erc20': 'tokentx',          # ERC-20 token transfers
    'erc721': 'tokennfttx',      # ERC-721 NFT transfers
    'erc1155': 'token1155tx'     # ERC-1155 multi-tokens
}
```

#### 2. **Progressive Block-Based Pagination**
- **Initial Request**: Starts from block 0 with 10,000 transaction limit
- **Progressive Batching**: Uses the last transaction's block number + 1 as the starting point for the next batch

#### 3. **Batch Processing Flow**
```
Batch 1: Block 0 → Block N (10,000 transactions)
Batch 2: Block N+1 → Block M (10,000 transactions)
Batch 3: Block M+1 → Block X (< 10,000 transactions) → STOP
```


## 📋 Prerequisites

- **Python**: 3.10
- **Etherscan API Key**: Free API key from [Etherscan.io](https://etherscan.io/apis)
- **Operating System**: Windows, macOS, or Linux

### Step 1: Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Environment Configuration
Create a `.env` file in the project root:
```bash
# Create .env file
touch .env
```

Add your Etherscan API key to `.env`:
```env
# Etherscan API Configuration
ETHERSCAN_API_KEY=your_etherscan_api_key_here
```

### Step 5: Verify Installation
```bash
python main.py --help
```

You should see the help message with available options.

## 🚀 Usage

### Basic Usage
```bash
python main.py --address 0x742d35Cc6634C0532925a3b8D698Ac2160c85609
```

### Command Options
```bash
python main.py --address <ETHEREUM_ADDRESS>
```

**Arguments:**
- `--address`: Ethereum wallet address to analyze (required, must include 0x prefix)

### Sample Output
```
INFO - Starting transaction analysis for address: 0x742d35Cc6634C0532925a3b8D698Ac2160c85609
INFO - Initializing Etherscan API client...

---- Transaction type: NORMAL, Fetching batch 1 of transactions for 0x742d35Cc6634C0532925a3b8D698Ac2160c85609 ----
---- Completed fetching transactions of type: NORMAL, Fetched 150 transactions ----

---- Transaction type: ERC20, Fetching batch 1 of transactions for 0x742d35Cc6634C0532925a3b8D698Ac2160c85609 ----
---- Completed fetching transactions of type: ERC20, Fetched 75 transactions ----

Starting transaction analysis...
Processing 150 normal transactions
Processing 75 erc20 transactions
Successfully processed 225 total transactions

--------------------------------
Export summary for 0x742d35Cc6634C0532925a3b8D698Ac2160c85609:
- Total transactions: 225 (from 2020-01-15 10:30:45 to 2024-01-10 16:22:10)
- Transaction types: {'ETH Transfer': 150, 'ERC-20 Transfer': 75}
- Total gas fees: 0.045230 ETH
--------------------------------

Transactions exported to: ./transaction_reports/eth_transactions_0x742d...85609_20240110_162230.csv
```

## 📁 Project Structure

```
ethereum-transaction-analyzer/
├── main.py                              # Application entry point
├── config.py                            # Configuration management
├── requirements.txt                     # Python dependencies
├── .env                                 # Environment variables (create this)
├── .gitignore                          # Git ignore rules
├── README.md                           # This documentation
│
├── analyzer/                           # Transaction analysis module
│   ├── __init__.py
│   ├── base_transaction_analyzer.py    # Abstract base class
│   └── transaction_analyzer.py         # Ethereum transaction analyzer
│
├── data_exporter/                      # Data export module
│   ├── __init__.py
│   ├── data_exporter_base.py          # Abstract base exporter
│   └── csv_exporter.py                # CSV export implementation
│
├── external_data_providers/            # External API clients
│   ├── __init__.py
│   ├── external_data_provider_base_client.py  # Base API client
│   └── etherscan_api_client.py         # Etherscan API implementation
│
├── tests/                              # Test suite
│   ├── __init__.py
│   ├── test_utils.py                   # Utility function tests
│   └── analyzer/
│       ├── __init__.py
│       └── test_transaction_analyzer.py # Analyzer tests
│
├── transaction_reports/                # Generated CSV files
│   └── (CSV files generated here)
│
├── domain_models.py                    # Data models and types
├── utils.py                           # Utility functions
├── constants.py                       # Application constants
├── api_client.py                      # HTTP client wrapper
```

## 🧪 Testing

The project includes a comprehensive test suite with both unit and integration tests.

### Running All Tests
```bash
pytest ./tests
```

## 📊 Output Format


### File Naming Convention
```
eth_transactions_<short_address>_<timestamp>.csv
```
Example: `eth_transactions_0x742d...5609_20240115_143022.csv`

## ⚙️ Configuration

### Environment Variables
The application supports the following environment variables:

| Variable | Description | Required | Default |
|----------|-------------|--------|---------|
| `ETHERSCAN_API_KEY` | Your Etherscan API key | Yes | None |

---