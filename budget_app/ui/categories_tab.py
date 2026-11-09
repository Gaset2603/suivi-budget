from __future__ import annotations

from PySide6.QtWidgets import (
    QInputDialog,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class CategoriesTab(QWidget):
    TITLE = "Catégories"

    def __init__(self, db):
        super().__init__()
        self.db = db
        layout = QVBoxLayout(self)
        self.name = QLineEdit()
        self.name.setPlaceholderText("Nouvelle catégorie")
        add_btn = QPushButton("Ajouter")
        add_btn.clicked.connect(self.add)
        edit_btn = QPushButton("Modifier les mots-clés de la catégorie sélectionnée")
        edit_btn.clicked.connect(self.edit_keywords)
        layout.addWidget(self.name)
        layout.addWidget(add_btn)
        layout.addWidget(edit_btn)
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Catégorie", "Mots-clés"])
        layout.addWidget(self.table)
        self.refresh()

    def add(self):
        if not self.name.text().strip():
            return
        self.db.add_category(self.name.text().strip())
        self.name.clear()
        self.refresh()

    def edit_keywords(self):
        row = self.table.currentRow()
        if row < 0:
            return
        cat = self.db.get_categories()[row] if row < len(self.db.get_categories()) else None
        if cat is None:
            return
        text, ok = QInputDialog.getText(self, "Mots-clés", "Mots-clés séparés par des virgules :", text=cat.keywords)
        if ok:
            self.db.set_category_keywords(cat.id, text)
            self.refresh()

    def refresh(self):
        categories = self.db.get_categories()
        self.table.setRowCount(len(categories))
        for i, cat in enumerate(categories):
            self.table.setItem(i, 0, QTableWidgetItem(cat.name))
            self.table.setItem(i, 1, QTableWidgetItem(cat.keywords))
