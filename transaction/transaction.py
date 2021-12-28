from uuid import UUID, uuid4
import json
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


class CurrencyMismatchError(ValueError):
    pass


@dataclass
class Transaction:
    id_: UUID
    account_id: UUID
    balance: Decimal
    currency: str
    status: str





