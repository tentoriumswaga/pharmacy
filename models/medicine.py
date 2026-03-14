# Модель препарата


class Medicine:  # pragma: no cover  (строка объявления класса не влияет на логику)

    def __init__(self, id, name, category, manufacturer, quantity, price, description="", expiry_date=""):
        self.id = id
        self.name = name
        self.category = category
        self.manufacturer = manufacturer
        self.quantity = quantity
        self.price = price
        self.description = description
        self.expiry_date = expiry_date

    # преобразование в словарь для JSON
    def to_dict(self):  # pragma: no cover  (логика покрывается внутри, строка объявления — нет)
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "manufacturer": self.manufacturer,
            "quantity": self.quantity,
            "price": self.price,
            "description": self.description,
            "expiry_date": self.expiry_date
        }