import unittest

from budget_app import categorizer
from budget_app.db import Database


class TestCategorizer(unittest.TestCase):
    def setUp(self):
        self.db = Database(":memory:")

    def tearDown(self):
        self.db.close()

    def test_normalize_strips_accents_and_case(self):
        self.assertEqual(categorizer.normalize("Électricité EDF!"), "electricite edf")

    def test_auto_categorize_keyword(self):
        cid = categorizer.auto_categorize(self.db, "CARREFOUR MARKET PARIS")
        self.assertEqual(self.db.get_category(cid).name, "Alimentation")

    def test_auto_categorize_no_match(self):
        self.assertIsNone(categorizer.auto_categorize(self.db, "zzzqwx unknown stuff"))

    def test_learn_adds_keyword(self):
        cat = next(c for c in self.db.get_categories() if c.name == "Loisirs")
        categorizer.learn(self.db, "Magasin de jeux VIDEO GAMES", cat.id)
        cid = categorizer.auto_categorize(self.db, "chez VIDEO GAMES shop")
        self.assertEqual(cid, cat.id)


if __name__ == "__main__":
    unittest.main()
