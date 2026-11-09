from __future__ import annotations

import openpyxl
from openpyxl.styles import Font

from . import reports


def _bold(ws, row):
    for cell in ws[row]:
        cell.font = Font(bold=True)


def export_month(db, path, year: int, month: int, account_id=None):
    rep = reports.monthly_report(db, year, month, account_id)
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Transactions"
    ws.append(["Date", "Compte", "Libellé", "Catégorie", "Montant (€)"])
    _bold(ws, 1)
    for t in rep["transactions"]:
        acc = db.get_account(t.account_id)
        cat = db.get_category(t.category_id)
        ws.append([t.date, acc.name if acc else "", t.label, cat.name if cat else "Non classé", t.amount])
    ws2 = wb.create_sheet("Résumé")
    ws2.append([f"Résumé {month:02d}/{year}"])
    ws2.append(["Catégorie", "Total (€)"])
    _bold(ws2, 2)
    for name, value in sorted(rep["by_category"].items()):
        ws2.append([name, value])
    ws2.append(["Total débit", rep["total_debit"]])
    ws2.append(["Total crédit", rep["total_credit"]])
    ws2.append(["Solde", rep["solde"]])
    wb.save(path)
    return path


def export_year(db, path, year: int, account_id=None):
    rep = reports.yearly_report(db, year, account_id)
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Annuel"
    ws.append([f"Année {year}"])
    ws.append(["Mois", "Débit (€)", "Crédit (€)", "Solde (€)"])
    _bold(ws, 2)
    for month in range(1, 13):
        r = rep["by_month"][month]
        ws.append([f"{month:02d}", r["debit"], r["credit"], r["solde"]])
    ws.append(["Total", rep["total_debit"], rep["total_credit"], rep["solde"]])
    ws2 = wb.create_sheet("Catégories")
    ws2.append(["Catégorie", "Total (€)"])
    _bold(ws2, 1)
    for name, value in sorted(rep["by_category"].items()):
        ws2.append([name, value])
    wb.save(path)
    return path
