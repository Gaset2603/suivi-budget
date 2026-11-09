from __future__ import annotations

import sqlite3
from typing import Optional

from .models import Account, Category, Transaction, Transfer

SCHEMA = """
CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    type TEXT NOT NULL DEFAULT 'commun',
    card_mask TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    keywords TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS transfers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_account_id INTEGER NOT NULL REFERENCES accounts(id),
    to_account_id INTEGER NOT NULL REFERENCES accounts(id),
    date TEXT NOT NULL,
    amount REAL NOT NULL,
    label TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL REFERENCES accounts(id),
    date TEXT NOT NULL,
    label TEXT NOT NULL,
    raw_label TEXT NOT NULL DEFAULT '',
    amount REAL NOT NULL,
    category_id INTEGER REFERENCES categories(id),
    source TEXT NOT NULL DEFAULT 'import',
    transfer_id INTEGER REFERENCES transfers(id),
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_tx_date ON transactions(date);
CREATE INDEX IF NOT EXISTS idx_tx_account ON transactions(account_id);
"""

DEFAULT_CATEGORIES = [
    ("Alimentation", "courses,carrefour,auchan,leclerc,intermarche,boulangerie,restaurant,uber eats,deliveroo,supermarche"),
    ("Transport", "essence,sncf,uber,taxi,parking,peage,autoroute,total,ratp"),
    ("Logement", "loyer,edf,electricite,gaz,eau,orange,free,internet,assurance habitation"),
    ("Sante", "pharmacie,medecin,dentiste,mutuelle,opticien,docteur"),
    ("Loisirs", "cinema,netflix,spotify,jeu,steam,bar,theatre"),
    ("Abonnements", "abonnement,forfait,mobile"),
    ("Virements", "virement"),
    ("Autre", ""),
]


class Database:
    def __init__(self, path: str = ":memory:"):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.executescript(SCHEMA)
        self.seed_categories()

    def close(self):
        self.conn.close()

    def seed_categories(self):
        for name, kw in DEFAULT_CATEGORIES:
            self.conn.execute(
                "INSERT OR IGNORE INTO categories(name, keywords) VALUES (?, ?)", (name, kw)
            )
        self.conn.commit()

    def add_account(self, name: str, type: str = "commun", card_mask: str = "") -> int:
        cur = self.conn.execute(
            "INSERT INTO accounts(name, type, card_mask) VALUES (?, ?, ?)", (name, type, card_mask)
        )
        self.conn.commit()
        return cur.lastrowid

    def get_accounts(self):
        rows = self.conn.execute("SELECT * FROM accounts ORDER BY name").fetchall()
        return [Account(r["id"], r["name"], r["type"], r["card_mask"] or "") for r in rows]

    def get_account(self, account_id: int) -> Optional[Account]:
        r = self.conn.execute("SELECT * FROM accounts WHERE id = ?", (account_id,)).fetchone()
        return Account(r["id"], r["name"], r["type"], r["card_mask"] or "") if r else None

    def get_account_by_name(self, name: str) -> Optional[Account]:
        r = self.conn.execute("SELECT * FROM accounts WHERE name = ?", (name,)).fetchone()
        return Account(r["id"], r["name"], r["type"], r["card_mask"] or "") if r else None

    def set_card_mask(self, account_id: int, mask: str):
        self.conn.execute("UPDATE accounts SET card_mask = ? WHERE id = ?", (mask, account_id))
        self.conn.commit()

    def add_category(self, name: str, keywords: str = "") -> int:
        cur = self.conn.execute(
            "INSERT OR IGNORE INTO categories(name, keywords) VALUES (?, ?)", (name, keywords)
        )
        self.conn.commit()
        return cur.lastrowid

    def get_categories(self):
        rows = self.conn.execute("SELECT * FROM categories ORDER BY name").fetchall()
        return [Category(r["id"], r["name"], r["keywords"] or "") for r in rows]

    def get_category(self, category_id: Optional[int]) -> Optional[Category]:
        if category_id is None:
            return None
        r = self.conn.execute("SELECT * FROM categories WHERE id = ?", (category_id,)).fetchone()
        return Category(r["id"], r["name"], r["keywords"] or "") if r else None

    def set_category_keywords(self, category_id: int, keywords: str):
        self.conn.execute(
            "UPDATE categories SET keywords = ? WHERE id = ?", (keywords, category_id)
        )
        self.conn.commit()

    def _tx(self, r) -> Transaction:
        return Transaction(
            r["id"], r["account_id"], r["date"], r["label"], r["amount"],
            r["category_id"], r["raw_label"], r["source"], r["transfer_id"],
        )

    def add_transaction(
        self,
        account_id: int,
        date: str,
        label: str,
        amount: float,
        category_id: Optional[int] = None,
        raw_label: str = "",
        source: str = "import",
    ) -> int:
        cur = self.conn.execute(
            "INSERT INTO transactions(account_id, date, label, raw_label, amount, category_id, source)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)",
            (account_id, date, label, raw_label or label, round(amount, 2), category_id, source),
        )
        self.conn.commit()
        return cur.lastrowid

    def get_transaction(self, tx_id: int) -> Optional[Transaction]:
        r = self.conn.execute("SELECT * FROM transactions WHERE id = ?", (tx_id,)).fetchone()
        return self._tx(r) if r else None

    def list_transactions(self, account_id: Optional[int] = None, prefix: Optional[str] = None):
        query = "SELECT * FROM transactions"
        cond, params = [], []
        if account_id is not None:
            cond.append("account_id = ?")
            params.append(account_id)
        if prefix:
            cond.append("date LIKE ?")
            params.append(prefix + "%")
        if cond:
            query += " WHERE " + " AND ".join(cond)
        query += " ORDER BY date, id"
        return [self._tx(r) for r in self.conn.execute(query, params).fetchall()]

    def set_transaction_category(self, tx_id: int, category_id: Optional[int]):
        self.conn.execute(
            "UPDATE transactions SET category_id = ? WHERE id = ?", (category_id, tx_id)
        )
        self.conn.commit()

    def set_transaction_transfer(self, tx_id: int, transfer_id: Optional[int]):
        self.conn.execute(
            "UPDATE transactions SET transfer_id = ? WHERE id = ?", (transfer_id, tx_id)
        )
        self.conn.commit()

    def add_transfer(
        self, from_account_id: int, to_account_id: int, date: str, amount: float, label: str = ""
    ) -> Transfer:
        cur = self.conn.execute(
            "INSERT INTO transfers(from_account_id, to_account_id, date, amount, label) VALUES (?, ?, ?, ?, ?)",
            (from_account_id, to_account_id, date, round(abs(amount), 2), label),
        )
        self.conn.commit()
        return Transfer(cur.lastrowid, from_account_id, to_account_id, date, round(abs(amount), 2), label)

    def list_transfers(self):
        rows = self.conn.execute("SELECT * FROM transfers ORDER BY date, id").fetchall()
        return [
            Transfer(r["id"], r["from_account_id"], r["to_account_id"], r["date"], r["amount"], r["label"])
            for r in rows
        ]
