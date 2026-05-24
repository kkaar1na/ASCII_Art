import unittest
from unittest.mock import patch, mock_open
from ASCII_converter import ASCIIConverter


class FakeImage:
    def __init__(self, pixels):
        self.pixels = pixels
        self.height = len(pixels)
        self.width = len(pixels[0]) if pixels else 0

    def getpixel(self, pos):
        x, y = pos
        return self.pixels[y][x]


class TestASCIIConverter(unittest.TestCase):

    def setUp(self):
        self.converter = ASCIIConverter()

    def test_load_charset_builtin_standard(self):
        charset = self.converter.load_charset("standard")
        self.assertEqual(charset, "@%#*+=-:. ")

    def test_load_charset_builtin_detailed(self):
        charset = self.converter.load_charset("detailed")
        self.assertTrue(charset.startswith("$@B"))

    def test_load_charset_builtin_blocks(self):
        charset = self.converter.load_charset("blocks")
        self.assertEqual(charset, "█▓▒░ ")

    def test_load_charset_builtin_simple(self):
        charset = self.converter.load_charset("simple")
        self.assertEqual(charset, " .:-=+*#%@")

    def test_load_charset_non_existing(self):
        charset = self.converter.load_charset("invalid_name_123")
        self.assertEqual(charset, "@%#*+=-:. ")

    def test_load_charset_from_file_success(self):
        mock_data = "ABCDE"
        with patch("builtins.open", mock_open(read_data=mock_data)):
            charset = self.converter.load_charset("custom_charset.txt")
            self.assertEqual(charset, "ABCDE")

    def test_load_charset_from_file_with_whitespace(self):
        mock_data = "  XYZ  \n"
        with patch("builtins.open", mock_open(read_data=mock_data)):
            charset = self.converter.load_charset("custom_charset.txt")
            self.assertEqual(charset, "XYZ")

    def test_pixel_to_char_min(self):
        charset = "@%#*+=-:. "
        char = self.converter.pixel_to_char(0, charset)
        self.assertEqual(char, "@")

    def test_pixel_to_char_max(self):
        charset = "@%#*+=-:. "
        char = self.converter.pixel_to_char(255, charset)
        self.assertEqual(char, " ")

    def test_pixel_to_char_middle(self):
        charset = "01234"
        char = self.converter.pixel_to_char(128, charset)
        self.assertEqual(char, "2")

    def test_pixel_to_char_empty_charset(self):
        char = self.converter.pixel_to_char(127, "")
        self.assertEqual(char, " ")

    def test_convert_small_image(self):
        fake_image = FakeImage([
            [0, 255],
            [255, 0]
        ])
        result = self.converter.convert_to_ascii(fake_image, "standard")
        expected = "@ \n @"
        self.assertEqual(result, expected)

    def test_convert_uniform_image(self):
        fake_image = FakeImage([
            [128, 128],
            [128, 128]
        ])
        result = self.converter.convert_to_ascii(fake_image, "standard")
        lines = result.split("\n")
        self.assertEqual(len(lines), 2)
        self.assertEqual(len(lines[0]), 2)

    def test_convert_brightness_clamping(self):
        fake_image = FakeImage([
            [-50, 300]
        ])
        result = self.converter.convert_to_ascii(fake_image, "standard")
        expected = "@ "
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()