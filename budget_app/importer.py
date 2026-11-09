from __future__ import annotations

import csv
import re
import unicodedata
from datetime import datetime, timedelta
from pathlib import Path

from . import categorizer, transfers

DATE_HEADERS = {"date operation", "date", "date de valeur", "date comptabilisation"}
LABEL_HEADERS = {"libelle", "description", "details", "detail", "intitule"}
DEBIT_HEADERS = {"debit", "montant debit"}
CREDIT_HEADERS = {"credit", "montant credit"}

CARD_RE = re.compile(r"CARTE\s+(X\d{4})")


def _norm_header(value) -> str:
    s = unicodedata.normalize("NFD", str(value).lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def detect_separator(sample_line: str) -> str:
    return ";" if sample_line.count(";") >= sample_line.count(",") else ","


def parse_amount(text) -> float:
    if text is None:
        return 0.0
    if isinstance(text, (int, float)):
        return round(float(text), 2)
    s = str(text).strip()
    if not s:
        return 0.0
    s = s.replace("\u202f", " ").replace("\xa0", " ").replace(" ", "")
    s = s.replace("€", "").replace(",", ".")
    negative = s.startswith("-") or (s.startswith("(") and s.endswith(")"))
    s = s.strip("()-")
    try:
        value = float(s)
    except ValueError:
        return 0.0
    return round(-value if negative else value, 2)


def parse_date(text):
    if text is None:
        return None
    if isinstance(text, datetime):
        return text.date().isoformat()
    s = str(text).strip()
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%y"):
        try:
            return datetime.strptime(s, fmt).date().isoformat()
        except ValueError:
            pass
    try:
        serial = float(s)
        if 20000 < serial < 80000:
            return (datetime(1899, 12, 30) + timedelta(days=serial)).date().isoformat()
    except ValueError:
        pass
    return None


def flatten_label(text) -> str:
    return re.sub(r"\s+", " ", str(text).replace("\r", " ").replace("\n", " ")).strip()


def _rows(path):
    ext = Path(path).suffix.lower()
    if ext == ".csv":
        with open(path, newline="", encoding="utf-8-sig") as handle:
            first = handle.readline()
            handle.seek(0)
            sep = detect_separator(first)
            for row in csv.reader(handle, delimiter=sep):
                yield ["" if c is None else c for c in row]
    elif ext == ".xlsx":
        import openpyxl

        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        for row in wb.active.iter_rows(values_only=True):
            yield ["" if c is None else c for c in row]
    elif ext == ".xls":
        import xlrd

        wb = xlrd.open_workbook(path)
        sheet = wb.sheet_by_index(0)
        for r in range(sheet.nrows):
            yield [sheet.cell_value(r, c) for c in range(sheet.ncols)]
    else:
        raise ValueError(f"Format non supporté: {ext}")


def _column_map(header_row):
    cols = {}
    for i, cell in enumerate(header_row):
        h = _norm_header(cell)
        if h in DATE_HEADERS and "date" not in cols:
            cols["date"] = i
        elif h in LABEL_HEADERS and "label" not in cols:
            cols["label"] = i
        elif h in DEBIT_HEADERS and "debit" not in cols:
            cols["debit"] = i
        elif h in CREDIT_HEADERS and "credit" not in cols:
            cols["credit"] = i
    return cols


def import_file(db, path, account_id: int):
    rows = list(_rows(path))
    if not rows:
        return {"imported": 0, "skipped": 0, "transfers": 0}
    cols = _column_map(rows[0])
    if len(cols) >= 2:
        start = 1
    elif len(rows) > 1 and len(_column_map(rows[1])) >= 2:
        cols = _column_map(rows[1])
        start = 2
    else:
        cols = {"date": 0, "label": 1, "debit": 2, "credit": 3}
        start = 0

    def cell(row, key):
        i = cols.get(key)
        return row[i] if i is not None and i < len(row) else ""

    imported = skipped = n_transfers = 0
    if start == 2:
        skipped = 1
    for row in rows[start:]:
        if not row or all(str(c).strip() == "" for c in row):
            continue
        date = parse_date(cell(row, "date"))
        if not date:
            skipped += 1
            continue
        label = flatten_label(cell(row, "label"))
        debit = parse_amount(cell(row, "debit"))
        credit = parse_amount(cell(row, "credit"))
        amount = round(credit - debit, 2)
        if amount == 0 and not label:
            skipped += 1
            continue
        match = CARD_RE.search(label.upper())
        if match:
            db.set_card_mask(account_id, match.group(1))
        category_id = categorizer.auto_categorize(db, label)
        tx_id = db.add_transaction(
            account_id, date, label, amount, category_id=category_id, raw_label=label, source="import"
        )
        if transfers.detect_and_create(db, db.get_transaction(tx_id)):
            n_transfers += 1
        imported += 1
    return {"imported": imported, "skipped": skipped, "transfers": n_transfers}
