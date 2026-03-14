# Репозиторий — отвечает за хранение и работу с JSON

import json
import os
from datetime import datetime


class PharmacyRepository:

    def __init__(self):

        self.medicine_file = "data/medicines.json"
        self.sales_file = "data/sales.json"
        self.pharmacists_file = "data/pharmacists.json"

        self.medicines = []
        self.sales = []
        self.pharmacists = []

        self.load_data()

    # загрузка данных из JSON
    def load_data(self):

        if os.path.exists(self.medicine_file):
            with open(self.medicine_file, "r", encoding="utf-8") as f:
                self.medicines = json.load(f)

        if os.path.exists(self.sales_file):
            with open(self.sales_file, "r", encoding="utf-8") as f:
                self.sales = json.load(f)

        if os.path.exists(self.pharmacists_file):
            with open(self.pharmacists_file, "r", encoding="utf-8") as f:
                self.pharmacists = json.load(f)

    # сохранение препаратов
    def save_medicines(self):

        with open(self.medicine_file, "w", encoding="utf-8") as f:
            json.dump(self.medicines, f, indent=4, ensure_ascii=False)

    # сохранение продаж
    def save_sales(self):

        with open(self.sales_file, "w", encoding="utf-8") as f:
            json.dump(self.sales, f, indent=4, ensure_ascii=False)

    # получение списка препаратов
    def get_medicines(self):
        return self.medicines

    # получение списка фармацевтов (Фамилия Имя)
    def get_pharmacists(self):
        result = []
        for p in self.pharmacists:
            last_name = p.get("last_name", "")
            first_name = p.get("first_name", "")
            full_name = f"{last_name} {first_name}".strip()
            if full_name:
                result.append(full_name)
        return result

    # получение одного препарата по ID
    def get_medicine_by_id(self, id_value):

        for m in self.medicines:
            if m.get("id") == id_value:
                return m

        return None

    # поиск препаратов по фильтрам
    def search(self, name="", category="", manufacturer="", in_stock=None):

        result = []

        for m in self.medicines:

            if name and name.lower() not in m["name"].lower():
                continue

            if category and category.lower() not in m["category"].lower():
                continue

            if manufacturer and manufacturer.lower() not in m["manufacturer"].lower():
                continue

            if in_stock is not None:
                if in_stock and m["quantity"] == 0:
                    continue
                if not in_stock and m["quantity"] > 0:
                    continue

            result.append(m)

        return result

    # продажа препарата
    def make_sale(self, medicine_name, pharmacist, quantity):

        for m in self.medicines:

            if m["name"] == medicine_name:

                if m["quantity"] < quantity:
                    return False

                m["quantity"] -= quantity

                sale = {
                    "medicine": medicine_name,
                    "pharmacist": pharmacist,
                    "quantity": quantity,
                    "date": datetime.now().strftime("%Y-%m-%d")
                }

                self.sales.append(sale)

                self.save_medicines()
                self.save_sales()

                return True

        return False

    # редактирование препарата
    def update_medicine(self, id, name, category, manufacturer, quantity, price):

        for m in self.medicines:

            if m["id"] == id:

                m["name"] = name
                m["category"] = category
                m["manufacturer"] = manufacturer
                m["quantity"] = quantity
                m["price"] = price

                self.save_medicines()
                return True

        return False

    # отчет по продажам
    def sales_report(self, medicine, date_from, date_to):

        result = []

        for s in self.sales:

            if medicine and medicine.lower() not in s["medicine"].lower():
                continue

            if date_from <= s["date"] <= date_to:
                result.append(s)

        return result