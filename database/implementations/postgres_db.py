from typing import List, Optional
from uuid import UUID, uuid4
import psycopg2
import pandas as pd
from pandas import DataFrame, Series
from account.account import Account
from transaction.transaction import Transaction
from database.database import AccountDatabase
from database.database import ObjectNotFound


class AccountDatabasePostgres(AccountDatabase):
    def __init__(self, connection: str,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conn = psycopg2.connect(connection)
        cur = self.conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS accounts_kaisar (
            id varchar primary key ,
            currency varchar ,
            balance decimal 
        );
        
        CREATE TABLE IF NOT EXISTS transactions_kaisar (
            id varchar primary key ,
            account_id varchar ,
            currency varchar ,
            balance decimal ,
            status varchar
        );
        """)
        self.conn.commit()


    def close_connection(self):
        self.conn.close()

    def _save(self, account: Account) -> None:
        if account.id_ is None:
            account.id_ = uuid4()

        cur = self.conn.cursor()
        cur.execute("""
                UPDATE accounts_kaisar SET currency = %s, balance = %s WHERE id = %s;
        """, (account.currency, account.balance, str(account.id_)))
        rows_count = cur.rowcount
        self.conn.commit()

        print("ROWS COUNT", rows_count)
        if rows_count == 0:
            cur = self.conn.cursor()
            cur.execute("""
                    INSERT INTO accounts_kaisar (id, currency, balance) VALUES (%s, %s, %s);
                    """, (str(account.id_), account.currency, account.balance))
            self.conn.commit()

    def clear_all(self) -> None:
        cur = self.conn.cursor()
        cur.execute("DELETE FROM accounts_kaisar;")
        self.conn.commit()

    def max_value(self):
        cur = self.conn.cursor()
        cur.execute("SELECT MAX(balance) FROM accounts_kaisar;")
        data = cur.fetchall()
        return data[0][0]



    def get_objects(self) -> List[Account]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM accounts_kaisar;")
        data = cur.fetchall()
        cols = [x[0] for x in cur.description]
        df = pd.DataFrame(data, columns=cols)
        return [self.pandas_row_to_account(row) for index, row in df.iterrows()]

    def pandas_row_to_account(self, row: Series) -> Account:
        return Account(
            id_=UUID(row["id"]),
            currency=row["currency"],
            balance=row["balance"],
        )

    def get_tran_by_account_id(self, account_id: UUID):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM transactions_kaisar WHERE account_id = %s;", (str(account_id),))
        data = cur.fetchall()
        cols = [x[0] for x in cur.description]
        df = pd.DataFrame(data, columns=cols)
        return [self.pandas_row_to_account(row) for index, row in df.iterrows()]

    def save_trans(self, transaction: Transaction):
        if transaction.id_ is None:
            transaction.id_ = uuid4()

        cur = self.conn.cursor()
        cur.execute("""
                UPDATE transactions_kaisar SET  account_id = %s, balance = %s, currency = %s, status = %s WHERE id = %s;
        """, (str(transaction.account_id), transaction.balance,  transaction.currency, transaction.status, str(transaction.id_)))
        rows_count = cur.rowcount
        self.conn.commit()

        print("ROWS COUNT", rows_count)
        if rows_count == 0:
            cur = self.conn.cursor()
            cur.execute("""
                    INSERT INTO transactions_kaisar (id, account_id, balance, currency, status) VALUES (%s, %s, %s, %s, 
                    %s);
                    """, (str(transaction.id_), str(transaction.account_id), transaction.balance, transaction.currency,
                          transaction.status))
            self.conn.commit()


    def get_object(self, id_: UUID) -> Optional[Account]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM accounts_kaisar WHERE id = %s;", (str(id_),))
        print("Trying to find", str(id_))
        data = cur.fetchall()
        if len(data) == 0:
            raise ObjectNotFound("Postgres: Object not found")
        cols = [x[0] for x in cur.description]


        df = pd.DataFrame(data, columns=cols)
        return self.pandas_row_to_account(row=df.iloc[0])