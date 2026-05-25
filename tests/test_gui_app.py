import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
from PyQt6.QtWidgets import QApplication
from gui_app import ASCIIAppGUI

app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()


class TestASCIIAppGUI(unittest.TestCase):
    def setUp(self) -> None:
        with patch('PyQt6.QtWidgets.QMainWindow.show'), patch('PyQt6.QtWidgets.QWidget.show'):
            self.gui = ASCIIAppGUI()
        self.gui.charset_combo = MagicMock()
        self.gui.file_entry = MagicMock()
        self.gui.show = MagicMock()
        self.gui.hide = MagicMock()

    @patch("gui_app.QFileDialog.getOpenFileName")
    def test_browse_file_updates_path_on_success(self, mock_dialog) -> None:
        """Проверяет, что выбор файла через диалог обновляет путь в строке ввода и внутреннее состояние."""
        mock_dialog.return_value = ("/path/to/image.png", "PNG Files (*.png)")
        self.gui._browse_file()
        self.assertEqual(self.gui.input_path, "/path/to/image.png")
        self.gui.file_entry.setText.assert_called_once_with("/path/to/image.png")

    def test_get_active_charset_for_builtin_presets(self) -> None:
        """Убеждается, что метод корректно извлекает строковое имя выбранного встроенного пресета."""
        self.gui.charset_combo.currentText.return_value = "standard"
        self.assertEqual(self.gui._get_active_charset(), "standard")

    def test_process_image_core_raises_value_error_if_no_file(self) -> None:
        """Проверяет генерацию исключения ValueError, если ядро обработки вызвано без указания пути к файлу."""
        self.gui.input_path = ""
        with self.assertRaises(ValueError):
            self.gui._process_image_core()

    @patch("gui_app.QFileDialog.getSaveFileName")
    @patch("gui_app.QMessageBox.information")
    def test_convert_to_file_flow(self, mock_info, mock_save_dialog) -> None:
        """Проверяет выполнение сценария сохранения сгенерированного арта через системное окно сохранения."""
        mock_save_dialog.return_value = ("output.txt", "Text Files (*.txt)")
        self.gui._process_image_core = MagicMock(return_value="mock_ascii")

        with patch("builtins.open", mock_open()) as mock_f:
            self.gui._convert_to_file()
            mock_f.assert_called_once_with("output.txt", "w", encoding="utf-8")

    @patch("gui_app.WebcamASCII")
    def test_start_webcam_flow(self, mock_webcam) -> None:
        """Проверяет корректное скрытие окон GUI, инициализацию и запуск стрима веб-камеры."""
        mock_cam_instance = MagicMock()
        mock_webcam.return_value = mock_cam_instance
        self.gui.charset_combo.currentText.return_value = "standard"

        self.gui._start_webcam()
        mock_webcam.assert_called_once_with(width=300, charset="standard")
        mock_cam_instance.run.assert_called_once()

    def test_simple_gui_properties(self) -> None:
        """Проверяет начальное состояние базовых свойств интерфейса после инициализации."""
        self.assertEqual(self.gui.input_path, "")
        self.assertEqual(self.gui.custom_charset_data, "")