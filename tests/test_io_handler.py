import unittest
from unittest.mock import patch, mock_open
from io_handler import IOHandler


class TestIOHandler(unittest.TestCase):
    def test_parse_arguments_default(self) -> None:
        io = IOHandler()
        with patch("sys.argv", [["main.py"], "-i", "input.png"]):
            args = io.parse()
            self.assertEqual(args.input, "input.png")
            self.assertEqual(args.charset, "standard")
            self.assertFalse(args.webcam)

    def test_parse_arguments_custom(self) -> None:
        io = IOHandler()
        argv = ["main.py", "--webcam", "-c", "blocks", "-o", "out.txt"]
        with patch("sys.argv", argv):
            args = io.parse()
            self.assertTrue(args.webcam)
            self.assertEqual(args.charset, "blocks")
            self.assertEqual(args.output, "out.txt")

    def test_parse_arguments_input_only(self) -> None:
        io = IOHandler()
        argv = ["main.py", "-i", "test.png", "-c", "detailed"]
        with patch("sys.argv", argv):
            args = io.parse()
            self.assertEqual(args.input, "test.png")
            self.assertEqual(args.charset, "detailed")
            self.assertIsNone(args.output)

    def test_print_to_console(self) -> None:
        io = IOHandler()
        with patch("builtins.print") as mock_print:
            io.print_to_console("ascii_art_data")
            mock_print.assert_called_once_with("ascii_art_data")

    def test_print_to_console_empty_and_multiline(self) -> None:
        io = IOHandler()
        with patch("builtins.print") as mock_print:
            io.print_to_console("")
            mock_print.assert_called_with("")
            io.print_to_console("line1\nline2")
            mock_print.assert_called_with("line1\nline2")

    def test_save_to_file(self) -> None:
        io = IOHandler()
        m = mock_open()
        with patch("builtins.open", m):
            io.save_to_file("art", "test.txt")
            m.assert_called_once_with("test.txt", "w", encoding="utf-8")
            m().write.assert_called_once_with("art")

    def test_save_to_file_empty_string(self) -> None:
        io = IOHandler()
        m = mock_open()
        with patch("builtins.open", m):
            io.save_to_file("", "empty.txt")
            m().write.assert_called_once_with("")
