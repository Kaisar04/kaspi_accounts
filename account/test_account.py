from decimal import Decimal
from uuid import uuid4, UUID

import pytest
import json

from account.account import Account, CurrencyMismatchError


class TestAccount:
    def test_account_create(self) -> None:
        account = Account(
            id_=uuid4(),
            currency="KZT",
            balance=Decimal(10),
        )
        assert isinstance(account, Account)
        assert account.balance == 10

        account2 = Account(
            id_=uuid4(),
            currency="KZT",
            balance=Decimal(5),
        )

        assert account2 < account

    def test_errors(self) -> None:
        account = Account(
            id_=uuid4(),
            currency="KZT",
            balance=Decimal(10),
        )

        account2 = Account(
            id_=uuid4(),
            currency="USD",
            balance=Decimal(5),
        )

        with pytest.raises(CurrencyMismatchError):
            assert account2 < account

    def test_json_import_export(self) -> None:
        account_id = uuid4()
        account = Account(
            id_=account_id,
            currency="KZT",
            balance=Decimal(10),
        )

        json_account = account.to_json()
        assert json.loads(json_account) == {
            "id": str(account.id_),
            "currency": account.currency,
            "balance": account.balance,
        }

    def test_account_from_json(self) -> None:
        test_json = '{"id": "4dc2e5e3-671f-4efb-8a07-bbb71147a335", "currency": "KZT", "balance": 10.0}'

        account = Account.from_json(test_json)
        assert isinstance(account, Account)
        assert account.id_ == UUID("4dc2e5e3-671f-4efb-8a07-bbb71147a335")
        assert account.balance == Decimal(10)
        assert account.currency == "KZT"





