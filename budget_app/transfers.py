from __future__ import annotations

from .categorizer import normalize


def detect_and_create(db, transaction):
    if transaction is None:
        return None
    if "VIREMENT" not in transaction.label.upper():
        return None
    norm_label = normalize(transaction.label)
    for acc in db.get_accounts():
        if acc.id == transaction.account_id:
            continue
        if normalize(acc.name) and normalize(acc.name) in norm_label:
            amount = abs(transaction.amount)
            if transaction.amount < 0:
                transfer = db.add_transfer(
                    transaction.account_id, acc.id, transaction.date, amount, transaction.label
                )
            else:
                transfer = db.add_transfer(
                    acc.id, transaction.account_id, transaction.date, amount, transaction.label
                )
            db.set_transaction_transfer(transaction.id, transfer.id)
            return transfer
    return None
