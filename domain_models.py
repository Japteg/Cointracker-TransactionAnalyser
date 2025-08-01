from typing import List
from enum import Enum
from pydantic import BaseModel, RootModel


class EthereumTransactionType(Enum):
    NORMAL = "normal"
    INTERNAL = "internal"
    ERC20 = "erc20"
    ERC721 = "erc721"
    ERC1155 = "erc1155"


class TransactionDomainModel(BaseModel):
    transaction_hash: str
    date_time: str
    from_address: str
    to_address: str
    transaction_type: str
    contract_address: str
    asset_symbol: str
    asset_name: str
    token_id: str
    value_amount_eth: str
    gas: str
    gas_price: str
    gas_used: str
    gas_fee_eth: str
    is_error: bool


class TransactionListDomainModel(RootModel):
    root: List[TransactionDomainModel]