import sys
from PyQt6.QtWidgets import QApplication, QTableWidgetItem, QMessageBox
from PyQt6.QtCore import Qt

from sqlalchemy import create_engine, MetaData, Table, select, update

from ui import MainWindowUI
import config


class AppLogic(MainWindowUI):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setWindowTitle(f"База Данных | {config.TARGET_SCHEMA}.{config.TARGET_TABLE}")

        self.refresh_btn.clicked.connect(self.load_data)
        self.table.cellChanged.connect(self.update_record)

        self.pk_name = None
        self.col_names = []

        self.init_db()
        self.load_data()

    def init_db(self):
        """Инициализация подключения к БД и рефлексия таблицы."""
        try:
            self.engine = create_engine(config.DATABASE_URL)
            self.metadata = MetaData(schema=config.TARGET_SCHEMA)
            self.dynamic_table = Table(config.TARGET_TABLE, self.metadata, autoload_with=self.engine)

            # Автоматическое определение Primary Key
            pk_columns = [key.name for key in self.dynamic_table.primary_key]
            if pk_columns:
                self.pk_name = pk_columns[0]
            else:
                QMessageBox.warning(self, "Внимание", "В таблице нет Primary Key. Сохранение может работать некорректно.")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка БД", f"Не удалось подключиться к БД:\n{e}")
            sys.exit(1)

    def load_data(self):
        """Чтение данных из БД с сортировкой и отрисовка в QTableWidget."""
        try:
            # Блокируем сигналы таблицы, чтобы заполнение не триггерило update_record
            self.table.blockSignals(True)

            with self.engine.connect() as conn:
                stmt = select(self.dynamic_table)

                if self.pk_name:
                    stmt = stmt.order_by(self.dynamic_table.c[self.pk_name].asc())

                result = conn.execute(stmt)
                self.col_names = list(result.keys())
                rows = result.fetchall()

            # Настройка структуры таблицы в UI
            self.table.setColumnCount(len(self.col_names))
            self.table.setHorizontalHeaderLabels(self.col_names)
            self.table.setRowCount(0)

            # Заполнение данных
            for row_idx, row_data in enumerate(rows):
                self.table.insertRow(row_idx)
                for col_idx, value in enumerate(row_data):
                    display_text = "" if value is None else str(value)
                    item = QTableWidgetItem(display_text)

                    # Делаем колонку PK доступной только для чтения (Read-Only)
                    if self.col_names[col_idx] == self.pk_name:
                        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                        item.setBackground(Qt.GlobalColor.lightGray)

                    self.table.setItem(row_idx, col_idx, item)

            self.table.resizeColumnsToContents()
            self.status_bar.showMessage("Данные загружены", 3000)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке данных:\n{e}")
            print(f"Load error: {e}")
        finally:
            self.table.blockSignals(False)

    def update_record(self, row, col):
        """Обработчик изменения данных в ячейке. Формирует и выполняет UPDATE запрос."""
        if not self.pk_name:
            QMessageBox.warning(self, "Ошибка", "Невозможно сохранить: нет Primary Key.")
            return

        try:
            col_name = self.col_names[col]
            new_value = self.table.item(row, col).text()

            # Преобразуем пустые строки в NULL для корректной работы с БД
            if new_value.strip() == "":
                new_value = None

            # Получаем значение PK для текущей строки
            pk_col_idx = self.col_names.index(self.pk_name)
            pk_value_str = self.table.item(row, pk_col_idx).text()

            # Безопасный каст типа PK (int / str)
            try:
                pk_value = int(pk_value_str)
            except ValueError:
                pk_value = pk_value_str

            # Подготовка и выполнение UPDATE запроса
            stmt = update(self.dynamic_table).where(
                self.dynamic_table.c[self.pk_name] == pk_value
            ).values({col_name: new_value})

            with self.engine.connect() as conn:
                result = conn.execute(stmt)
                conn.commit()

                if result.rowcount == 0:
                    raise Exception("Запись не найдена в базе. Обновлено 0 строк.")

            self.status_bar.setStyleSheet("color: green; font-weight: bold;")
            self.status_bar.showMessage(f"Сохранено: {col_name} -> {new_value}", 3000)

        except Exception as e:
            self.status_bar.setStyleSheet("color: red; font-weight: bold;")
            self.status_bar.showMessage("Ошибка сохранения!", 5000)
            QMessageBox.critical(self, "Ошибка БД", f"Не удалось сохранить данные:\n{e}")

            # Откатываем визуальные изменения, перезапрашивая данные
            self.table.blockSignals(True)
            self.load_data()
            self.table.blockSignals(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AppLogic()
    window.show()
    sys.exit(app.exec())