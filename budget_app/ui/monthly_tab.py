from __future__ import annotations

from datetime import date

from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from .. import exporters, reports


class MonthlyTab(QWidget):
    TITLE = "Mensuel"

    def __init__(self, db):
        super().__init__()
        self.db = db
        layout = QVBoxLayout(self)
        top = QHBoxLayout()
        now = date.today()
        self.year = QComboBox()
        self.year.addItems(str(y) for y in range(now.year - 5, now.year + 2))
        self.year.setCurrentText(str(now.year))
        self.month = QComboBox()
        self.month.addItems(f"{m:02d}" for m in range(1, 13))
        self.month.setCurrentText(f"{now.month:02d}")
        self.year.currentTextChanged.connect(self.refresh)
        self.month.currentTextChanged.connect(self.refresh)
        export_btn = QPushButton("Exporter Excel")
        export_btn.clicked.connect(self.export)
        top.addWidget(QLabel("Année :"))
        top.addWidget(self.year)
        top.addWidget(QLabel("Mois :"))
        top.addWidget(self.month)
        top.addWidget(export_btn)
        top.addStretch()
        layout.addLayout(top)
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Date", "Compte", "Libellé", "Catégorie", "Montant (€)"])
        layout.addWidget(self.table)
        self.summary = QLabel("")
        layout.addWidget(self.summary)
        self.refresh()

    def refresh(self):
        rep = reports.monthly_report(self.db, int(self.year.currentText()), int(self.month.currentText()))
        self.table.setRowCount(len(rep["transactions"]))
        for i, t in enumerate(rep["transactions"]):
            acc = self.db.get_account(t.account_id)
            cat = self.db.get_category(t.category_id)
            values = [t.date, acc.name if acc else "", t.label, cat.name if cat else "Non classé", f"{t.amount:.2f}"]
            for j, v in enumerate(values):
                self.table.setItem(i, j, QTableWidgetItem(str(v)))
        self.summary.setText(
            f"Débit : {rep['total_debit']:.2f} € | Crédit : {rep['total_credit']:.2f} € | Solde : {rep['solde']:.2f} €"
        )

    def export(self):
        default = f"budget_{self.year.currentText()}-{self.month.currentText()}.xlsx"
        path, _ = QFileDialog.getSaveFileName(self, "Exporter le mois", default, "Excel (*.xlsx)")
        if path:
            exporters.export_month(self.db, path, int(self.year.currentText()), int(self.month.currentText()))
            self.summary.setText(f"Exporté : {path}")
