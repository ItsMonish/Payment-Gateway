import sqlite3
from typing import Union

class Connection:
    db_connection = None

    @staticmethod
    def get(path: Union[None,str] = None) -> sqlite3.Connection:
        if Connection.db_connection == None:
            Connection.db_connection = sqlite3.connect(path)
        return Connection.db_connection