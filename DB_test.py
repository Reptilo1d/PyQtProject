import sys
from urllib.parse import quote_plus

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
                             QMessageBox, QHeaderView)
from sqlalchemy import create_engine, Column, String, BigInteger, Text
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. НАСТРОЙКИ ПОДКЛЮЧЕНИЯ

DB_HOST = "localhost"
DB_PORT = "5432"
DB_USER = "postgres"
DB_NAME = "postgres"  # Имя базы данных

# Ваш пароль
RAW_PASSWORD = "1"
DB_PASS = quote_plus(RAW_PASSWORD)

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

Base = declarative_base()


# 2. МОДЕЛЬ ДАННЫХ

class UserData(Base):
    __tablename__ = 'user_data'
    __table_args__ = {"schema": "todolist"}

    id = Column(BigInteger, primary_key=True)
    username = Column(Text)
    email = Column(Text)
    password = Column(Text)


# 3. ГРАФ ИНТЕРФЕЙС

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DBTest")
        self.resize(800, 500)

        self.init_db()

        # Основной виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Основной вертикальный слой
        layout = QVBoxLayout(central_widget)

        # --- БЛОК КНОПОК (ВЕРХНЯЯ ЧАСТЬ) ---
        button_layout = QHBoxLayout()

        self.refresh_btn = QPushButton("Обновить таблицу")
        self.refresh_btn.setMinimumHeight(40)  # Делаем кнопку чуть больше
        self.refresh_btn.setStyleSheet("font-size: 14px; font-weight: bold; background-color: #f0f0f0;")
        # Подключаем нажатие кнопки к функции загрузки данных
        self.refresh_btn.clicked.connect(self.load_data)

        button_layout.addWidget(self.refresh_btn)

        # Добавляем блок кнопок в основной слой
        layout.addLayout(button_layout)

        # --- ТАБЛИЦА ---
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Username", "Email", "Password"])

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        layout.addWidget(self.table)

        # Первичная загрузка данных
        self.load_data()

    def init_db(self):
        """Подключение к БД"""
        try:
            self.engine = create_engine(DATABASE_URL)
            self.Session = sessionmaker(bind=self.engine)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось подключиться к БД:\n{e}")
            sys.exit(1)

    def load_data(self):
        """Запрос данных из БД и обновление таблицы"""
        session = self.Session()
        try:
            # Делаем свежий запрос
            users = session.query(UserData).order_by(UserData.id).all()

            # Очищаем таблицу перед новой отрисовкой
            self.table.setRowCount(0)

            # Заполняем заново
            for row_idx, user in enumerate(users):
                self.table.insertRow(row_idx)

                # Обработка NULL значений
                val_id = str(user.id)
                val_username = str(user.username) if user.username is not None else ""
                val_email = str(user.email) if user.email is not None else ""
                val_password = str(user.password) if user.password is not None else ""

                self.table.setItem(row_idx, 0, QTableWidgetItem(val_id))
                self.table.setItem(row_idx, 1, QTableWidgetItem(val_username))
                self.table.setItem(row_idx, 2, QTableWidgetItem(val_email))
                self.table.setItem(row_idx, 3, QTableWidgetItem(val_password))

            # (Опционально) Можно вывести в консоль, что обновление прошло
            print(f"Данные обновлены. Загружено строк: {len(users)}")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при обновлении данных:\n{e}")
        finally:
            # Важно закрывать сессию, чтобы не висели старые транзакции
            session.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())