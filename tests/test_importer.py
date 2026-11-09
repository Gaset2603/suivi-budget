import os
import tempfile
import unittest
from datetime import datetime

from budget_app.db import Database
from budget_app.importer import (
    detect_separator,
    flatten_label,
    import_file,
    parse_amount,
    parse_date,
)

CSV_CONTENT = (
    "Export du compte courant X2121;;;;\n"
    "Date opération;Libellé;Débit;Crédit\n"
    '05/01/2026;"CARREFOUR MARKET\nCentre ville";"1\u202f234,56";\n'
    "06/01/2026;VIREMENT EMIS VERS JEAN;500,00;;\n"
    "07/01/2026;EDF ENERGIE;80,25;;\n"
    "20/01/2026;CARTE X2121 PHARMACIE CENTRALE;12,40;;\n"
)


class TestParsing(unittest.TestCase):
    def test_detect_separator(self):
        self.assertEqual(detect_separator("a;b;c"), ";")
        self.assertEqual(detect_separator("a,b,c"), ",")

    def test_parse_amount(self):
        self.assertEqual(parse_amount("1\u202f234,56 €"), 1234.56)
        self.assertEqual(parse_amount("-80,25"), -80.25)
        self.assertEqual(parse_amount("(12,00)"), -12.0)
        self.assertEqual(parse_amount(""), 0.0)
        self.assertEqual(parse_amount(None), 0.0)
        self.assertEqual(parse_amount(42.5), 42.5)

    def test_parse_date(self):
        self.assertEqual(parse_date("05/01/2026"), "2026-01-05")
        self.assertEqual(parse_date("2026-01-05"), "2026-01-05")
        self.assertEqual(parse_date(datetime(2026, 1, 5, 15, 30)), "2026-01-05")
        self.assertIsNone(parse_date("Export du compte"))

    def test_flatten_label(self):
        self.assertEqual(flatten_label("CARREFOUR\nMARKET  Paris"), "CARREFOUR MARKET Paris")


class TestImport(unittest.TestCase):
    def setUp(self):
        self.db = Database(":memory:")
        self.commun = self.db.add_account("Commun", "commun")
        self.db.add_account("JEAN", "perso")
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.db.close()
        self.tmp.cleanup()

    def _write(self, name, content, mode="w"):
        path = os.path.join(self.tmp.name, name)
        with open(path, mode, newline="" if "b" in mode else None) as f:
            f.write(content)
        return path

    def test_import_csv(self):
        path = self._write("export.csv", CSV_CONTENT)
        stats = import_file(self.db, path, self.commun)
        self.assertEqual(stats["imported"], 4)
        self.assertEqual(stats["skipped"], 1)
        self.assertEqual(stats["transfers"], 1)
        txs = self.db.list_transactions(account_id=self.commun)
        self.assertEqual(len(txs), 4)
        carrefour = next(t for t in txs if "CARREFOUR" in t.label)
        self.assertEqual(carrefour.amount, -1234.56)
        self.assertEqual(carrefour.date, "2026-01-05")
        self.assertEqual(carrefour.label, "CARREFOUR MARKET Centre ville")
        self.assertEqual(self.db.get_category(carrefour.category_id).name, "Alimentation")
        self.assertEqual(self.db.get_account(self.commun).card_mask, "X2121")
        virement = next(t for t in txs if "VIREMENT" in t.label)
        self.assertIsNotNone(virement.transfer_id)
        edf = next(t for t in txs if "EDF" in t.label)
        self.assertEqual(self.db.get_category(edf.category_id).name, "Logement")
        carte = next(t for t in txs if "CARTE X2121" in t.label)
        self.assertEqual(self.db.get_category(carte.category_id).name, "Sante")

    def test_import_xlsx(self):
        import openpyxl

        path = os.path.join(self.tmp.name, "export.xlsx")
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(["Date opération", "Libellé", "Débit", "Crédit"])
        ws.append(["10/02/2026", "CARREFOUR", 25.9, None])
        ws.append(["11/02/2026", "SALAIRE ENTREPRISE", None, 2100.0])
        wb.save(path)
        stats = import_file(self.db, path, self.commun)
        self.assertEqual(stats["imported"], 2)
        txs = self.db.list_transactions(account_id=self.commun)
        self.assertEqual(txs[0].amount, -25.9)
        self.assertEqual(txs[1].amount, 2100.0)

    def test_import_xls(self):
        try:
            import xlwt
        except ImportError:
            self.skipTest("xlwt non installé")
        path = os.path.join(self.tmp.name, "export.xls")
        wb = xlwt.Workbook()
        ws = wb.add_sheet("Operations")
        ws.write(0, 0, "Date opération")
        ws.write(0, 1, "Libellé")
        ws.write(0, 2, "Débit")
        ws.write(0, 3, "Crédit")
        ws.write(1, 0, "15/03/2026")
        ws.write(1, 1, "EDF")
        ws.write(1, 2, 66.4)
        wb.save(path)
        stats = import_file(self.db, path, self.commun)
        self.assertEqual(stats["imported"], 1)
        tx = self.db.list_transactions(account_id=self.commun)[0]
        self.assertEqual(tx.amount, -66.4)
        self.assertEqual(self.db.get_category(tx.category_id).name, "Logement")

    def test_unsupported_format(self):
        path = self._write("export.txt", "hello")
        with self.assertRaises(ValueError):
            import_file(self.db, path, self.commun)


if __name__ == "__main__":
    unittest.main()
