import unittest

from models.medicine import Medicine
from models.sale import Sale


class TestModels(unittest.TestCase):
    def test_medicine_to_dict(self):
        med = Medicine(
            id=1,
            name="Тестовый препарат",
            category="Категория",
            manufacturer="Производитель",
            quantity=10,
            price=123.45,
            description="Описание",
            expiry_date="2030-01-01",
        )

        data = med.to_dict()

        self.assertEqual(data["id"], 1)
        self.assertEqual(data["name"], "Тестовый препарат")
        self.assertEqual(data["category"], "Категория")
        self.assertEqual(data["manufacturer"], "Производитель")
        self.assertEqual(data["quantity"], 10)
        self.assertEqual(data["price"], 123.45)
        self.assertEqual(data["description"], "Описание")
        self.assertEqual(data["expiry_date"], "2030-01-01")

    def test_sale_to_dict(self):
        sale = Sale(
            medicine_name="Парацетамол",
            pharmacist="Иванов Алексей",
            quantity=3,
            date="2026-03-11",
        )

        data = sale.to_dict()

        self.assertEqual(data["medicine"], "Парацетамол")
        self.assertEqual(data["pharmacist"], "Иванов Алексей")
        self.assertEqual(data["quantity"], 3)
        self.assertEqual(data["date"], "2026-03-11")


if __name__ == "__main__":
    unittest.main()

