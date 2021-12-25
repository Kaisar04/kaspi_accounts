from decimal import Decimal
from uuid import uuid4
import pytest

from account.account import Account
from customer.customer import Customer
import mypy


class TestCustomer:
    def test_two_plus_two(self) -> None:
        assert 2 + 2 == 4

    def test_customer_create(self):
        customer_id = uuid4()
        customer = Customer(
            id_=customer_id,
            first_name="Kaisar",
            last_name="Sarymsakov",
            age=23,
            accounts=[],
        )

        customer2 = Customer(
            id_=customer_id,
            first_name="Kaisar",
            last_name="Sarymsakov",
            age=23,
            accounts=[],
        )

        assert customer.id_ == customer_id
        assert customer.first_name == "Kaisar"
        assert customer.last_name == "Sarymsakov"

        assert isinstance(customer, Customer)

        assert customer == customer2
        assert id(customer) != id(customer2)

        assert customer < customer2

    def test_customer_create_with_accounts(self) -> None:
        account1_id = uuid4()
        account2_id = uuid4()
        account1 = Account(
            id_=account1_id,
            currency="KZT",
            balance=Decimal(1000),
        )
        account2 = Account(
            id_=account2_id,
            currency="KZT",
            balance=Decimal(500),
        )


