from __future__ import annotations

from datetime import date

from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDoubleSpinBox,
    QFormLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class TransfersTab(QWidget):
    TITLE = "Virements"

    def __init__(self, db):
        super().__init__()
        self.db = db
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.date_edit = QDateEdit(date.today())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.from_acc = QComboBox()
        self.to_acc = QComboBox()
        self.amount = QDoubleSpinBox()
        self.amount.setRange(0, 1000000)
        self.amount.setDecimals(2)
        self.refresh_combos()
        form.addRow("Date", self.date_edit)
        form.addRow("Depuis", self.from_acc)
        form.addRow("Vers", self.to_acc)
        form.addRow("Montant (€)", self.amount)
        add_btn = QPushButton("Ajouter le virement")
        add_btn.clicked.connect(self.add)
        layout.addLayout(form)
        layout.addWidget(add_btn)
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Date", "Depuis", "Vers", "Montant (€)", "Libellé"])
        layout.addWidget(self.table)
        self.refresh()

    def refresh_combos(self):
        self.from_acc.clear()
        self.to_acc.clear()
        for acc in self.db.get_accounts():
            self.from_acc.addItem(acc.name, acc.id)
            self.to_acc.addItem(acc.name, acc.id)

    def add(self):
        from_id = self.from_acc.currentData()
        to_id = self.to_acc.currentData()
        if from_id is None or to_id is None or from_id == to_id:
            return
        self.db.add_transfer(
            from_id, to_id, self.date_edit.date().toString("yyyy-MM-dd"), self.amount.value(), "Saisie manuelle"
        )
        self.refresh()

    def refresh(self):
        transfers = self.db.list_transfers()
        self.table.setRowCount(len(transfers))
        for i, t in enumerate(reversed(transfers)):
            src = self.db.get_account(t.from_account_id)
            dst = self.db.get_account(t.to_account_id)
            values = [t.date, src.name if src else "", dst.name if dst else "", f"{t.amount:.2f}", t.label]
            for j, v in enumerate(values):
                self.table.setItem(i, j, QTableWidgetItem(str(v)))
