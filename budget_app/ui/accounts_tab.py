from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class AccountsTab(QWidget):
    TITLE = "Comptes & cartes"

    def __init__(self, db):
        super().__init__()
        self.db = db
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.name = QLineEdit()
        self.type = QComboBox()
        self.type.addItems(["commun", "perso"])
        self.card = QLineEdit()
        self.card.setPlaceholderText("ex. X2121")
        form.addRow("Nom du compte", self.name)
        form.addRow("Type", self.type)
        form.addRow("Carte (masque)", self.card)
        add_btn = QPushButton("Ajouter le compte")
        add_btn.clicked.connect(self.add)
        layout.addLayout(form)
        layout.addWidget(add_btn)
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Nom", "Type", "Carte"])
        layout.addWidget(self.table)
        self.refresh()

    def add(self):
        if not self.name.text().strip():
            return
        self.db.add_account(self.name.text().strip(), self.type.currentText(), self.card.text().strip())
        self.name.clear()
        self.card.clear()
        self.refresh()

    def refresh(self):
        accounts = self.db.get_accounts()
        self.table.setRowCount(len(accounts))
        for i, acc in enumerate(accounts):
            for j, v in enumerate([acc.name, acc.type, acc.card_mask]):
                self.table.setItem(i, j, QTableWidgetItem(str(v)))
