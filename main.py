# main.py
import sys
from PyQt6.QtWidgets import QApplication, QTableWidgetItem, QMessageBox

# Импортируем интерфейс и настройки из наших соседних файлов
from ui import MainWindowUI
import config

from sqlalchemy import create_engine, MetaData, Table, select


class AppLogic(MainWindowUI):
    """Класс наследует интерфейс и добавляет в него логику работы с БД"""

    def __init__(self):
        super().__init__()
        # 1. Отрисовываем интерфейс (вызов метода из ui.py)
        self.setup_ui()

        # Добавляем заголовок окна из настроек config.py
        self.setWindowTitle(f"База Данных | {config.TARGET_SCHEMA}.{config.TARGET_TABLE}")

        # 2. Подключаем нажатие кнопки к функции загрузки
        self.refresh_btn.clicked.connect(self.load_data)

        # 3. Настраиваем базу данных и сразу загружаем данные
        self.init_db()
        self.load_data()

    def init_db(self):
        """Подключается к БД и считывает структуру (Рефлексия)"""
        try:
            # Используем DATABASE_URL из config.py
            self.engine = create_engine(config.DATABASE_URL)
            self.metadata = MetaData(schema=config.TARGET_SCHEMA)

            # Авто-парсинг колонок из БД
            self.dynamic_table = Table(config.TARGET_TABLE, self.metadata, autoload_with=self.engine)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка БД", f"Не удалось подключиться:\n{e}")
            sys.exit(1)

    def load_data(self):
        """Запрашивает данные и заполняет таблицу интерфейса"""
        try:
            with self.engine.connect() as conn:
                stmt = select(self.dynamic_table)
                result = conn.execute(stmt)

                column_names = list(result.keys())
                rows = result.fetchall()

            # --- ЗАПОЛНЕНИЕ ТАБЛИЦЫ ---
            self.table.setColumnCount(len(column_names))
            self.table.setHorizontalHeaderLabels(column_names)
            self.table.setRowCount(0)

            for row_idx, row_data in enumerate(rows):
                self.table.insertRow(row_idx)
                for col_idx, value in enumerate(row_data):
                    display_text = "" if value is None else str(value)
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(display_text))

            # РЕШЕНИЕ ПРОБЛЕМЫ С ОБРЕЗАННЫМ ТЕКСТОМ (Часть 2):
            # После того как данные загружены, эта команда автоматически
            # раздвигает ширину колонок так, чтобы влез самый длинный текст в ячейке!
            self.table.resizeColumnsToContents()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке данных:\n{e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AppLogic()  # Запускаем класс с логикой (он уже включает в себя UI)
    window.show()
    sys.exit(app.exec())