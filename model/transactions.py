from os import environ
from .Accounts.connection import Connection
from dotenv import load_dotenv

load_dotenv()
conn = Connection.get(environ.get("DATABASE_PATH"))
db_cursor = conn.cursor()
TXN_BASE = 10000000
records = db_cursor.execute("SELECT COUNT(*) FROM Transactions").fetchone()[0]


class Transaction:
    def __init__(self, origin_acc, dest_acc, amount) -> None:
        global TXN_BASE, records
        self.transactionID = TXN_BASE + records
        self.origin_account = origin_acc
        self.destination_account = dest_acc
        self.amount = amount
        records = records + 1

    def startTransaction(self) -> int:
        origin = db_cursor.execute(
            "SELECT * FROM Accounts WHERE account_number = ?", (self.origin_account,)
        ).fetchone()
        if origin == None:
            db_cursor.execute(
                "INSERT INTO Transactions VALUES(?,?,?,?,?)",
                (
                    self.transactionID,
                    self.origin_account,
                    self.destination_account,
                    self.amount,
                    "Failed - Origin not found",
                ),
            )
            conn.commit()
            return 1
        if (origin[2] - self.amount) < 500:
            db_cursor.execute(
                "INSERT INTO Transactions VALUES(?,?,?,?,?)",
                (
                    self.transactionID,
                    self.origin_account,
                    self.destination_account,
                    self.amount,
                    "Failed - Insufficient balance",
                ),
            )
            conn.commit()
            return 2
        destination = db_cursor.execute(
            "SELECT * FROM Accounts WHERE account_number = ?",
            (self.destination_account,),
        ).fetchone()
        if destination == None:
            db_cursor.execute(
                "INSERT INTO Transactions VALUES(?,?,?,?,?)",
                (
                    self.transactionID,
                    self.origin_account,
                    self.destination_account,
                    self.amount,
                    "Failed - Destination not found",
                ),
            )
            conn.commit()
            return 3
        db_cursor.execute(
            "UPDATE Accounts SET balance = ? WHERE account_number = ?",
            (origin[2] - self.amount, self.origin_account),
        )
        db_cursor.execute(
            "UPDATE Accounts SET balance = ? WHERE account_number = ?",
            (destination[2] + self.amount, self.destination_account),
        )
        db_cursor.execute(
            "INSERT INTO Transactions VALUES(?,?,?,?,?)",
            (
                self.transactionID,
                self.origin_account,
                self.destination_account,
                self.amount,
                "Success",
            ),
        )
        conn.commit()
        return 0


def returnTransaction(txn_id) -> dict:
    result = db_cursor.execute(
        "SELECT * FROM Transactions WHERE transaction_id = ?", (txn_id,)
    ).fetchone()
    if result == None:
        return None
    txn = dict()
    txn["Transaction_ID"] = txn_id
    txn["Origin"] = result[1]
    txn["Destination"] = result[2]
    txn["Amount"] = result[3]
    txn["Status"] = result[4]
    return txn
