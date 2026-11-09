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


class YearlyTab(QWidget):
    TITLE = "Annuel"

    def __init__(self, db):
        super().__init__()
        self.db = db
        layout = QVBoxLayout(self)
        top = QHBoxLayout()
        now = date.today()
        self.year = QComboBox()
        self.year.addItems(str(y) for y in range(now.year - 5, now.year + 2))
        self.year.setCurrentText(str(now.year))
        self.year.currentTextChanged.connect(self.refresh)
        export_btn = QPushButton("Exporter Excel")
        export_btn.clicked.connect(self.export)
        top.addWidget(QLabel("Année :"))
        top.addWidget(self.year)
        top.addWidget(export_btn)
        top.addStretch()
        layout.addLayout(top)
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Mois", "Débit (€)", "Crédit (€)", "Solde (€)"])
        layout.addWidget(self.table)
        self.summary = QLabel("")
        layout.addWidget(self.summary)
        self.refresh()

    def refresh(self):
        year = int(self.year.currentText())
        rep = reports.yearly_report(self.db, year)
        self.table.setRowCount(12)
        for i, month in enumerate(range(1, 13)):
            r = rep["by_month"][month]
            for j, v in enumerate([f"{month:02d}", f"{r['debit']:.2f}", f"{r['credit']:.2f}", f"{r['solde']:.2f}"]):
                self.table.setItem(i, j, QTableWidgetItem(str(v)))
        self.summary.setText(
            f"Total débit : {rep['total_debit']:.2f} € | Crédit : {rep['total_credit']:.2f} € | Solde : {rep['solde']:.2f} €"
        )

    def export(self):
        year = int(self.year.currentText())
        path, _ = QFileDialog.getSaveFileName(self, "Exporter l'année", f"budget_{year}.xlsx", "Excel (*.xlsx)")
        if path:
            exporters.export_year(self.db, path, year)
            self.summary.setText(f"Exporté : {path}")
