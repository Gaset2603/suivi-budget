from __future__ import annotations

from PySide6.QtWidgets import QMainWindow, QTabWidget


class MainWindow(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setWindowTitle("Suivi de budget")
        self.resize(1100, 700)
        tabs = QTabWidget()
        from .accounts_tab import AccountsTab
        from .categories_tab import CategoriesTab
        from .import_tab import ImportTab
        from .manual_tab import ManualTab
        from .monthly_tab import MonthlyTab
        from .transfers_tab import TransfersTab
        from .yearly_tab import YearlyTab

        for cls in (
            MonthlyTab,
            YearlyTab,
            ImportTab,
            ManualTab,
            TransfersTab,
            AccountsTab,
            CategoriesTab,
        ):
            tabs.addTab(cls(self.db), cls.TITLE)
        self.setCentralWidget(tabs)


def run(db_path=None):
    from PySide6.QtWidgets import QApplication

    from ..config import DEFAULT_DB
    from ..db import Database

    app = QApplication([])
    db = Database(db_path or DEFAULT_DB)
    window = MainWindow(db)
    window.show()
    return app.exec()
