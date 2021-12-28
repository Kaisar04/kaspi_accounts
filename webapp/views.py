import json
from decimal import Decimal
from uuid import uuid4

from django.http import HttpResponse, HttpRequest
import os

from django.shortcuts import render

from account.account import Account
from database.database import ObjectNotFound
from database.implementations.postgres_db import AccountDatabasePostgres
from transaction.transaction import Transaction

dbname: str = "postgres"
port: int = 5432
user: str = "postgres"
print(user)
password: str = "10011000Ks"
host: str = "localhost"
connection_str = f"dbname={dbname} port={port} user={user} password={password} host={host}"
database = AccountDatabasePostgres(connection=connection_str)


def accounts_list(request: HttpRequest) -> HttpResponse:
    max_balance = database.max_value()
    accounts = database.get_objects()
    if request.method == "POST":
            account = Account.fill_spaces(request.body.decode("utf8"))
            database.save(account)
            accounts = database.get_objects()
    return render(request, "index.html", context={"accounts": accounts, "max_balance": max_balance})


def account_detail(request: HttpRequest, pk):
    account = database.get_object(id_=pk)
    transactions = database.get_tran_by_account_id(account_id=account.id_)
    if request.method == "POST":
        balance = Decimal(request.POST.get("balance", 0))
        account = database.get_object(id_=pk)
        account.balance += balance
        database.save(account)
        transaction = Transaction(
            id_=uuid4(),
            account_id=account.id_,
            balance=balance,
            currency=account.currency,
            status="Completed",
        )
        database.save_trans(transaction=transaction)
    transactions = database.get_tran_by_account_id(account_id=account.id_)
    print(transactions)
    return render(request, "account_detail.html", context={"account": account, "transactions": transactions})


def index(request: HttpRequest) -> HttpResponse:
    return HttpResponse(content="""
    <html>
        <body>
           <h1>Hello, World!</h1> 
           <h3>Try to access <a href="/api/accounts/">/api/accounts/</a></h3>
        </body>
    </html>
    """)


def accounts(request: HttpRequest) -> HttpResponse:
    accounts = database.get_objects()

    if request.method == "GET":
        json_obj = [account.to_json() for account in accounts]
        return HttpResponse(content=json.dumps(json_obj))

    if request.method == "POST":
        try:
            account = Account.from_json_str(request.body.decode("utf8"))
            account.id_ = uuid4()
            try:
                database.get_object(account.id_)
                return HttpResponse(content=f"Error: object already exists, use PUT to update", status=400)
            except ObjectNotFound:
                database.save(account)
                return HttpResponse(content=account.to_json_str(), status=201)
        except Exception as e:
            return HttpResponse(content=f"Error: {e}", status=400)

    if request.method == "PUT":
        try:
            account = Account.from_json_str(request.body.decode("utf8"))
            database.get_object(account.id_)
            database.save(account)
            return HttpResponse(content="OK", status=200)
        except Exception as e:
            return HttpResponse(content=f"Error: {e}", status=400)


# def deposit(request: HttpRequest, pk, amount) -> HttpResponse:
#     account = database.get_object(id_=pk)
#     account.balance = account.balance + amount
#     database.save(account)
#     return render(request, "account_detail.html", context={"account": account})