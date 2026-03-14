import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from repository.pharmacy_repository import PharmacyRepository


class MainWindow:

    def __init__(self):

        self.repo = PharmacyRepository()

        self.root = tk.Tk()
        self.root.title("Аптечная информационная система")
        self.root.geometry("900x600")

        tabs = ttk.Notebook(self.root)

        self.view_tab = ttk.Frame(tabs)
        self.sale_tab = ttk.Frame(tabs)
        self.edit_tab = ttk.Frame(tabs)
        self.report_tab = ttk.Frame(tabs)

        tabs.add(self.view_tab, text="Препараты")
        tabs.add(self.sale_tab, text="Продажа")
        tabs.add(self.edit_tab, text="Редактирование")
        tabs.add(self.report_tab, text="Отчет")

        tabs.pack(expand=1, fill="both")

        self.create_view_tab()
        self.create_sale_tab()
        self.create_edit_tab()
        self.create_report_tab()

    # -------------------------------
    # вкладка просмотра и поиска
    # -------------------------------

    def create_view_tab(self):

        frame = self.view_tab

        tk.Label(frame, text="Название").grid(row=0, column=0)
        tk.Label(frame, text="Категория").grid(row=0, column=1)
        tk.Label(frame, text="Производитель").grid(row=0, column=2)
        tk.Label(frame, text="Наличие").grid(row=0, column=3)
        tk.Label(frame, text="Сортировка").grid(row=0, column=4)

        self.name_filter = tk.Entry(frame)
        self.category_filter = tk.Entry(frame)
        self.man_filter = tk.Entry(frame)

        self.name_filter.grid(row=1, column=0, padx=2, pady=2, sticky="ew")
        self.category_filter.grid(row=1, column=1, padx=2, pady=2, sticky="ew")
        self.man_filter.grid(row=1, column=2, padx=2, pady=2, sticky="ew")

        # фильтр по наличию
        self.stock_filter = ttk.Combobox(
            frame,
            values=["Все", "Только в наличии", "Нет в наличии"],
            state="readonly"
        )
        self.stock_filter.current(0)
        self.stock_filter.grid(row=1, column=3, padx=2, pady=2, sticky="ew")

        # выбор сортировки
        self.sort_var = tk.StringVar(value="name")
        self.sort_combo = ttk.Combobox(
            frame,
            textvariable=self.sort_var,
            values=["Название", "Количество"],
            state="readonly"
        )
        self.sort_combo.current(0)
        self.sort_combo.grid(row=1, column=4, padx=2, pady=2, sticky="ew")

        tk.Button(frame, text="Поиск", command=self.search).grid(row=1, column=5, padx=4)

        self.tree = ttk.Treeview(frame, columns=("id", "name", "cat", "man", "qty", "price"), show="headings")

        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Название")
        self.tree.heading("cat", text="Категория")
        self.tree.heading("man", text="Производитель")
        self.tree.heading("qty", text="Количество")
        self.tree.heading("price", text="Цена")

        self.tree.grid(row=2, column=0, columnspan=6, sticky="nsew")

        # обработчик двойного щелчка для подробной информации
        self.tree.bind("<Double-1>", self.show_medicine_details)

        # настройка растяжения столбцов
        frame.grid_rowconfigure(2, weight=1)
        for col in range(6):
            frame.grid_columnconfigure(col, weight=1)

        self.refresh_table(self.repo.get_medicines())

    def refresh_table(self, data):

        for row in self.tree.get_children():
            self.tree.delete(row)

        for m in data:

            self.tree.insert("", "end", values=(
                m["id"],
                m["name"],
                m["category"],
                m["manufacturer"],
                m["quantity"],
                m["price"]
            ))

    def search(self):

        # преобразуем фильтр по наличию
        stock_value = self.stock_filter.get()
        if stock_value == "Только в наличии":
            in_stock = True
        elif stock_value == "Нет в наличии":
            in_stock = False
        else:
            in_stock = None

        data = self.repo.search(
            self.name_filter.get(),
            self.category_filter.get(),
            self.man_filter.get(),
            in_stock=in_stock
        )

        # сортировка результатов
        sort_choice = self.sort_var.get()
        if sort_choice == "Название":
            data = sorted(data, key=lambda m: m.get("name", ""))
        elif sort_choice == "Количество":
            data = sorted(data, key=lambda m: m.get("quantity", 0), reverse=True)

        self.refresh_table(data)

    def show_medicine_details(self, event=None):

        selected = self.tree.selection()
        if not selected:
            return

        item = self.tree.item(selected[0])
        values = item.get("values", [])
        if not values:
            return

        med_id = values[0]
        medicine = self.repo.get_medicine_by_id(med_id)
        if not medicine:
            messagebox.showerror("Ошибка", "Не удалось найти данные о препарате")
            return

        # формирование текста с подробной информацией
        description = medicine.get("description", "—")
        manufacturer = medicine.get("manufacturer", "—")
        expiry = medicine.get("expiry_date", "—")
        quantity = medicine.get("quantity", 0)

        detail_text = (
            f'Название: {medicine.get("name", "")}\n'
            f'Категория: {medicine.get("category", "")}\n'
            f'Производитель: {manufacturer}\n'
            f'Описание: {description}\n'
            f'Срок годности: {expiry}\n'
            f'Количество на складе: {quantity}'
        )

        messagebox.showinfo("Информация о препарате", detail_text)

    # -------------------------------
    # вкладка продажи
    # -------------------------------

    def create_sale_tab(self):

        tk.Label(self.sale_tab, text="Название препарата").pack()
        self.sale_name = tk.Entry(self.sale_tab)
        self.sale_name.pack()

        tk.Label(self.sale_tab, text="Фармацевт").pack()
        self.pharmacist = ttk.Combobox(
            self.sale_tab,
            values=self.repo.get_pharmacists()
        )
        self.pharmacist.pack()

        tk.Label(self.sale_tab, text="Количество").pack()
        self.sale_qty = tk.Entry(self.sale_tab)
        self.sale_qty.pack()

        tk.Button(self.sale_tab, text="Продать", command=self.sell).pack(pady=10)

    def sell(self):

        success = self.repo.make_sale(
            self.sale_name.get(),
            self.pharmacist.get(),
            int(self.sale_qty.get())
        )

        if success:
            messagebox.showinfo("Успех", "Продажа выполнена")
        else:
            messagebox.showerror("Ошибка", "Недостаточно товара")

    # -------------------------------
    # редактирование препарата
    # -------------------------------

    def create_edit_tab(self):

        tk.Label(self.edit_tab, text="ID").pack()
        self.edit_id = tk.Entry(self.edit_tab)
        self.edit_id.pack()

        tk.Button(self.edit_tab, text="Загрузить по ID", command=self.load_medicine_for_edit).pack(pady=5)

        tk.Label(self.edit_tab, text="Название").pack()
        self.edit_name = tk.Entry(self.edit_tab)
        self.edit_name.pack()

        tk.Label(self.edit_tab, text="Категория").pack()
        self.edit_category = tk.Entry(self.edit_tab)
        self.edit_category.pack()

        tk.Label(self.edit_tab, text="Производитель").pack()
        self.edit_man = tk.Entry(self.edit_tab)
        self.edit_man.pack()

        tk.Label(self.edit_tab, text="Количество").pack()
        self.edit_qty = tk.Entry(self.edit_tab)
        self.edit_qty.pack()

        tk.Label(self.edit_tab, text="Цена").pack()
        self.edit_price = tk.Entry(self.edit_tab)
        self.edit_price.pack()

        tk.Button(self.edit_tab, text="Сохранить", command=self.edit).pack(pady=10)

    def load_medicine_for_edit(self):

        try:
            med_id = int(self.edit_id.get())
        except ValueError:
            messagebox.showerror("Ошибка", "ID должен быть числом")
            return

        medicine = self.repo.get_medicine_by_id(med_id)
        if not medicine:
            messagebox.showerror("Ошибка", "Препарат с таким ID не найден")
            return

        # автозаполнение текущими данными
        self.edit_name.delete(0, tk.END)
        self.edit_name.insert(0, medicine.get("name", ""))

        self.edit_category.delete(0, tk.END)
        self.edit_category.insert(0, medicine.get("category", ""))

        self.edit_man.delete(0, tk.END)
        self.edit_man.insert(0, medicine.get("manufacturer", ""))

        self.edit_qty.delete(0, tk.END)
        self.edit_qty.insert(0, str(medicine.get("quantity", 0)))

        self.edit_price.delete(0, tk.END)
        self.edit_price.insert(0, str(medicine.get("price", 0)))

    def edit(self):

        try:
            med_id = int(self.edit_id.get())
        except ValueError:
            messagebox.showerror("Ошибка", "ID должен быть числом")
            return

        medicine = self.repo.get_medicine_by_id(med_id)
        if not medicine:
            messagebox.showerror("Ошибка", "Препарат с таким ID не найден")
            return

        # если поле пустое — оставляем старое значение
        name = self.edit_name.get() or medicine.get("name", "")
        category = self.edit_category.get() or medicine.get("category", "")
        manufacturer = self.edit_man.get() or medicine.get("manufacturer", "")

        qty_text = self.edit_qty.get()
        price_text = self.edit_price.get()

        try:
            quantity = int(qty_text) if qty_text else int(medicine.get("quantity", 0))
        except ValueError:
            messagebox.showerror("Ошибка", "Количество должно быть целым числом")
            return

        try:
            price = float(price_text) if price_text else float(medicine.get("price", 0))
        except ValueError:
            messagebox.showerror("Ошибка", "Цена должна быть числом")
            return

        self.repo.update_medicine(
            med_id,
            name,
            category,
            manufacturer,
            quantity,
            price
        )

        messagebox.showinfo("Готово", "Данные обновлены")

    # -------------------------------
    # отчет
    # -------------------------------

    def create_report_tab(self):

        tk.Label(self.report_tab, text="Препарат").pack()
        self.rep_med = tk.Entry(self.report_tab)
        self.rep_med.pack()

        tk.Label(self.report_tab, text="Дата с").pack()
        self.date_from = tk.Entry(self.report_tab)
        self.date_from.pack()

        tk.Label(self.report_tab, text="Дата по").pack()
        self.date_to = tk.Entry(self.report_tab)
        self.date_to.pack()

        # выбор формата отчета
        tk.Label(self.report_tab, text="Формат отчета").pack()
        self.report_format = ttk.Combobox(
            self.report_tab,
            values=["Текстовый (TXT)", "Таблица (CSV)", "JSON"],
            state="readonly"
        )
        self.report_format.current(0)
        self.report_format.pack()

        tk.Button(self.report_tab, text="Сформировать", command=self.make_report).pack(pady=10)

    def make_report(self):

        data = self.repo.sales_report(
            self.rep_med.get(),
            self.date_from.get(),
            self.date_to.get()
        )

        # определяем формат и расширение файла
        fmt = self.report_format.get()
        if fmt == "Таблица (CSV)":
            def_ext = ".csv"
            filetypes = [("CSV файлы", "*.csv"), ("Все файлы", "*.*")]
        elif fmt == "JSON":
            def_ext = ".json"
            filetypes = [("JSON файлы", "*.json"), ("Все файлы", "*.*")]
        else:
            def_ext = ".txt"
            filetypes = [("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]

        file = filedialog.asksaveasfilename(defaultextension=def_ext, filetypes=filetypes)

        if not file:
            return

        # экспорт в выбранный формат
        if fmt == "Таблица (CSV)":
            import csv
            with open(file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow(["Дата", "Препарат", "Фармацевт", "Количество"])
                for s in data:
                    writer.writerow([s.get("date", ""), s.get("medicine", ""), s.get("pharmacist", ""), s.get("quantity", "")])
        elif fmt == "JSON":
            import json
            with open(file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        else:
            with open(file, "w", encoding="utf-8") as f:
                for s in data:
                    line = f'{s["date"]} | {s["medicine"]} | {s["pharmacist"]} | {s["quantity"]}\n'
                    f.write(line)

        messagebox.showinfo("Готово", "Отчет сохранен")

    def run(self):
        self.root.mainloop()