from __future__ import annotations


def monthly_report(db, year: int, month: int, account_id=None):
    prefix = f"{year:04d}-{month:02d}"
    txs = db.list_transactions(account_id=account_id, prefix=prefix)
    by_category = {}
    debit = credit = 0.0
    for t in txs:
        cat = db.get_category(t.category_id)
        name = cat.name if cat else "Non classé"
        by_category[name] = round(by_category.get(name, 0.0) + t.amount, 2)
        if t.amount < 0:
            debit += -t.amount
        else:
            credit += t.amount
    return {
        "year": year,
        "month": month,
        "transactions": txs,
        "by_category": by_category,
        "total_debit": round(debit, 2),
        "total_credit": round(credit, 2),
        "solde": round(credit - debit, 2),
    }


def yearly_report(db, year: int, account_id=None):
    by_month = {}
    by_category = {}
    total_debit = total_credit = 0.0
    for month in range(1, 13):
        rep = monthly_report(db, year, month, account_id)
        by_month[month] = {
            "debit": rep["total_debit"],
            "credit": rep["total_credit"],
            "solde": rep["solde"],
        }
        total_debit += rep["total_debit"]
        total_credit += rep["total_credit"]
        for name, value in rep["by_category"].items():
            by_category[name] = round(by_category.get(name, 0.0) + value, 2)
    return {
        "year": year,
        "by_month": by_month,
        "by_category": by_category,
        "total_debit": round(total_debit, 2),
        "total_credit": round(total_credit, 2),
        "solde": round(total_credit - total_debit, 2),
    }
