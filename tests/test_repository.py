import json
import os
import tempfile
import unittest
from datetime import datetime

from repository.pharmacy_repository import PharmacyRepository


class TestPharmacyRepository(unittest.TestCase):
    def setUp(self):
        self.repo = PharmacyRepository()

        # подменяем данные, чтобы не трогать реальные файлы
        self.repo.medicines = [
            {
                "id": 1,
                "name": "Парацетамол",
                "category": "Жаропонижающее",
                "manufacturer": "PharmaCorp",
                "quantity": 10,
                "price": 50.0,
            },
            {
                "id": 2,
                "name": "Ибупрофен",
                "category": "Обезболивающее",
                "manufacturer": "MedLife",
                "quantity": 0,
                "price": 100.0,
            },
        ]

        self.repo.sales = [
            {
                "medicine": "Парацетамол",
                "pharmacist": "Иванов Алексей",
                "quantity": 2,
                "date": "2026-03-10",
            },
            {
                "medicine": "Ибупрофен",
                "pharmacist": "Петрова Мария",
                "quantity": 1,
                "date": "2026-03-11",
            },
        ]

        self.repo.pharmacists = [
            {"last_name": "Иванов", "first_name": "Алексей"},
            {"last_name": "Петрова", "first_name": "Мария"},
        ]

        # чтобы не портить реальные json-файлы
        self.repo.save_medicines = lambda: None
        self.repo.save_sales = lambda: None

    def test_get_medicines(self):
        meds = self.repo.get_medicines()
        self.assertEqual(len(meds), 2)

    def test_get_medicine_by_id_found_and_not_found(self):
        med = self.repo.get_medicine_by_id(1)
        self.assertIsNotNone(med)
        self.assertEqual(med["name"], "Парацетамол")

        not_found = self.repo.get_medicine_by_id(999)
        self.assertIsNone(not_found)

    def test_get_pharmacists(self):
        names = self.repo.get_pharmacists()
        self.assertIn("Иванов Алексей", names)
        self.assertIn("Петрова Мария", names)

    def test_search_by_name_and_in_stock(self):
        # поиск по названию
        result = self.repo.search(name="Парацетамол")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], 1)

        # только в наличии
        in_stock = self.repo.search(in_stock=True)
        self.assertEqual(len(in_stock), 1)
        self.assertEqual(in_stock[0]["id"], 1)

        # только отсутствующие
        out_of_stock = self.repo.search(in_stock=False)
        self.assertEqual(len(out_of_stock), 1)
        self.assertEqual(out_of_stock[0]["id"], 2)

    def test_make_sale_success_and_fail(self):
        # успешная продажа
        ok = self.repo.make_sale("Парацетамол", "Иванов Алексей", 3)
        self.assertTrue(ok)
        med = self.repo.get_medicine_by_id(1)
        self.assertEqual(med["quantity"], 7)
        self.assertGreaterEqual(len(self.repo.sales), 3)

        # недостаточно товара
        fail = self.repo.make_sale("Парацетамол", "Иванов Алексей", 1000)
        self.assertFalse(fail)

    def test_update_medicine(self):
        updated = self.repo.update_medicine(
            1,
            "Новый парацетамол",
            "Новая категория",
            "Новый производитель",
            5,
            77.0,
        )
        self.assertTrue(updated)
        med = self.repo.get_medicine_by_id(1)
        self.assertEqual(med["name"], "Новый парацетамол")
        self.assertEqual(med["quantity"], 5)
        self.assertEqual(med["price"], 77.0)

        # несуществующий id
        updated_false = self.repo.update_medicine(
            999, "Имя", "Категория", "Производитель", 1, 10.0
        )
        self.assertFalse(updated_false)

    def test_sales_report_filtered_by_medicine_and_date(self):
        # по периоду, включает обе продажи
        result_all = self.repo.sales_report(
            medicine="",
            date_from="2026-03-09",
            date_to="2026-03-12",
        )
        self.assertEqual(len(result_all), 2)

        # только по парацетамолу
        result_paracetamol = self.repo.sales_report(
            medicine="Парацетамол",
            date_from="2026-03-09",
            date_to="2026-03-12",
        )
        self.assertEqual(len(result_paracetamol), 1)
        self.assertEqual(result_paracetamol[0]["medicine"], "Парацетамол")

        # пустой период
        result_empty = self.repo.sales_report(
            medicine="Парацетамол",
            date_from="2026-03-01",
            date_to="2026-03-05",
        )
        self.assertEqual(len(result_empty), 0)


class TestPharmacyRepositoryIO(unittest.TestCase):
    """Тесты, которые проверяют работу с JSON-файлами (load/save)."""

    def test_save_and_load_all_entities(self):
        repo = PharmacyRepository()

        with tempfile.TemporaryDirectory() as tmpdir:
            med_path = os.path.join(tmpdir, "medicines.json")
            sales_path = os.path.join(tmpdir, "sales.json")
            pharm_path = os.path.join(tmpdir, "pharmacists.json")

            # перенастраиваем пути на временные файлы
            repo.medicine_file = med_path
            repo.sales_file = sales_path
            repo.pharmacists_file = pharm_path

            # подготавливаем данные в памяти
            repo.medicines = [
                {
                    "id": 10,
                    "name": "Тест-мед",
                    "category": "Тестовая",
                    "manufacturer": "ТестПроизводитель",
                    "quantity": 5,
                    "price": 10.0,
                }
            ]

            repo.sales = [
                {
                    "medicine": "Тест-мед",
                    "pharmacist": "Тест Фармацевт",
                    "quantity": 1,
                    "date": "2026-03-11",
                }
            ]

            repo.pharmacists = [
                {"last_name": "Тестов", "first_name": "Фармацевт"},
            ]

            # сохраняем во временные JSON-файлы
            repo.save_medicines()
            repo.save_sales()

            with open(pharm_path, "w", encoding="utf-8") as f:
                json.dump(repo.pharmacists, f, ensure_ascii=False, indent=4)

            # очищаем данные в памяти и загружаем обратно из файлов
            repo.medicines = []
            repo.sales = []
            repo.pharmacists = []

            repo.load_data()

            self.assertEqual(len(repo.medicines), 1)
            self.assertEqual(len(repo.sales), 1)
            self.assertEqual(len(repo.pharmacists), 1)
            self.assertEqual(repo.medicines[0]["name"], "Тест-мед")
            self.assertEqual(repo.sales[0]["medicine"], "Тест-мед")
            self.assertEqual(repo.pharmacists[0]["last_name"], "Тестов")


if __name__ == "__main__":
    unittest.main()

