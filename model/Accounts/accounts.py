from os import environ
from .connection import Connection
from dotenv import load_dotenv

load_dotenv()
conn = Connection.get(environ.get('DATABASE_PATH'))
db_cursor = conn.cursor()
ACC_BASE = 1000000
records = db_cursor.execute("SELECT COUNT(*) FROM Accounts").fetchone()[0]

class Account:

    def __init__(self, name, balance, username, password) -> None:
        global ACC_BASE,records
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

    
def getAccountByAccNumber(acc_number) -> dict:
    requested_account = dict()
    result = db_cursor.execute('SELECT * FROM Accounts WHERE account_number = ?',(acc_number,)).fetchone()
    if result == None:
        return None
    requested_account['Account Holder Name'] = result[1]
    requested_account['Account Number'] = result[0]
    requested_account['Balance'] = result[2]
    requested_account['Username'] = result[3]
    return requested_account

def getAccountByUsername(username) -> dict:
    requested_account = dict()
    result = db_cursor.execute('SELECT * FROM Accounts WHERE username = ?',(username,)).fetchone()
    if result == None:
        return None
    requested_account['Account Holder Name'] = result[1]
    requested_account['Account Number'] = result[0]
    requested_account['Balance'] = result[2]
    requested_account['Username'] = result[3]
    return requested_account

def creditBalance(acc_number,amount) -> bool:
    target_account = db_cursor.execute('SELECT * FROM Accounts WHERE account_number = ?',(acc_number,)).fetchone()
    if target_account == None:
        return False
    balance = target_account[2]
    db_cursor.execute('UPDATE Accounts SET balance = ? WHERE account_number = ?',(amount+balance,acc_number))
    conn.commit()
    return True

def debitBalance(acc_number,amount) -> bool:
    target_account = db_cursor.execute('SELECT * FROM Accounts WHERE account_number = ?',(acc_number,)).fetchone()
    if target_account == None:
        return False
    balance = target_account[2]
    db_cursor.execute('UPDATE Accounts SET balance = ? WHERE account_number = ?',(balance-amount,acc_number))
    conn.commit()
    return True

def deleteAccount(acc_number) -> bool:
    target_account = db_cursor.execute('SELECT * FROM Accounts WHERE account_number = ?',(acc_number,)).fetchone()
    if target_account == None:
        return False
    db_cursor.execute('DELETE FROM Accounts WHERE account_number = ?',(acc_number,))
    conn.commit()
    return True