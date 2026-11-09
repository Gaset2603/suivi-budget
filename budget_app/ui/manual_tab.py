from __future__ import annotations

from datetime import date

from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDoubleSpinBox,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class ManualTab(QWidget):
    TITLE = "Saisie manuelle"

    def __init__(self, db):
        super().__init__()
        self.db = db
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.date_edit = QDateEdit(date.today())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.label = QLineEdit()
        self.amount = QDoubleSpinBox()
        self.amount.setRange(-1000000, 1000000)
        self.amount.setDecimals(2)
        self.account = QComboBox()
        self.category = QComboBox()
        self.refresh_combos()
        form.addRow("Date", self.date_edit)
        form.addRow("Libellé", self.label)
        form.addRow("Montant (€)", self.amount)
        form.addRow("Compte", self.account)
        form.addRow("Catégorie", self.category)
        add_btn = QPushButton("Ajouter")
        add_btn.clicked.connect(self.add)
        layout.addLayout(form)
        layout.addWidget(add_btn)
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Date", "Compte", "Libellé", "Catégorie", "Montant (€)"])
        layout.addWidget(self.table)
        self.refresh()

    def refresh_combos(self):
        self.account.clear()
        for acc in self.db.get_accounts():
            self.account.addItem(acc.name, acc.id)
        self.category.clear()
        self.category.addItem("Non classé", None)
        for cat in self.db.get_categories():
            self.category.addItem(cat.name, cat.id)

    def add(self):
        if not self.label.text().strip():
            return
        self.db.add_transaction(
            self.account.currentData(),
            self.date_edit.date().toString("yyyy-MM-dd"),
            self.label.text().strip(),
            self.amount.value(),
            category_id=self.category.currentData(),
            source="manuel",
        )
        self.label.clear()
        self.amount.setValue(0.0)
        self.refresh()

    def refresh(self):
        txs = self.db.list_transactions()
        self.table.setRowCount(len(txs))
        for i, t in enumerate(reversed(txs)):
            acc = self.db.get_account(t.account_id)
            cat = self.db.get_category(t.category_id)
            values = [t.date, acc.name if acc else "", t.label, cat.name if cat else "Non classé", f"{t.amount:.2f}"]
            for j, v in enumerate(values):
                self.table.setItem(i, j, QTableWidgetItem(str(v)))
