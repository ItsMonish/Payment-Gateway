from flask import Flask, render_template, jsonify, request, Response
from model.Accounts.accounts import *
from model.transactions import *
import json

service = Flask(__name__)


@service.route("/")
def display_doc():
    return render_template("index.html")


@service.route("/account/<in_var>", methods=["GET"])
def getaccounts(in_var) -> Response:
    req_account = getAccountByAccNumber(str(in_var))
    if req_account == None:
        req_account = getAccountByUsername(str(in_var))
        if req_account == None:
            return "ACCOUNT_NOT_FOUND", 404
    txns = fetchTransactions(req_account["Account Number"])
    return jsonify(req_account, {"transactions": txns})


@service.route("/account", methods=["PUT"])
def addAccount() -> Response:
    new_acc = json.loads(request.data)
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
    if deleteAccount(in_var):
        return "DELETE_SUCCESSFUL", 204
    else:
        return "ACCOUNT_NOT_FOUND", 404


@service.route("/transaction", methods=["POST"])
def performTransaction() -> Response:
    txn_details = json.loads(request.data)
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


@service.route("/transactions/str:<in_var>")
def findTransaction(in_var) -> Response:
    req_txn = findTransaction(in_var)
    if req_txn == None:
        return "TRANSACTION_ID_NOT_FOUND", 404
    return jsonify(req_txn), 200


if __name__ == "__main__":
    service.run(debug=True)
