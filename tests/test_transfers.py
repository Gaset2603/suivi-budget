import unittest

from budget_app.db import Database
from budget_app.transfers import detect_and_create


class TestTransfers(unittest.TestCase):
    def setUp(self):
        self.db = Database(":memory:")
        self.commun = self.db.add_account("Commun", "commun")
        self.perso = self.db.add_account("JEAN", "perso")

    def tearDown(self):
        self.db.close()

    def test_virement_emis_creates_transfer(self):
        tx = self.db.add_transaction(self.commun, "2026-01-10", "VIREMENT EMIS VERS JEAN", -500.0)
        transfer = detect_and_create(self.db, self.db.get_transaction(tx))
        self.assertIsNotNone(transfer)
        self.assertEqual(transfer.from_account_id, self.commun)
        self.assertEqual(transfer.to_account_id, self.perso)
        self.assertEqual(transfer.amount, 500.0)
        self.assertEqual(self.db.get_transaction(tx).transfer_id, transfer.id)

    def test_virement_recu_direction(self):
        tx = self.db.add_transaction(self.commun, "2026-01-12", "VIREMENT RECU DE JEAN", 300.0)
        transfer = detect_and_create(self.db, self.db.get_transaction(tx))
        self.assertEqual(transfer.from_account_id, self.perso)
        self.assertEqual(transfer.to_account_id, self.commun)

    def test_no_virement(self):
        tx = self.db.add_transaction(self.commun, "2026-01-10", "CARREFOUR", -50.0)
        self.assertIsNone(detect_and_create(self.db, self.db.get_transaction(tx)))

    def test_unknown_counterparty(self):
        tx = self.db.add_transaction(self.commun, "2026-01-10", "VIREMENT EMIS VERS INCONNU", -10.0)
        self.assertIsNone(detect_and_create(self.db, self.db.get_transaction(tx)))


if __name__ == "__main__":
    unittest.main()
