from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Account:
    id: int
    name: str
    type: str = "commun"
    card_mask: str = ""


@dataclass
class Category:
    id: int
    name: str
    keywords: str = ""

    def keywords_list(self):
        return [k.strip() for k in self.keywords.split(",") if k.strip()]


@dataclass
class Transaction:
    id: int
    account_id: int
    date: str
    label: str
    amount: float
    category_id: Optional[int] = None
    raw_label: str = ""
    source: str = "import"
    transfer_id: Optional[int] = None


@dataclass
class Transfer:
    id: int
    from_account_id: int
    to_account_id: int
    date: str
    amount: float
    label: str = ""
