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
        """Проверяет загрузку стандартного встроенного набора символов."""
        charset = self.converter.load_charset("standard")
        self.assertEqual(charset, "@%#*+=-:. ")

    def test_load_charset_builtin_detailed(self) -> None:
        """Проверяет, что расширенный набор символов корректно извлекается по ключу."""
        charset = self.converter.load_charset("detailed")
        self.assertTrue(charset.startswith("$@B"))

    def test_load_charset_builtin_blocks(self) -> None:
        """Проверяет успешное получение набора блочных символов."""
        charset = self.converter.load_charset("blocks")
        self.assertEqual(charset, "█▓▒░ ")

    def test_load_charset_builtin_simple(self) -> None:
        """Проверяет извлечение простейшего набора символов."""
        charset = self.converter.load_charset("simple")
        self.assertEqual(charset, " .:-=+*#%@")

    def test_load_charset_non_existing(self) -> None:
        """Проверяет возврат набора по умолчанию при указании несуществующего имени."""
        charset = self.converter.load_charset("invalid_name_123")
        self.assertEqual(charset, "@%#*+=-:. ")

    def test_load_charset_from_file_success(self) -> None:
        """Проверяет успешное чтение кастомного набора символов из существующего текстового файла."""
        with patch("builtins.open", mock_open(read_data="QWERTY")):
            charset = self.converter.load_charset("my_charset.txt")
            self.assertEqual(charset, "QWERTY")

    def test_pixel_to_char_min(self) -> None:
        """Проверяет маппинг нулевой яркости в первый символ набора."""
        charset = "@%#*+=-:. "
        char = self.converter.pixel_to_char(0, charset)
        self.assertEqual(char, "@")

    def test_pixel_to_char_max(self) -> None:
        """Проверяет маппинг максимальной яркости (255) в последний символ набора."""
        charset = "@%#*+=-:. "
        char = self.converter.pixel_to_char(255, charset)
        self.assertEqual(char, " ")

    def test_pixel_to_char_middle(self) -> None:
        """Проверяет пропорциональный выбор символа для промежуточных значений яркости."""
        charset = "01234"
        char = self.converter.pixel_to_char(128, charset)
        self.assertEqual(char, "2")

    def test_pixel_to_char_empty_charset(self) -> None:
        """Убеждается, что пустой набор символов безопасно возвращает стандартный пробел."""
        char = self.converter.pixel_to_char(127, "")
        self.assertEqual(char, " ")

    def test_convert_small_image(self) -> None:
        """Проверяет итоговую сборку строк ASCII-арта из двумерной матрицы пикселей."""
        fake_image = FakeImage([
            [0, 255],
            [255, 0]
        ])
        result = self.converter.convert_to_ascii(fake_image, "standard")
        expected = "@ \n @"
        self.assertEqual(result, expected)

    def test_convert_uniform_image(self) -> None:
        """Проверяет сохранение пропорций строк и столбцов при конвертации однотонного изображения."""
        fake_image = FakeImage([
            [128, 128],
            [128, 128]
        ])
        result = self.converter.convert_to_ascii(fake_image, "standard")
        lines = result.split("\n")
        self.assertEqual(len(lines), 2)
        self.assertEqual(len(lines[0]), 2)

    def test_convert_brightness_clamping(self) -> None:
        """Проверяет ограничение значений яркости, выходящих за рамки 0-255."""
        fake_image = FakeImage([
            [-50, 300]
        ])
        result = self.converter.convert_to_ascii(fake_image, "standard")
        expected = "@ "
        self.assertEqual(result, expected)

    def test_pixel_to_char_extreme_brightness(self) -> None:
        """Проверяет маппинг символов при экстремальном выходе яркости за стандартные границы."""
        charset = "abc"
        char_low = self.converter.pixel_to_char(-50, charset)
        self.assertEqual(char_low, "a")
        char_high = self.converter.pixel_to_char(300, charset)
        self.assertEqual(char_high, "c")