import logging
from typing import List, Dict
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, RootModel, model_validator

logger = logging.getLogger(__name__)


class EthereumTransactionType(Enum):
    NORMAL = "normal"
    INTERNAL = "internal"
    ERC20 = "erc20"
    ERC721 = "erc721"
    ERC1155 = "erc1155"


class TransactionDomainModel(BaseModel):
    transaction_hash: str
    date_time: datetime
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

    @model_validator(mode="before")
    @classmethod
    def validate_request(cls, values: Dict) -> Dict:

        # Validate date time
        date_time_value = values.get("date_time", "")
        try:
            # Try to parse the date to ensure it's valid
            formatted_date_time = datetime.strptime(date_time_value, "%Y-%m-%d %H:%M:%S")
            values["date_time"] = formatted_date_time
        except ValueError:
            logger.warning(
                f"Invalid date format in transaction {values.get('transaction_hash')}: {date_time_value}"
            )
            raise ValueError(f"Invalid date format in transaction {values.get('transaction_hash')}: {date_time_value}")

        # Other validations can also be added here as per requirements

        return values




class TransactionListDomainModel(RootModel):
    root: List[TransactionDomainModel]
