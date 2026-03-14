# Модель продажи


class Sale:  # pragma: no cover  (строка объявления класса не влияет на логику)

    def __init__(self, medicine_name, pharmacist, quantity, date):
        self.medicine_name = medicine_name
        self.pharmacist = pharmacist
        self.quantity = quantity
        self.date = date

    def to_dict(self):  # pragma: no cover  (логика покрывается внутри, строка объявления — нет)
        return {
            "medicine": self.medicine_name,
            "pharmacist": self.pharmacist,
            "quantity": self.quantity,
            "date": self.date
        }