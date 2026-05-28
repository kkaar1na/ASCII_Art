import sys
import unittest
from unittest.mock import patch, MagicMock, mock_open


class SmartFakeWidget:

    def __init__(self, *args, **kwargs):
        self._mock_methods = {}

    def __getattr__(self, name):
        if name not in self._mock_methods:
            self._mock_methods[name] = MagicMock()
        return self._mock_methods[name]

    def windowTitle(self) -> str:
        return "ASCII Art"

    def width(self) -> int:
        return 500

    def height(self) -> int:
        return 400


class FakeComboBox(SmartFakeWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._current_text = "standard"
        self._items = [
            "standard", "detailed", "blocks", "simple", "свой файл..."
        ]

    def currentText(self) -> str:
        return self._current_text

    def setCurrentText(self, text: str) -> None:
        self._current_text = text

    def count(self) -> int:
        return len(self._items)

    def itemText(self, index: int) -> str:
        return self._items[index]


qt_mock = MagicMock()
QtWidgets_mock = MagicMock()

QtWidgets_mock.QMainWindow = SmartFakeWidget
QtWidgets_mock.QWidget = SmartFakeWidget
QtWidgets_mock.QDialog = SmartFakeWidget
QtWidgets_mock.QComboBox = FakeComboBox
QtWidgets_mock.QPushButton = SmartFakeWidget
QtWidgets_mock.QLineEdit = SmartFakeWidget
QtWidgets_mock.QTextEdit = SmartFakeWidget
QtWidgets_mock.QVBoxLayout = SmartFakeWidget
QtWidgets_mock.QHBoxLayout = SmartFakeWidget

sys.modules['PyQt6'] = qt_mock
sys.modules['PyQt6.QtWidgets'] = QtWidgets_mock
sys.modules['PyQt6.QtGui'] = MagicMock()
sys.modules['PyQt6.QtCore'] = MagicMock()


class TestASCIIAppGUI(unittest.TestCase):

    def setUp(self) -> None:
        QtWidgets_mock.QMessageBox.critical.reset_mock()
        QtWidgets_mock.QMessageBox.information.reset_mock()
        QtWidgets_mock.QMessageBox.warning.reset_mock()
        QtWidgets_mock.QFileDialog.getOpenFileName.reset_mock()
        QtWidgets_mock.QFileDialog.getSaveFileName.reset_mock()

        if 'gui_app' in sys.modules:
            del sys.modules['gui_app']

        with patch('gui_app.ImageProcessor'), patch(
                'gui_app.ASCIIConverter'):
            from gui_app import ASCIIAppGUI
            self.gui = ASCIIAppGUI()

        self.gui.input_path = ""
        self.gui.custom_charset_data = ""

    def test_window_title(self) -> None:
        self.assertEqual(self.gui.windowTitle(), "ASCII Art")

    def test_window_fixed_size(self) -> None:
        self.assertEqual(self.gui.width(), 500)
        self.assertEqual(self.gui.height(), 400)

    def test_initial_input_path_empty(self) -> None:
        self.assertEqual(self.gui.input_path, "")

    def test_initial_custom_charset_empty(self) -> None:
        self.assertEqual(self.gui.custom_charset_data, "")

    def test_charset_combo_has_items(self) -> None:
        expected = ["standard", "detailed", "blocks", "simple", "свой файл..."]
        items = [
            self.gui.charset_combo.itemText(i)
            for i in range(self.gui.charset_combo.count())
        ]
        self.assertEqual(items, expected)

    def test_get_active_charset_standard(self) -> None:
        self.gui.charset_combo.setCurrentText("standard")
        self.assertEqual(self.gui._get_active_charset(), "standard")

    def test_get_active_charset_detailed(self) -> None:
        self.gui.charset_combo.setCurrentText("detailed")
        self.assertEqual(self.gui._get_active_charset(), "detailed")

    def test_get_active_charset_blocks(self) -> None:
        self.gui.charset_combo.setCurrentText("blocks")
        self.assertEqual(self.gui._get_active_charset(), "blocks")

    def test_get_active_charset_simple(self) -> None:
        self.gui.charset_combo.setCurrentText("simple")
        self.assertEqual(self.gui._get_active_charset(), "simple")

    def test_get_active_charset_custom_with_data(self) -> None:
        self.gui.charset_combo.setCurrentText("свой файл...")
        self.gui.custom_charset_data = "ABCDEFG"
        self.assertEqual(self.gui._get_active_charset(), "ABCDEFG")

    def test_get_active_charset_custom_without_data(self) -> None:
        self.gui.charset_combo.setCurrentText("свой файл...")
        self.gui.custom_charset_data = ""
        self.assertEqual(self.gui._get_active_charset(), "@%#*+=-:. ")

    def test_process_image_core_raises_error_if_no_file(self) -> None:
        self.gui.input_path = ""
        with self.assertRaises(ValueError) as context:
            self.gui._process_image_core()
        self.assertEqual(str(context.exception), "Выберите изображение")

    @patch("gui_app.ImageProcessor")
    @patch("gui_app.ASCIIConverter")
    def test_process_image_core_standard_charset(
            self, mock_converter_class, mock_processor_class) -> None:
        mock_processor = MagicMock()
        mock_converter = MagicMock()
        mock_processor_class.return_value = mock_processor
        mock_converter_class.return_value = mock_converter

        mock_image = MagicMock()
        mock_resized = MagicMock()
        mock_processor.load_image.return_value = mock_image
        mock_processor.resize_image.return_value = mock_resized
        mock_converter.convert_to_ascii.return_value = "ascii_result"

        self.gui.input_path = "test.png"
        self.gui.processor = mock_processor
        self.gui.converter = mock_converter
        self.gui.charset_combo.setCurrentText("standard")

        result = self.gui._process_image_core()
        self.assertEqual(result, "ascii_result")

    @patch("gui_app.ImageProcessor")
    def test_process_image_core_custom_charset(
            self, mock_processor_class) -> None:
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor

        mock_image = MagicMock()
        mock_resized = MagicMock()
        mock_resized.height = 2
        mock_resized.width = 2

        mock_resized.getpixel = MagicMock(
            side_effect=[100, 150, 200, 250, 0, 0, 0]
        )
        mock_processor.load_image.return_value = mock_image
        mock_processor.resize_image.return_value = mock_resized

        self.gui.input_path = "test.png"
        self.gui.processor = mock_processor
        self.gui.converter = MagicMock()
        self.gui.converter.pixel_to_char = MagicMock(
            side_effect=["A", "B", "C", "D", " ", " ", " "]
        )
        self.gui.charset_combo.setCurrentText("свой файл...")
        self.gui.custom_charset_data = "ABCD"

        result = self.gui._process_image_core()
        self.assertEqual(result, "AB\nCD")

    def test_convert_to_window_error_handling(self) -> None:
        self.gui.input_path = "test.png"
        mock_critical = QtWidgets_mock.QMessageBox.critical
        with patch.object(self.gui, '_process_image_core',
                          side_effect=Exception("Conversion error")):
            self.gui._convert_to_window()
            mock_critical.assert_called_once()

    @patch("gui_app.QMessageBox.information")
    def test_convert_to_file_success(self, mock_info) -> None:
        mock_save_dialog = QtWidgets_mock.QFileDialog.getSaveFileName
        mock_save_dialog.return_value = ("output.txt", "Text Files (*.txt)")
        self.gui.input_path = "test.png"
        self.gui.charset_combo.setCurrentText("standard")

        with patch.object(self.gui, '_process_image_core',
                          return_value="ascii_art"):
            with patch("builtins.open", mock_open()) as mock_file:
                self.gui._convert_to_file()
                mock_file.assert_called_once_with(
                    "output.txt", "w", encoding="utf-8")
                mock_info.assert_called_once()

    def test_convert_to_file_cancelled(self) -> None:
        mock_save_dialog = QtWidgets_mock.QFileDialog.getSaveFileName
        mock_save_dialog.return_value = ("", "")
        with patch.object(self.gui, '_process_image_core',
                          return_value="mock_ascii"):
            with patch("builtins.open", mock_open()) as mock_file:
                self.gui._convert_to_file()
                if hasattr(mock_file, 'assert_not_called'):
                    mock_file.assert_not_called()

    def test_convert_to_file_error_handling(self) -> None:
        mock_save_dialog = QtWidgets_mock.QFileDialog.getSaveFileName
        mock_save_dialog.return_value = ("output.txt", "Text Files (*.txt)")
        mock_critical = QtWidgets_mock.QMessageBox.critical
        with patch.object(self.gui, '_process_image_core',
                          side_effect=Exception("Conversion error")):
            self.gui._convert_to_file()
            mock_critical.assert_called_once()

    @patch("gui_app.WebcamASCII")
    def test_start_webcam_standard(self, mock_webcam) -> None:
        mock_cam_instance = MagicMock()
        mock_webcam.return_value = mock_cam_instance
        self.gui.charset_combo.setCurrentText("standard")

        with patch.object(self.gui, 'hide') as mock_hide, patch.object(
                self.gui, 'show') as mock_show:
            self.gui._start_webcam()
            mock_webcam.assert_called_once_with(
                width=300, charset="standard")
            mock_cam_instance.run.assert_called_once()
            mock_hide.assert_called_once()
            mock_show.assert_called_once()

    @patch("gui_app.WebcamASCII")
    def test_start_webcam_exception(self, mock_webcam) -> None:
        mock_webcam.side_effect = Exception("Webcam error")
        self.gui.charset_combo.setCurrentText("standard")
        mock_critical = QtWidgets_mock.QMessageBox.critical

        with patch.object(self.gui, 'show') as mock_show:
            self.gui._start_webcam()
            mock_critical.assert_called_once()
            mock_show.assert_called_once()

    def test_on_charset_changed_builtin(self) -> None:
        self.gui._on_charset_changed(0)
        self.assertEqual(self.gui.custom_charset_data, "")

    @patch("gui_app.QMessageBox.information")
    def test_on_charset_changed_custom_success(self, mock_info) -> None:
        mock_dialog = QtWidgets_mock.QFileDialog.getOpenFileName
        mock_dialog.return_value = ("custom.txt", "Text Files (*.txt)")
        with patch("builtins.open", mock_open(read_data="ABCDEFGH")):
            self.gui._on_charset_changed(4)
            mock_info.assert_called_once()
            self.assertEqual(self.gui.custom_charset_data, "ABCDEFGH")

    def test_on_charset_changed_custom_empty(self) -> None:
        mock_dialog = QtWidgets_mock.QFileDialog.getOpenFileName
        mock_dialog.return_value = ("custom.txt", "Text Files (*.txt)")
        mock_warning = QtWidgets_mock.QMessageBox.warning
        with patch("builtins.open", mock_open(read_data="")):
            self.gui._on_charset_changed(4)
            mock_warning.assert_called_once()

    def test_on_charset_changed_custom_error(self) -> None:
        mock_dialog = QtWidgets_mock.QFileDialog.getOpenFileName
        mock_dialog.return_value = ("custom.txt", "Text Files (*.txt)")
        mock_warning = QtWidgets_mock.QMessageBox.warning
        with patch("builtins.open",
                   side_effect=IOError("Permission denied")):
            self.gui._on_charset_changed(4)
            mock_warning.assert_called_once()

    def test_convert_to_window_without_file_shows_error(self) -> None:
        self.gui.input_path = ""
        mock_critical = QtWidgets_mock.QMessageBox.critical
        self.gui._convert_to_window()
        mock_critical.assert_called_once()

    def test_webcam_button_exists(self) -> None:
        self.assertIsNotNone(self.gui.webcam_btn)

    def test_browse_file_no_path(self) -> None:
        mock_dialog = QtWidgets_mock.QFileDialog.getOpenFileName
        mock_dialog.return_value = ("", "")
        self.gui._browse_file()
        self.assertEqual(self.gui.input_path, "")

    def test_browse_file_with_path(self) -> None:
        mock_dialog = QtWidgets_mock.QFileDialog.getOpenFileName
        mock_dialog.return_value = (
            "/path/img.png", "PNG Files (*.png)"
        )
        self.gui._browse_file()
        self.assertEqual(self.gui.input_path, "/path/img.png")

    @patch("gui_app.QMainWindow")
    @patch("gui_app.QTextEdit")
    def test_convert_to_window_creates_view(
            self, mock_text_edit, mock_main_window) -> None:
        mock_view = MagicMock()
        mock_main_window.return_value = mock_view
        mock_text = MagicMock()
        mock_text_edit.return_value = mock_text

        self.gui.input_path = "test.png"
        with patch.object(self.gui, '_process_image_core',
                          return_value="ascii_art"):
            self.gui._convert_to_window()
            mock_main_window.assert_called_once()
