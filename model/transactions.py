class Transactions:

    def __init__(self, txnID, origin_acc, dest_acc, amount) -> None:
        self.transactionID = txnID
        self.origin_account = origin_acc
        self.destination_account = dest_acc
        self.amount = amount
        