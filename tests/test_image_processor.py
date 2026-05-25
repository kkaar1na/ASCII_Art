import unittest
from unittest.mock import patch, mock_open
from image_processor import ImageProcessor, Image

class TestImageProcessor(unittest.TestCase):
    def setUp(self) -> None:
        self.processor = ImageProcessor()

    def test_paeth_predictor_exact_matches(self) -> None:
        """Проверяет точность выбора базового значения Paeth-предсказателя при граничных условиях."""
        self.assertEqual(self.processor._paeth_predictor(10, 20, 20), 10)
        self.assertEqual(self.processor._paeth_predictor(20, 10, 20), 10)
        self.assertEqual(self.processor._paeth_predictor(20, 20, 10), 20)

    def test_resize_image_dimensions_and_mapping(self) -> None:
        """Проверяет корректность пропорционального масштабирования матрицы пикселей."""
        original_pixels = [
            [10, 20, 30, 40],
            [50, 60, 70, 80],
            [90, 100, 110, 120],
            [130, 140, 150, 160]
        ]
        img = Image(width=4, height=4, pixels=original_pixels)
        resized_img = self.processor.resize_image(img, width=2)
        self.assertEqual(resized_img.width, 2)
        self.assertGreaterEqual(resized_img.height, 0)

    def test_getpixel_out_of_bounds(self) -> None:
        """Убеждается, что метод getpixel падает с IndexError при запросе координат вне матрицы."""
        img = Image(width=2, height=2, pixels=[[1, 2], [3, 4]])
        with self.assertRaises(IndexError):
            img.getpixel((5, 5))

    def test_reconstruct_filters(self) -> None:
        """Тестирует применение базовых типов фильтрации (0 и 1) при восстановлении строк PNG."""
        width, height = 2, 2
        color_type = 0
        palette = b""
        raw_data = bytes([
            0, 10, 20,
            1, 5, 5
        ])
        pixels = self.processor._reconstruct(raw_data, width, height, color_type, palette)
        self.assertEqual(pixels[0], [10, 20])
        self.assertEqual(pixels[1], [5, 10])

    def test_reconstruct_color_types(self) -> None:
        """Тестирует декодирование и сведение к оттенкам серого для форматов RGB, Palette и RGBA."""
        raw_rgb = bytes([0, 255, 0, 0, 0, 255, 0])
        pixels_rgb = self.processor._reconstruct(raw_rgb, 2, 1, 2, b"")
        self.assertEqual(len(pixels_rgb[0]), 2)

        raw_palette = bytes([0, 0, 1])
        fake_palette = b"\xff\x00\x00\x00\xff\x00"
        pixels_pal = self.processor._reconstruct(raw_palette, 2, 1, 3, fake_palette)
        self.assertEqual(len(pixels_pal[0]), 2)

        raw_rgba = bytes([0, 255, 0, 0, 255, 0, 255, 0, 255])
        pixels_rgba = self.processor._reconstruct(raw_rgba, 2, 1, 6, b"")
        self.assertEqual(len(pixels_rgba[0]), 2)

    def test_load_image_invalid_signature(self) -> None:
        """Проверяет генерацию ошибки ValueError, если файл не имеет валидной сигнатуры PNG."""
        with patch("builtins.open", mock_open(read_data=b"NOT_A_PNG_FILE")):
            with self.assertRaises(ValueError):
                self.processor.load_image("fake.png")

    def test_image_simple_init(self) -> None:
        """Проверяет корректное сохранение атрибутов геометрии структуры данных Image при инициализации."""
        img = Image(1, 1, [[100]])
        self.assertEqual(img.width, 1)
        self.assertEqual(img.height, 1)
        self.assertEqual(img.pixels, [[100]])

    def test_load_image_invalid_bit_depth(self) -> None:
        """Проверяет генерацию ошибки ValueError при обработке PNG с отличной от 8 бит глубиной цвета."""
        fake_png_data = b"\x89PNG\r\n\x1a\n" + \
                        b"\x00\x00\x00\x0d" + b"IHDR" + \
                        b"\x00\x00\x00\x01\x00\x00\x00\x01\x10\x02\x00\x00\x00" + b"fake_crc"
        with patch("builtins.open", mock_open(read_data=fake_png_data)):
            with self.assertRaises(ValueError):
                self.processor.load_image("invalid_depth.png")