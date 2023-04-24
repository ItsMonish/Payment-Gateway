from os import environ
from Accounts.connection import Connection
from dotenv import load_dotenv

load_dotenv()
conn = Connection.get(environ.get('DATABASE_PATH'))
db_cursor = conn.cursor()
TXN_BASE = 10000000
records = db_cursor.execute("SELECT COUNT(*) FROM Transactions").fetchone()[0]

class Transaction:

    def __init__(self, origin_acc, dest_acc, amount) -> None:
        global TXN_BASE,records
        self.transactionID = TXN_BASE + records
        self.origin_account = origin_acc
        self.destination_account = dest_acc
        self.amount = amount
        records = records + 1

def startTransaction(orign_acc, dest_acc, amt) -> bool:
    txn_obj = Transaction(orign_acc,dest_acc,amt)
    origin = db_cursor.execute('SELECT * FROM Accounts WHERE account_number = ?',(orign_acc,)).fetchone()
    if origin == None:
        db_cursor.execute('INSERT INTO Transactions VALUES(?,?,?,?,?)',
                          (
                            txn_obj.transactionID,
                            txn_obj.origin_account,
                            txn_obj.destination_account,
                            txn_obj.amount,
                            "Failed - Origin not found"
                          ))
        conn.commit()
        return False
    if (origin[2] - amt) < 500 :
        db_cursor.execute('INSERT INTO Transactions VALUES(?,?,?,?,?)',
                          (
                            txn_obj.transactionID,
                            txn_obj.origin_account,
                            txn_obj.destination_account,
                            txn_obj.amount,
                            "Failed - Insufficient balance"
                          ))
        conn.commit()
        return False
    destination = db_cursor.execute('SELECT * FROM Accounts WHERE account_number = ?',(dest_acc,)).fetchone()
    if destination == None:
        db_cursor.execute('INSERT INTO Transactions VALUES(?,?,?,?,?)',
                          (
                            txn_obj.transactionID,
                            txn_obj.origin_account,
                            txn_obj.destination_account,
                            txn_obj.amount,
                            "Failed - Destination not found"
                          ))
        conn.commit()
        return False
    db_cursor.execute('UPDATE Accounts SET balance = ? WHERE account_number = ?',(origin[2] - amt,orign_acc))
    db_cursor.execute('UPDATE Accounts SET balance = ? WHERE account_number = ?',(destination[2] + amt,dest_acc))
    db_cursor.execute('INSERT INTO Transactions VALUES(?,?,?,?,?)',
                          (
                            txn_obj.transactionID,
                            txn_obj.origin_account,
                            txn_obj.destination_account,
                            txn_obj.amount,
                            "Success"
                          ))
    conn.commit()
    return True