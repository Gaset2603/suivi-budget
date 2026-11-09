import unittest

from budget_app.db import Database


class TestDb(unittest.TestCase):
    def setUp(self):
        self.db = Database(":memory:")

    def tearDown(self):
        self.db.close()

    def test_seed_categories(self):
        cats = self.db.get_categories()
        self.assertGreaterEqual(len(cats), 8)
        self.assertIn("Alimentation", {c.name for c in cats})

    def test_add_account_and_card_mask(self):
        aid = self.db.add_account("Commun", "commun")
        self.db.set_card_mask(aid, "X2121")
        acc = self.db.get_account(aid)
        self.assertEqual(acc.card_mask, "X2121")
        self.assertEqual(acc.type, "commun")
        self.assertEqual(self.db.get_account_by_name("Commun").id, aid)

    def test_add_and_list_transactions(self):
        aid = self.db.add_account("Commun")
        cat = self.db.get_categories()[0]
        self.db.add_transaction(aid, "2026-01-05", "CARREFOUR", -42.5, category_id=cat.id)
        self.db.add_transaction(aid, "2026-02-01", "Salaire", 2000.0, source="manuel")
        jan = self.db.list_transactions(account_id=aid, prefix="2026-01")
        self.assertEqual(len(jan), 1)
        self.assertEqual(jan[0].amount, -42.5)
        self.assertEqual(jan[0].category_id, cat.id)
        self.assertEqual(len(self.db.list_transactions(account_id=aid)), 2)

    def test_set_category_and_transfer(self):
        aid = self.db.add_account("Commun")
        pid = self.db.add_account("JEAN", "perso")
        tx = self.db.add_transaction(aid, "2026-01-10", "Virement", -100.0)
        cat = self.db.get_categories()[0]
        self.db.set_transaction_category(tx, cat.id)
        self.assertEqual(self.db.get_transaction(tx).category_id, cat.id)
        transfer = self.db.add_transfer(aid, pid, "2026-01-10", 100.0, "Virement")
        self.db.set_transaction_transfer(tx, transfer.id)
        self.assertEqual(self.db.get_transaction(tx).transfer_id, transfer.id)
        self.assertEqual(len(self.db.list_transfers()), 1)
        self.assertEqual(transfer.amount, 100.0)


if __name__ == "__main__":
    unittest.main()
