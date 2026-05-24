import unittest
from unittest.mock import patch, mock_open
from io_handler import IOHandler


class TestIOHandler(unittest.TestCase):

    def test_parse_arguments_default(self):
        io = IOHandler()
        with patch("sys.argv", ["main.py", "-i", "input.png"]):
            args = io.parse()
            self.assertEqual(args.input, "input.png")
            self.assertEqual(args.charset, "standard")
            self.assertFalse(args.webcam)

    def test_parse_arguments_custom(self):
        io = IOHandler()
        with patch("sys.argv", ["main.py", "--webcam", "-c", "blocks", "-o", "out.txt"]):
            args = io.parse()
            self.assertTrue(args.webcam)
            self.assertEqual(args.charset, "blocks")
            self.assertEqual(args.output, "out.txt")

    def test_print_to_console(self):
        io = IOHandler()
        with patch("builtins.print") as mock_print:
            io.print_to_console("ascii_art_data")
            mock_print.assert_called_once_with("ascii_art_data")

    def test_save_to_file(self):
        io = IOHandler()
        m = mock_open()
        with patch("builtins.open", m):
            io.save_to_file("art", "output.txt")
            m.assert_called_once_with("output.txt", "w", encoding="utf-8")
            m().write.assert_called_once_with("art")


if __name__ == "__main__":
    unittest.main()