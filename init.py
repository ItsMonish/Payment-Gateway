from flask import Flask, render_template, jsonify, request, Response, redirect, url_for
from model.Accounts.accounts import *
from model.transactions import *
from model.authenticator import *
import json

service = Flask(__name__)


@service.route("/")
def redirect_to_doc():
    return redirect(url_for("display_doc"))


@service.route("/help")
def display_doc():
    return render_template("index.html")


@service.route("/login", methods=["POST"])
def loginService():
    creds = json.loads(request.data)
    try:
        user_name = creds["username"]
        passwd = creds["password"]
    except KeyError:
        return "NO_CREDENTIALS_FOUND", 400
    token = Account.validateUser(user_name, passwd)
    if token == None:
        return "INVALID_CREDENTIALS", 400
    return jsonify({"token": token}), 200


@service.route("/account/<in_var>", methods=["GET"])
def getaccounts(in_var) -> Response:
    token = getAuthToken(request)
    if token == "1":
        return "NO_AUTH_HEADER", 401
    elif token == "2":
        return "BAD_AUTH_HEADER", 400
    else:
        pass
    req_account = getAccountByAccNumber(str(in_var))
    if req_account == None:
        req_account = getAccountByUsername(str(in_var))
        if req_account == None:
            return "ACCOUNT_NOT_FOUND", 404
    if not validateAccountToken(token, req_account):
        return "UNAUTHORIZED_ACCESS", 401
    txns = fetchTransactions(req_account["Account Number"])
    return jsonify(req_account, {"transactions": txns})


@service.route("/account", methods=["PUT"])
def addAccount() -> Response:
    new_acc = json.loads(request.data)
    token = getAuthToken(request)
    if token == "1":
        return "NO_AUTH_HEADER", 401
    elif token == "2":
        return "BAD_AUTH_HEADER", 400
    else:
        pass
    if not isAdminToken(token):
        return "ADMIN_ACTION_ONLY", 403
    created_acc = create_account(
        new_acc["holder_name"],
        new_acc["username"],
        new_acc["passwd"],
        new_acc["balance"],
    )
    if created_acc == None:
        return "USERNAME_ALREADY_EXISTS", 409
    created_acc.pop("password")
    created_acc.pop("role")
    return jsonify(created_acc), 201


@service.route("/account/<in_var>", methods=["DELETE"])
def findAndDelete(in_var) -> Response:
    token = getAuthToken(request)
    if token == "1":
        return "NO_AUTH_HEADER", 401
    elif token == "2":
        return "BAD_AUTH_HEADER", 400
    else:
        pass
    if not isAdminToken(token):
        return "ADMIN_ACTION_ONLY", 403
    if deleteAccount(in_var):
        return "", 204
    else:
        return "ACCOUNT_NOT_FOUND", 404


@service.route("/transaction", methods=["POST"])
def performTransaction() -> Response:
    token = getAuthToken(request)
    if token == "1":
        return "NO_AUTH_HEADER", 401
    elif token == "2":
        return "BAD_AUTH_HEADER", 400
    else:
        pass
    txn_details = json.loads(request.data)
    if not validateAccountToken(token, getAccountByAccNumber(txn_details["origin"])):
        return "UNAUTHORIZED_ACCESS", 401
    new_txn = Transaction(
        txn_details["origin"], txn_details["destination"], txn_details["amt"]
    )
    status = new_txn.startTransaction()
    if status == 0:
        return (
            jsonify(
                {
                    "status": "TRANSACTION_SUCCESS",
                    "transaction_id": "{}".format(new_txn.transactionID),
                }
            ),
            200,
        )
    elif status == 1:
        return (
            jsonify(
                {
                    "status": "TRANSACTION_FAILED",
                    "message": "ORIGIN_NOT_FOUND",
                    "transaction_id": "{}".format(new_txn.transactionID),
                }
            ),
            404,
        )
    elif status == 2:
        return (
            jsonify(
                {
                    "status": "TRANSACTION_FAILED",
                    "message": "DESTINATION_NOT_FOUND",
                    "transaction_id": "{}".format(new_txn.transactionID),
                }
            ),
            404,
        )
    else:
        return (
            jsonify(
                {
                    "status": "TRANSACTION_FAILED",
                    "message": "INSUFFICIENT_BALANCE",
                    "transaction_id": "{}".format(new_txn.transactionID),
                }
            ),
            404,
        )


@service.errorhandler(404)
def return_notFound():
    return "INVALID_URL", 404


if __name__ == "__main__":
    service.run(debug=True)
