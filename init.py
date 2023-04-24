from flask import Flask,render_template,jsonify,abort,request
from model.Accounts.accounts import *

service = Flask(__name__)

@service.route("/")
def display_doc():
    return render_template('index.html')

@service.route("/account/<in_var>",methods = ['GET'])
def getaccounts(in_var):
    req_account = getAccountByAccNumber(str(in_var))
    if req_account == None: 
        req_account = getAccountByUsername(str(in_var))
        if req_account == None: 
            abort(404)
    return jsonify(req_account)

if __name__ == "__main__":
    service.run(debug=True)