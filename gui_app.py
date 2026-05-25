import sys
import os
from typing import List
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QTextEdit, QFileDialog, QMessageBox
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from ASCII_converter import ASCIIConverter
from image_processor import ImageProcessor
from webcam_ascii import WebcamASCII


class ASCIIAppGUI(QMainWindow):
    """Главное окно графического интерфейса ASCII Art Studio."""

    def __init__(self) -> None:
        """Инициализирует GUI, модули обработки и настраивает стили."""
        super().__init__()
        self.setWindowTitle("ASCII Art Studio")
        self.setFixedSize(550, 450)

        self.processor: ImageProcessor = ImageProcessor()
        self.converter: ASCIIConverter = ASCIIConverter()

        self.input_path: str = ""
        self.custom_trigger: str = "➕ Выбрать свой чарсет из файла..."
        self.charsets: List[str] = ["standard", "detailed", "blocks", "simple", self.custom_trigger]
        self.custom_charset_data: str = ""

        self._apply_dark_theme()
        self._init_ui()

    def _apply_dark_theme(self) -> None:
        """Применяет темную цветовую тему QSS к виджетам окна."""
        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e24; }
            QLabel { color: #e2e8f0; font-size: 13px; }
            QLineEdit { background-color: #2d2d38; color: #ffffff; border: 1px solid #4a4a5a; border-radius: 6px; padding-left: 10px; font-size: 13px; }
            QComboBox { background-color: #2d2d38; color: #ffffff; border: 1px solid #4a4a5a; border-radius: 6px; padding-left: 8px; font-size: 13px; }
            QComboBox::drop-down { border: 0px; }
            QComboBox QAbstractItemView { background-color: #2d2d38; color: #ffffff; selection-background-color: #5856d6; border: 1px solid #4a4a5a; }
            QPushButton { background-color: #3a3a4c; color: #ffffff; border: none; border-radius: 6px; font-weight: bold; font-size: 13px; }
            QPushButton:hover { background-color: #4e4e66; }
        """)

    def _init_ui(self) -> None:
        """Создает элементы управления и настраивает их расположение."""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(30, 25, 30, 25)
        main_layout.setSpacing(18)

        file_label = QLabel("Исходное изображение:")
        file_label.setStyleSheet("font-weight: bold; color: #a1a1aa;")
        main_layout.addWidget(file_label)

        file_layout = QHBoxLayout()
        self.file_entry = QLineEdit()
        self.file_entry.setPlaceholderText("Выберите PNG файл для конвертации...")
        self.file_entry.setReadOnly(True)
        self.file_entry.setFixedHeight(38)

        browse_btn = QPushButton("Обзор")
        browse_btn.setFixedHeight(38)
        browse_btn.setFixedWidth(100)
        browse_btn.setStyleSheet("QPushButton { background-color: #4f46e5; } QPushButton:hover { background-color: #4338ca; }")
        browse_btn.clicked.connect(self._browse_file)

        file_layout.addWidget(self.file_entry)
        file_layout.addWidget(browse_btn)
        main_layout.addLayout(file_layout)

        settings_panel = QWidget()
        settings_panel.setStyleSheet("QWidget { background-color: #25252f; border-radius: 8px; } QLabel { background: transparent; }")
        settings_layout = QVBoxLayout(settings_panel)
        settings_layout.setContentsMargins(18, 15, 18, 15)

        settings_title = QLabel("Настройки конвертации")
        settings_title.setStyleSheet("font-weight: bold; color: #818cf8; font-size: 14px;")
        settings_layout.addWidget(settings_title)

        combo_layout = QHBoxLayout()
        combo_label = QLabel("Набор символов:")
        combo_label.setStyleSheet("color: #d4d4d8;")

        self.charset_combo = QComboBox()
        self.charset_combo.addItems(self.charsets)
        self.charset_combo.setFixedHeight(34)
        self.charset_combo.setFixedWidth(240)
        self.charset_combo.currentIndexChanged.connect(self._on_charset_changed)

        combo_layout.addWidget(combo_label)
        combo_layout.addWidget(self.charset_combo)
        combo_layout.addStretch()
        settings_layout.addLayout(combo_layout)

        main_layout.addWidget(settings_panel)

        actions_label = QLabel("Доступные действия:")
        actions_label.setStyleSheet("font-weight: bold; color: #a1a1aa;")
        main_layout.addWidget(actions_label)

        img_buttons_layout = QHBoxLayout()

        window_btn = QPushButton("Показать в окне")
        window_btn.setFixedHeight(42)
        window_btn.clicked.connect(self._convert_to_window)

        file_save_btn = QPushButton("Сохранить в файл")
        file_save_btn.setFixedHeight(42)
        file_save_btn.setStyleSheet("QPushButton { background-color: #059669; } QPushButton:hover { background-color: #047857; }")
        file_save_btn.clicked.connect(self._convert_to_file)

        img_buttons_layout.addWidget(window_btn)
        img_buttons_layout.addWidget(file_save_btn)
        main_layout.addLayout(img_buttons_layout)

        self.webcam_btn = QPushButton(" Запустить веб-камеру")
        self.webcam_btn.setFixedHeight(48)
        self.webcam_btn.setStyleSheet("QPushButton { background-color: #7c3aed; font-size: 14px; } QPushButton:hover { background-color: #6d28d9; }")
        self.webcam_btn.clicked.connect(self._start_webcam)
        main_layout.addWidget(self.webcam_btn)

    def _browse_file(self) -> None:
        """Открывает диалог для выбора файла изображения."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", "", "PNG Files (*.png)")
        if file_path:
            self.input_path = file_path
            self.file_entry.setText(file_path)

    def _on_charset_changed(self, index: int) -> None:
        """Обрабатывает выбор кастомного набора символов из текстового файла."""
        choice = self.charset_combo.itemText(index)
        if choice == self.custom_trigger:
            file_path, _ = QFileDialog.getOpenFileName(self, "Открыть набор символов", "", "Text Files (*.txt);;All Files (*)")
            if file_path:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                    if content:
                        self.custom_charset_data = content
                        QMessageBox.information(self, "Успех", f"Загружен кастомный набор ({len(content)} симв.)")
                    else:
                        raise ValueError("Файл пустой")
                except Exception as e:
                    QMessageBox.warning(self, "Ошибка файла", f"Не удалось прочитать файл:\n{e}")
                    self.charset_combo.setCurrentIndex(0)
            else:
                self.charset_combo.setCurrentIndex(0)

    def _get_active_charset(self) -> str:
        """Возвращает строку текущего активного набора символов."""
        choice = self.charset_combo.currentText()
        if choice == self.custom_trigger:
            return self.custom_charset_data if self.custom_charset_data else "@%#*+=-:. "
        return choice

    def _process_image_core(self) -> str:
        """Выполняет загрузку, ресайз и генерацию текста для выбранного изображения."""
        if not self.input_path:
            raise ValueError("Сначала выберите входной PNG файл.")

        image = self.processor.load_image(self.input_path)
        resized = self.processor.resize_image(image, width=100)

        choice = self.charset_combo.currentText()
        charset_data = self._get_active_charset()

        if choice == self.custom_trigger:
            ascii_lines = []
            for y in range(resized.height):
                line = ""
                for x in range(resized.width):
                    brightness = resized.getpixel((x, y))
                    line += self.converter.pixel_to_char(brightness, charset_data)
                ascii_lines.append(line)
            return "\n".join(ascii_lines)

        return self.converter.convert_to_ascii(resized, choice)

    def _convert_to_window(self) -> None:
        """Конвертирует изображение и показывает результат в новом окне просмотра."""
        try:
            ascii_art = self._process_image_core()

            self.view_window = QMainWindow(self)
            self.view_window.setWindowTitle("Просмотр ASCII Арта")
            self.view_window.resize(750, 550)
            self.view_window.setStyleSheet("background-color: #1a1a1a;")

            text_area = QTextEdit()
            text_area.setReadOnly(True)
            text_area.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
            text_area.setStyleSheet("QTextEdit { background-color: #111111; color: #ffffff; border: none; padding: 10px; }")

            font = QFont("Courier New", 10)
            text_area.setFont(font)
            text_area.setPlainText(ascii_art)

            self.view_window.setCentralWidget(text_area)
            self.view_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сконвертировать:\n{e}")

    def _convert_to_file(self) -> None:
        """Конвертирует изображение и сохраняет текстовый результат в файл."""
        try:
            ascii_art = self._process_image_core()
            output_path, _ = QFileDialog.getSaveFileName(self, "Сохранить ASCII Арт", "", "Text Files (*.txt)")
            if output_path:
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(ascii_art)
                QMessageBox.information(self, "Успех", "Файл успешно сохранен!")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить:\n{e}")

    def _start_webcam(self) -> None:
        """Запускает видеопоток с веб-камеры во временном окне."""
        try:
            choice = self.charset_combo.currentText()

            if choice == self.custom_trigger:
                temp_path = "temp_charset.txt"
                with open(temp_path, "w", encoding="utf-8") as f:
                    f.write(self.custom_charset_data)
                charset_param = temp_path
            else:
                charset_param = choice

            self.hide()
            cam = WebcamASCII(width=300, charset=charset_param)
            cam.run()
            self.show()

            if choice == self.custom_trigger and os.path.exists("temp_charset.txt"):
                os.remove("temp_charset.txt")

        except Exception as e:
            self.show()
            QMessageBox.critical(self, "Ошибка", f"Ошибка запуска веб-камеры:\n{e}")