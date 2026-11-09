from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..importer import import_file


class ImportTab(QWidget):
    TITLE = "Import bancaire"

    def __init__(self, db):
        super().__init__()
        self.db = db
        layout = QVBoxLayout(self)
        top = QHBoxLayout()
        self.account = QComboBox()
        self.refresh_accounts()
        self.path_label = QLabel("Aucun fichier sélectionné")
        pick_btn = QPushButton("Choisir un export (.xls/.xlsx/.csv)")
        pick_btn.clicked.connect(self.pick_file)
        import_btn = QPushButton("Importer")
        import_btn.clicked.connect(self.do_import)
        top.addWidget(QLabel("Compte :"))
        top.addWidget(self.account)
        top.addWidget(pick_btn)
        top.addWidget(import_btn)
        top.addStretch()
        layout.addLayout(top)
        layout.addWidget(self.path_label)
        self.result = QLabel("")
        layout.addWidget(self.result)
        layout.addStretch()
        self.file_path = None

    def refresh_accounts(self):
        self.account.clear()
        for acc in self.db.get_accounts():
            self.account.addItem(acc.name, acc.id)

    def pick_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Export bancaire", "", "Exports bancaires (*.xls *.xlsx *.csv)"
        )
        if path:
            self.file_path = path
            self.path_label.setText(path)

    def do_import(self):
        if not self.file_path:
            self.result.setText("Choisis d'abord un fichier.")
            return
        account_id = self.account.currentData()
        stats = import_file(self.db, self.file_path, account_id)
        self.result.setText(
            f"Import terminé : {stats['imported']} opérations importées, "
            f"{stats['skipped']} ignorées, {stats['transfers']} virement(s) détecté(s)."
        )
