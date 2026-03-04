# ui.py
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QTableWidget,
                             QHeaderView, QStatusBar)


class MainWindowUI(QMainWindow):
    def setup_ui(self):
        self.resize(1000, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # --- КНОПКИ ---
        self.button_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("Обновить данные")
        self.refresh_btn.setMinimumHeight(40)
        self.refresh_btn.setStyleSheet("font-size: 14px; font-weight: bold;")

        self.button_layout.addWidget(self.refresh_btn)
        self.layout.addLayout(self.button_layout)

        # --- ТАБЛИЦА ---
        self.table = QTableWidget()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.setWordWrap(True)
        self.layout.addWidget(self.table)

        # --- СТРОКА СОСТОЯНИЯ (НОВОЕ) ---
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готово к работе", 5000)