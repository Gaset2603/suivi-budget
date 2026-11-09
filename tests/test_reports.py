import unittest

from budget_app.db import Database
from budget_app.reports import monthly_report, yearly_report


class TestReports(unittest.TestCase):
    def setUp(self):
        self.db = Database(":memory:")
        self.commun = self.db.add_account("Commun", "commun")
        self.perso = self.db.add_account("JEAN", "perso")
        alim = next(c for c in self.db.get_categories() if c.name == "Alimentation")
        loge = next(c for c in self.db.get_categories() if c.name == "Logement")
        self.db.add_transaction(self.commun, "2026-01-05", "CARREFOUR", -100.0, category_id=alim.id)
        self.db.add_transaction(self.commun, "2026-01-20", "EDF", -50.0, category_id=loge.id)
        self.db.add_transaction(self.commun, "2026-02-03", "CARREFOUR", -30.0, category_id=alim.id)
        self.db.add_transaction(self.commun, "2026-01-31", "SALAIRE", 2000.0, source="manuel")
        self.db.add_transaction(self.perso, "2026-01-15", "CARREFOUR PERSO", -20.0, category_id=alim.id)

    def tearDown(self):
        self.db.close()

    def test_monthly_report(self):
        rep = monthly_report(self.db, 2026, 1, account_id=self.commun)
        self.assertEqual(rep["total_debit"], 150.0)
        self.assertEqual(rep["total_credit"], 2000.0)
        self.assertEqual(rep["solde"], 1850.0)
        self.assertEqual(rep["by_category"]["Alimentation"], -100.0)
        self.assertEqual(len(rep["transactions"]), 3)

    def test_monthly_report_all_accounts(self):
        rep = monthly_report(self.db, 2026, 1)
        self.assertEqual(rep["by_category"]["Alimentation"], -120.0)

    def test_yearly_report(self):
        rep = yearly_report(self.db, 2026, account_id=self.commun)
        self.assertEqual(len(rep["by_month"]), 12)
        self.assertEqual(rep["by_month"][1]["debit"], 150.0)
        self.assertEqual(rep["by_month"][2]["debit"], 30.0)
        self.assertEqual(rep["total_debit"], 180.0)
        self.assertEqual(rep["by_category"]["Alimentation"], -130.0)


if __name__ == "__main__":
    unittest.main()
