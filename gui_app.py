import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QComboBox, QTextEdit,
    QFileDialog, QMessageBox
)
from PyQt6.QtGui import QFont

from ASCII_converter import ASCIIConverter
from image_processor import ImageProcessor
from webcam_ascii import WebcamASCII


class ASCIIAppGUI(QMainWindow):
    """Главное окно графического интерфейса приложения ASCII Art."""

    def __init__(self) -> None:
        """Инициализирует GUI и все необходимые компоненты."""
        super().__init__()
        self.setWindowTitle("ASCII Art")
        self.setFixedSize(500, 400)

        self.processor = ImageProcessor()
        self.converter = ASCIIConverter()

        self.input_path = ""
        self.custom_trigger = "свой файл..."
        self.charsets = ["standard", "detailed", "blocks",
                         "simple", self.custom_trigger]
        self.custom_charset_data = ""

        self._apply_style()
        self._init_ui()

    def _apply_style(self) -> None:
        """Применяет белую пастельно-розовую тему к интерфейсу."""
        self.setStyleSheet("""
            QMainWindow { background-color: #faf0f0; }
            QLabel { color: #a06c7a; font-size: 12px; }
            QLineEdit { background-color: white; color: #6d4c5c;
                border: 1px solid #f0c0c0; border-radius: 8px;
                padding-left: 8px; }
            QComboBox { background-color: white; color: #6d4c5c;
                border: 1px solid #f0c0c0; border-radius: 8px;
                padding-left: 6px; }
            QPushButton { background-color: #f0c0c0; color: #6d4c5c;
                border: none; border-radius: 12px; padding: 6px; }
            QPushButton:hover { background-color: #e8a8a8; }
        """)

    def _init_ui(self) -> None:
        """Создаёт и размещает все элементы управления."""
        widget = QWidget()
        self.setCentralWidget(widget)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(12)

        self.file_entry = QLineEdit()
        self.file_entry.setPlaceholderText("путь к изображению...")
        self.file_entry.setReadOnly(True)

        browse_btn = QPushButton("открыть")
        browse_btn.clicked.connect(self._browse_file)

        file_row = QHBoxLayout()
        file_row.addWidget(self.file_entry)
        file_row.addWidget(browse_btn)
        layout.addLayout(file_row)

        self.charset_combo = QComboBox()
        self.charset_combo.addItems(self.charsets)
        self.charset_combo.currentIndexChanged.connect(
            self._on_charset_changed)
        layout.addWidget(self.charset_combo)

        window_btn = QPushButton("показать")
        window_btn.clicked.connect(self._convert_to_window)
        layout.addWidget(window_btn)

        save_btn = QPushButton("сохранить")
        save_btn.clicked.connect(self._convert_to_file)
        layout.addWidget(save_btn)

        self.webcam_btn = QPushButton("веб-камера")
        self.webcam_btn.clicked.connect(self._start_webcam)
        layout.addWidget(self.webcam_btn)

    def _browse_file(self) -> None:
        """Открывает диалог выбора PNG-файла."""
        path, _ = QFileDialog.getOpenFileName(
            self, "", "", "PNG Files (*.png)")
        if path:
            self.input_path = path
            self.file_entry.setText(path)

    def _on_charset_changed(self, index: int) -> None:
        """Обрабатывает смену набора символов,
        включая загрузку кастомного.

        Args:
            index: Индекс выбранного элемента.
        """
        if self.charset_combo.itemText(index) == self.custom_trigger:
            path, _ = QFileDialog.getOpenFileName(
                self, "", "", "Text Files (*.txt)")
            if path:
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                    if content:
                        self.custom_charset_data = content
                        QMessageBox.information(
                            self, "", f"Загружено {len(content)} символов")
                    else:
                        raise ValueError()
                except Exception:
                    QMessageBox.warning(self, "", "Ошибка загрузки")
                    self.charset_combo.setCurrentIndex(0)
            else:
                self.charset_combo.setCurrentIndex(0)

    def _get_active_charset(self) -> str:
        """Возвращает текущий активный набор символов.

        Returns:
            Строка с символами для конвертации.
        """
        choice = self.charset_combo.currentText()
        if choice == self.custom_trigger:
            return (self.custom_charset_data if self.custom_charset_data
                    else "@%#*+=-:. ")
        return choice

    def _process_image_core(self) -> str:
        """Выполняет загрузку, ресайз и конвертацию изображения в ASCII.

        Returns:
            Многострочная строка с ASCII-артом.

        Raises:
            ValueError: Если не выбрано изображение.
        """
        if not self.input_path:
            raise ValueError("Выберите изображение")

        img = self.processor.load_image(self.input_path)
        resized = self.processor.resize_image(img, width=100)
        charset = self._get_active_charset()

        if self.charset_combo.currentText() == self.custom_trigger:
            lines = []
            for y in range(resized.height):
                line = ""
                for x in range(resized.width):
                    line += self.converter.pixel_to_char(
                        resized.getpixel((x, y)), charset)
                lines.append(line)
            return "\n".join(lines)

        return self.converter.convert_to_ascii(resized, charset)

    def _convert_to_window(self) -> None:
        """Конвертирует изображение и показывает результат в новом окне."""
        try:
            art = self._process_image_core()

            self.view = QMainWindow(self)
            self.view.setWindowTitle("ASCII")
            self.view.resize(700, 500)
            self.view.setStyleSheet("background-color: #faf0f0;")

            text = QTextEdit()
            text.setReadOnly(True)
            text.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
            text.setStyleSheet(
                "QTextEdit { background-color: white; color: #6d4c5c; "
                "border: none; padding: 8px; }")
            text.setFont(QFont("Courier New", 10))
            text.setPlainText(art)

            self.view.setCentralWidget(text)
            self.view.show()
        except Exception as e:
            QMessageBox.critical(self, "", str(e))

    def _convert_to_file(self) -> None:
        """Конвертирует изображение и сохраняет результат в текстовый файл."""
        try:
            art = self._process_image_core()
            path, _ = QFileDialog.getSaveFileName(
                self, "", "", "Text Files (*.txt)")
            if path:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(art)
                QMessageBox.information(self, "", "Сохранено")
        except Exception as e:
            QMessageBox.critical(self, "", str(e))

    def _start_webcam(self) -> None:
        """Запускает режим веб-камеры с текущим набором символов."""
        try:
            choice = self.charset_combo.currentText()

            if choice == self.custom_trigger:
                tmp = "temp.txt"
                with open(tmp, "w", encoding="utf-8") as f:
                    f.write(self.custom_charset_data)
                charset_param = tmp
            else:
                charset_param = choice

            self.hide()
            cam = WebcamASCII(width=300, charset=charset_param)
            cam.run()
            self.show()

            if choice == self.custom_trigger and os.path.exists("temp.txt"):
                os.remove("temp.txt")
        except Exception as e:
            self.show()
            QMessageBox.critical(self, "", str(e))
