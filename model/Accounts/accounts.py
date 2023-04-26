from os import environ
from .connection import Connection
from dotenv import load_dotenv
import jwt
import time
from hashlib import sha256

load_dotenv()
conn = Connection.get(environ.get("DATABASE_PATH"))
db_cursor = conn.cursor()
ACC_BASE = 1000000
records = db_cursor.execute("SELECT COUNT(*) FROM Accounts").fetchone()[0]
secret_key = "7bc8c3ff2c8a90d85cd651071ee01616a2db7bc3d7fdbeeb85c2eecf870588ad"


class Account:
    def __init__(
        self, name, balance, username, password, acc_num=None, in_role="Customer"
    ) -> None:
        global ACC_BASE, records
        self.account_holder_name = name
        if acc_num == None:
            self.account_number = "{}".format(ACC_BASE + records + 1)
            self.password = sha256(password.encode()).hexdigest()
            self.role = in_role
            records = records + 1
        else:
            self.account_number = acc_num
            self.password = password
        self.accout_balance = balance
        self.account_username = username

    def generateAuthToken(self, expires_in=600) -> str:
        return jwt.encode(
            {
                "userid": self.account_username,
                "exp": time.time() + expires_in,
            },
            secret_key,
            algorithm="HS256",
        )

    @staticmethod
    def validateUser(username, password) -> str:
        result = db_cursor.execute(
            "SELECT * FROM Accounts WHERE username = ?", (username,)
        ).fetchone()
        if result == None:
            return None
        thisuser = Account(result[1], result[2], result[3], result[4], result[0])
        thisuser.role = result[5]
        claimpass = sha256(password.encode()).hexdigest()
        if claimpass == thisuser.password:
            return thisuser.generateAuthToken()
        else:
            return None

    @staticmethod
    def authenticateToken(token) -> str:
        try:
            data = jwt.decode(token, secret_key, algorithms=["HS256"])
        except:
            return None
        return data["userid"]


def getRole(acc_num) -> str:
    result = db_cursor.execute(
        "SELECT * FROM Accounts WHERE username = ?", (acc_num,)
    ).fetchone()
    return result[5]


def create_account(name, username, password, balance) -> dict:
    new_account = Account(name, balance, username, password)
    result = db_cursor.execute(
        "SELECT * FROM Accounts WHERE username = ?", (username,)
    ).fetchone()
    if result != None:
        return None
    db_cursor.execute(
        "INSERT INTO Accounts VALUES(?,?,?,?,?,?)",
        (
            new_account.account_number,
            new_account.account_holder_name,
            new_account.accout_balance,
            new_account.account_username,
            new_account.password,
            new_account.role,
        ),
    )
    conn.commit()
    return new_account.__dict__


def getAccountByAccNumber(acc_number) -> dict:
    requested_account = dict()
    result = db_cursor.execute(
        "SELECT * FROM Accounts WHERE account_number = ?", (acc_number,)
    ).fetchone()
    if result == None:
        return None
    requested_account["Account Holder Name"] = result[1]
    requested_account["Account Number"] = result[0]
    requested_account["Balance"] = result[2]
    requested_account["Username"] = result[3]
    return requested_account


def getAccountByUsername(username) -> dict:
    requested_account = dict()
    result = db_cursor.execute(
        "SELECT * FROM Accounts WHERE username = ?", (username,)
    ).fetchone()
    if result == None:
        return None
    requested_account["Account Holder Name"] = result[1]
    requested_account["Account Number"] = result[0]
    requested_account["Balance"] = result[2]
    requested_account["Username"] = result[3]
    return requested_account


def creditBalance(acc_number, amount) -> bool:
    target_account = db_cursor.execute(
        "SELECT * FROM Accounts WHERE account_number = ?", (acc_number,)
    ).fetchone()
    if target_account == None:
        return False
    balance = target_account[2]
    db_cursor.execute(
        "UPDATE Accounts SET balance = ? WHERE account_number = ?",
        (amount + balance, acc_number),
    )
    conn.commit()
    return True


def debitBalance(acc_number, amount) -> bool:
    target_account = db_cursor.execute(
        "SELECT * FROM Accounts WHERE account_number = ?", (acc_number,)
    ).fetchone()
    if target_account == None:
        return False
    balance = target_account[2]
    db_cursor.execute(
        "UPDATE Accounts SET balance = ? WHERE account_number = ?",
        (balance - amount, acc_number),
    )
    conn.commit()
    return True


def deleteAccount(in_detail) -> bool:
    target_account = db_cursor.execute(
        "SELECT * FROM Accounts WHERE account_number = ?", (in_detail,)
    ).fetchone()
    if target_account == None:
        target_account = db_cursor.execute(
            "SELECT * FROM Accounts WHERE username = ?", (in_detail,)
        ).fetchone()
        if target_account == None:
            return False
        db_cursor.execute("DELETE FROM Accounts WHERE username = ?", (in_detail,))
        conn.commit()
        return True
    db_cursor.execute("DELETE FROM Accounts WHERE account_number = ?", (in_detail,))
    conn.commit()
    return True


def fetchTransactions(in_var) -> dict:
    acc = getAccountByAccNumber(in_var)
    if acc == None:
        acc = getAccountByUsername(in_var)
        if acc == None:
            return None
        acc_num = acc["Account Number"]
    else:
        acc_num = in_var
    results = db_cursor.execute(
        """SELECT * FROM Transactions WHERE origin_acc = ? 
            UNION 
            SELECT * FROM Transactions WHERE destination_acc = ?""",
        (acc_num, acc_num),
    ).fetchall()
    counter = 1
    req_txn = dict()
    for txn in results:
        req_txn["transaction{}".format(counter)] = dict(
            {
                "TransactionID": txn[0],
                "Origin": txn[1],
                "Destination": txn[2],
                "Amount": txn[3],
                "Status": txn[4],
            }
        )
        counter = counter + 1
    return req_txn
