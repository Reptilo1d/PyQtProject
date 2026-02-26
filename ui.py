# ui.py
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QTableWidget,
                             QHeaderView)


class MainWindowUI(QMainWindow):
    """Класс отвечает ТОЛЬКО за отрисовку интерфейса"""

    def setup_ui(self):
        self.resize(1000, 600)

        # Основной виджет и слой
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        #КНОПКИ
        self.button_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("Обновить данные")
        self.refresh_btn.setMinimumHeight(40)
        self.refresh_btn.setStyleSheet("font-size: 14px; font-weight: bold;")

        self.button_layout.addWidget(self.refresh_btn)
        self.layout.addLayout(self.button_layout)

        #ТАБЛИЦА
        self.table = QTableWidget()

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

        # Делаем так, чтобы текст мог переноситься на новую строку (опционально)
        self.table.setWordWrap(True)

        self.layout.addWidget(self.table)