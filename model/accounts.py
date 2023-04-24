import sqlite3
from os import environ
from Connectors.connection import Connection
from dotenv import load_dotenv
import json

load_dotenv()
ACC_BASE = 1000000
conn = Connection.get(environ.get('DATABASE_PATH'))
db_cursor = conn.cursor()
records = db_cursor.execute("SELECT COUNT(*) FROM Accounts").fetchone()[0]
class Account:

    def __init__(self, name, balance, username, password) -> None:
        global records
        global ACC_BASE
        self.account_holder_name = name
        self.account_number = "{}".format(ACC_BASE + records)
        self.accout_balance = balance
        self.account_username = username
        self.password = password
        self.role = "Customer"
        records = records + 1

def create_account(name, username, password, balance) -> Account:
    new_account = Account(name,balance,username,password)
    db_cursor.execute('INSERT INTO Accounts VALUES(?,?,?,?,?,?)',
                    (
                        new_account.account_number,
                        new_account.account_holder_name,
                        new_account.accout_balance,
                        new_account.account_username,
                        new_account.password,
                        new_account.role
                    ))
    conn.commit()
    return new_account

    
def get_account_details(acc_number) -> dict:
    requested_account = dict()
    result = db_cursor.execute('SELECT * FROM Accounts WHERE account_number = ?',(acc_number,)).fetchone()
    requested_account['Account Holder Name'] = result[1]
    requested_account['Account Number'] = result[0]
    requested_account['Balance'] = result[2]
    requested_account['Username'] = result[3]
    return requested_account

acc = get_account_details(1000001)
print(json.dumps(acc,indent=4))
