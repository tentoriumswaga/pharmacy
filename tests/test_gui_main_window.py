import os
import tempfile
import unittest
from unittest import mock

import tkinter as tk

from gui.main_window import MainWindow


class TestMainWindow(unittest.TestCase):
    def setUp(self):
        # чтобы окна не мешали во время тестов
        self.app = MainWindow()
        self.app.root.withdraw()

        # подготавливаем тестовые данные в репозитории
        self.app.repo.medicines = [
            {
                "id": 1,
                "name": "Парацетамол",
                "category": "Жаропонижающее",
                "manufacturer": "PharmaCorp",
                "quantity": 10,
                "price": 50.0,
            }
        ]
        self.app.repo.pharmacists = [
            {"last_name": "Иванов", "first_name": "Алексей"},
        ]
        self.app.repo.sales = []

        # чтобы не писать ничего в настоящие файлы
        self.app.repo.save_medicines = lambda: None
        self.app.repo.save_sales = lambda: None

    def tearDown(self):
        # корректно уничтожаем окно
        try:
            self.app.root.destroy()
        except tk.TclError:
            pass

    @mock.patch("tkinter.messagebox.showinfo")
    def test_search_and_show_medicine_details(self, mock_info):
        # заполняем фильтр и вызываем поиск
        self.app.name_filter.delete(0, tk.END)
        self.app.name_filter.insert(0, "Парацетамол")
        self.app.stock_filter.set("Все")

        self.app.search()

        items = self.app.tree.get_children()
        self.assertEqual(len(items), 1)

        # выбираем строку и вызываем показ подробной информации
        self.app.tree.selection_set(items[0])
        self.app.show_medicine_details()

        mock_info.assert_called_once()

    @mock.patch("tkinter.messagebox.showinfo")
    @mock.patch("tkinter.messagebox.showerror")
    def test_sell_calls_repository(self, mock_error, mock_info):
        # успешная продажа
        self.app.sale_name.delete(0, tk.END)
        self.app.sale_name.insert(0, "Парацетамол")
        self.app.pharmacist.set("Иванов Алексей")
        self.app.sale_qty.delete(0, tk.END)
        self.app.sale_qty.insert(0, "2")

        with mock.patch.object(self.app.repo, "make_sale", return_value=True) as ms:
            self.app.sell()
            ms.assert_called_once()
            mock_info.assert_called_once()

        # неуспешная продажа
        mock_info.reset_mock()
        with mock.patch.object(self.app.repo, "make_sale", return_value=False):
            self.app.sell()
            mock_error.assert_called()

    @mock.patch("tkinter.messagebox.showinfo")
    @mock.patch("tkinter.messagebox.showerror")
    def test_edit_flow_with_load_and_save(self, mock_error, mock_info):
        # подготавливаем данные
        self.app.repo.medicines[0]["quantity"] = 5
        self.app.repo.medicines[0]["price"] = 99.0

        # вводим ID и загружаем
        self.app.edit_id.delete(0, tk.END)
        self.app.edit_id.insert(0, "1")
        self.app.load_medicine_for_edit()

        self.assertEqual(self.app.edit_name.get(), "Парацетамол")

        # меняем только цену
        self.app.edit_price.delete(0, tk.END)
        self.app.edit_price.insert(0, "120.5")

        self.app.edit()

        med = self.app.repo.get_medicine_by_id(1)
        self.assertEqual(med["price"], 120.5)
        self.assertEqual(med["quantity"], 5)
        mock_info.assert_called()
        mock_error.assert_not_called()

    @mock.patch("tkinter.filedialog.asksaveasfilename")
    @mock.patch("tkinter.messagebox.showinfo")
    def test_make_report_txt_format(self, mock_info, mock_save):
        # имитируем данные для отчета
        self.app.repo.sales = [
            {
                "medicine": "Парацетамол",
                "pharmacist": "Иванов Алексей",
                "quantity": 2,
                "date": "2026-03-11",
            }
        ]

        # поля фильтра
        self.app.rep_med.delete(0, tk.END)
        self.app.rep_med.insert(0, "")
        self.app.date_from.delete(0, tk.END)
        self.app.date_from.insert(0, "2026-03-10")
        self.app.date_to.delete(0, tk.END)
        self.app.date_to.insert(0, "2026-03-12")
        self.app.report_format.set("Текстовый (TXT)")

        # временный файл для сохранения
        fd, path = tempfile.mkstemp(suffix=".txt")
        os.close(fd)
        mock_save.return_value = path

        try:
            self.app.make_report()
            self.assertTrue(os.path.exists(path))
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn("Парацетамол", content)
            mock_info.assert_called_once()
        finally:
            if os.path.exists(path):
                os.remove(path)


if __name__ == "__main__":
    unittest.main()

