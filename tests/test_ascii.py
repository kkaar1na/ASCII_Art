import unittest
from unittest.mock import patch, mock_open
from ASCII_converter import ASCIIConverter


class FakeImage:
    def __init__(self, pixels) -> None:
        self.pixels = pixels
        self.height = len(pixels)
        self.width = len(pixels[0]) if pixels else 0

    def getpixel(self, pos) -> int:
        x, y = pos
        return self.pixels[y][x]


class TestASCIIConverter(unittest.TestCase):
    def setUp(self) -> None:
        self.converter = ASCIIConverter()

    def test_load_charset_builtin_standard(self) -> None:
        charset = self.converter.load_charset("standard")
        self.assertEqual(charset, "@%#*+=-:. ")

    def test_load_charset_builtin_detailed(self) -> None:
        charset = self.converter.load_charset("detailed")
        self.assertTrue(charset.startswith("$@B"))

    def test_load_charset_builtin_blocks(self) -> None:
        charset = self.converter.load_charset("blocks")
        self.assertEqual(charset, "█▓▒░ ")

    def test_load_charset_builtin_simple(self) -> None:
        charset = self.converter.load_charset("simple")
        self.assertEqual(charset, " .:-=+*#%@")

    def test_load_charset_non_existing(self) -> None:
        charset = self.converter.load_charset("invalid_name_123")
        self.assertEqual(charset, "@%#*+=-:. ")

    def test_load_charset_from_file_success(self) -> None:
        with patch("builtins.open", mock_open(read_data="QWERTY")):
            charset = self.converter.load_charset("my_charset.txt")
            self.assertEqual(charset, "QWERTY")

    def test_pixel_to_char_min(self) -> None:
        charset = "@%#*+=-:. "
        char = self.converter.pixel_to_char(0, charset)
        self.assertEqual(char, "@")

    def test_pixel_to_char_max(self) -> None:
        charset = "@%#*+=-:. "
        char = self.converter.pixel_to_char(255, charset)
        self.assertEqual(char, " ")

    def test_pixel_to_char_middle(self) -> None:
        charset = "01234"
        char = self.converter.pixel_to_char(128, charset)
        self.assertEqual(char, "2")

    def test_pixel_to_char_empty_charset(self) -> None:
        char = self.converter.pixel_to_char(127, "")
        self.assertEqual(char, " ")

    def test_pixel_to_char_single_char_charset(self) -> None:
        charset = "X"
        char = self.converter.pixel_to_char(100, charset)
        self.assertEqual(char, "X")

    def test_convert_small_image(self) -> None:
        fake_image = FakeImage([[0, 255], [255, 0]])
        result = self.converter.convert_to_ascii(fake_image, "standard")
        expected = "@ \n @"
        self.assertEqual(result, expected)

    def test_convert_uniform_image(self) -> None:
        fake_image = FakeImage([[128, 128], [128, 128]])
        result = self.converter.convert_to_ascii(fake_image, "standard")
        lines = result.split("\n")
        self.assertEqual(len(lines), 2)
        self.assertEqual(len(lines[0]), 2)

    def test_convert_empty_image(self) -> None:
        fake_image = FakeImage([])
        result = self.converter.convert_to_ascii(fake_image, "standard")
        self.assertEqual(result, "")

    def test_convert_single_pixel(self) -> None:
        fake_image = FakeImage([[128]])
        result = self.converter.convert_to_ascii(fake_image, "standard")
        self.assertEqual(result, "+")


class TestASCIIConverterEdgeCases(unittest.TestCase):
    def setUp(self) -> None:
        self.converter = ASCIIConverter()

    def test_convert_one_row_image(self) -> None:
        fake_image = FakeImage([[100, 150, 200]])
        result = self.converter.convert_to_ascii(fake_image, "standard")
        self.assertEqual(len(result.split("\n")), 1)

    def test_pixel_to_char_boundary_values(self) -> None:
        charset = "ABCDE"
        self.assertEqual(self.converter.pixel_to_char(0, charset), "A")
        self.assertEqual(self.converter.pixel_to_char(255, charset), "E")
