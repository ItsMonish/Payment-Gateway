from flask import request
from Accounts.accounts import *


def getAuthToken(in_request: request) -> str:
    auth_header = in_request.headers.get("Authorization", None)
    if not auth_header:
        return "1"
    header_parts = auth_header.split(" ")
    if header_parts[0].lower() != "bearer" and len(header_parts) != 2:
        return "2"
    return header_parts[1]


def validateAccountToken(token: str, acc: dict) -> bool:
    token_un = Account.authenticateToken(token)
    if not token_un:
        return False
    elif token_un == acc["Username"]:
        return True
    elif token_un != acc["Username"] and getRole(acc["Account Number"] == "Admin"):
        return True
    else:
        return False


def isAdminToken(token: str) -> bool:
    token_un = Account.authenticateToken(token)
    if not token_un:
        return False
    elif getRole(token_un) == "Admin":
        return True
    else:
        return False
