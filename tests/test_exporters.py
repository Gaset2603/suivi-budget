import os
import tempfile
import unittest

import openpyxl

from budget_app.db import Database
from budget_app.exporters import export_month, export_year


class TestExporters(unittest.TestCase):
    def setUp(self):
        self.db = Database(":memory:")
        self.aid = self.db.add_account("Commun", "commun")
        alim = next(c for c in self.db.get_categories() if c.name == "Alimentation")
        self.db.add_transaction(self.aid, "2026-01-05", "CARREFOUR", -100.0, category_id=alim.id)
        self.db.add_transaction(self.aid, "2026-01-31", "SALAIRE", 2000.0, source="manuel")
        self.db.add_transaction(self.aid, "2026-02-03", "CARREFOUR", -30.0, category_id=alim.id)
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.db.close()
        self.tmp.cleanup()

    def test_export_month(self):
        path = os.path.join(self.tmp.name, "mois.xlsx")
        export_month(self.db, path, 2026, 1, account_id=self.aid)
        wb = openpyxl.load_workbook(path)
        self.assertEqual(wb.sheetnames, ["Transactions", "Résumé"])
        ws = wb["Transactions"]
        self.assertEqual(ws.max_row, 3)
        self.assertEqual(ws.cell(row=2, column=1).value, "2026-01-05")
        self.assertEqual(ws.cell(row=2, column=4).value, "Alimentation")
        self.assertEqual(ws.cell(row=2, column=5).value, -100.0)
        resume = wb["Résumé"]
        values = [resume.cell(row=r, column=1).value for r in range(1, resume.max_row + 1)]
        self.assertIn("Solde", values)

    def test_export_year(self):
        path = os.path.join(self.tmp.name, "annee.xlsx")
        export_year(self.db, path, 2026, account_id=self.aid)
        wb = openpyxl.load_workbook(path)
        self.assertEqual(wb.sheetnames, ["Annuel", "Catégories"])
        ws = wb["Annuel"]
        self.assertEqual(ws.max_row, 15)
        self.assertEqual(ws.cell(row=3, column=1).value, "01")
        self.assertEqual(ws.cell(row=3, column=2).value, 100.0)


if __name__ == "__main__":
    unittest.main()
