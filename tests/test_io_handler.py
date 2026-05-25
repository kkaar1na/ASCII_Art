import unittest
from unittest.mock import patch, mock_open
from io_handler import IOHandler

class TestIOHandler(unittest.TestCase):
    def test_parse_arguments_default(self) -> None:
        """Проверяет парсинг и установку параметров по умолчанию при явном указании флага входного файла."""
        io = IOHandler()
        with patch("sys.argv", [["main.py"], "-i", "input.png"]):
            args = io.parse()
            self.assertEqual(args.input, "input.png")
            self.assertEqual(args.charset, "standard")
            self.assertFalse(args.webcam)

    def test_parse_arguments_custom(self) -> None:
        """Проверяет парсинг всех переопределяемых флагов конфигурации командной строки."""
        io = IOHandler()
        with patch("sys.argv", ["main.py", "--webcam", "-c", "blocks", "-o", "out.txt"]):
            args = io.parse()
            self.assertTrue(args.webcam)
            self.assertEqual(args.charset, "blocks")
            self.assertEqual(args.output, "out.txt")

    def test_print_to_console(self) -> None:
        """Убеждается, что метод вывода обращается к стандартной функции печати терминала."""
        io = IOHandler()
        with patch("builtins.print") as mock_print:
            io.print_to_console("ascii_art_data")
            mock_print.assert_called_once_with("ascii_art_data")

    def test_print_to_console_empty_and_multiline(self) -> None:
        """Проверяет бесперебойный вывод пустых строк и многострочного форматированного текста в поток вывода."""
        io = IOHandler()
        with patch("builtins.print") as mock_print:
            io.print_to_console("")
            mock_print.assert_called_with("")
            io.print_to_console("line1\nline2")
            mock_print.assert_called_with("line1\nline2")

    def test_save_to_file(self) -> None:
        """Проверяет открытие файлового дескриптора на запись и сохранение текстовых данных в UTF-8."""
        io = IOHandler()
        m = mock_open()
        with patch("builtins.open", m):
            io.save_to_file("art", "test.txt")
            m.assert_called_once_with("test.txt", "w", encoding="utf-8")
            m().write.assert_called_once_with("art")