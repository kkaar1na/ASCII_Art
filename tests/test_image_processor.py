import unittest
import struct
import zlib
from image_processor import ImageProcessor, Image


class TestImageProcessor(unittest.TestCase):

    def setUp(self):
        self.processor = ImageProcessor()

    def test_paeth_predictor(self):
        self.assertEqual(self.processor._paeth_predictor(10, 20, 15), 15)
        self.assertEqual(self.processor._paeth_predictor(10, 30, 15), 30)
        self.assertEqual(self.processor._paeth_predictor(30, 10, 15), 30)

    def test_resize_image(self):
        pixels = [
            [10, 20, 30, 40],
            [50, 60, 70, 80],
            [90, 100, 110, 120],
            [130, 140, 150, 160]
        ]
        img = Image(width=4, height=4, pixels=pixels)

        resized = self.processor.resize_image(img, width=2)

        self.assertEqual(resized.width, 2)
        self.assertEqual(resized.height, 0)
        self.assertEqual(resized.pixels, [])

    def test_resize_image_valid_height(self):
        pixels = [[0] * 100 for _ in range(100)]
        img = Image(width=100, height=100, pixels=pixels)

        resized = self.processor.resize_image(img, width=10)

        self.assertEqual(resized.width, 10)
        self.assertEqual(resized.height, 4)
        self.assertEqual(len(resized.pixels), 4)
        self.assertEqual(len(resized.pixels[0]), 10)

    def test_convert_to_grayscale(self):
        img = Image(width=2, height=2, pixels=[[1, 2], [3, 4]])
        self.assertIs(self.processor.convert_to_grayscale(img), img)

    def test_reconstruct_filters_and_color_types(self):
        # Тестируем color_type=0 (Grayscale), filter_type=0, 1, 2, 3, 4
        # Каждый ряд начинается с байта фильтра
        raw_data = bytes([
            0, 10, 20,  # Row 0, Filter 0: без изменений -> [10, 20]
            1, 5, 10,  # Row 1, Filter 1: left -> [5, 15]
            2, 2, 2,  # Row 2, Filter 2: up -> [5+2, 15+2] = [7, 17]
            3, 1, 1,  # Row 3, Filter 3: avg(left, up) -> [1 + (0+7)//2, 1 + (4+17)//2] = [4, 11]
            4, 0, 0  # Row 4, Filter 4: Paeth -> проверяет ветку Paeth
        ])
        pixels = self.processor._reconstruct(raw_data, width=2, height=5, color_type=0, palette=None)
        self.assertEqual(len(pixels), 5)
        self.assertEqual(pixels[0], [10, 20])

        # Тестируем color_type=2 (RGB)
        raw_rgb = bytes([0, 255, 0, 0, 0, 255, 0])  # Filter 0, Pixel 1 (R=255), Pixel 2 (G=255)
        pixels_rgb = self.processor._reconstruct(raw_rgb, width=2, height=1, color_type=2, palette=None)
        self.assertEqual(len(pixels_rgb), 1)

        # Тестируем color_type=3 (Palette)
        palette = bytes([255, 0, 0, 0, 255, 0])  # ID 0: Red, ID 1: Green
        raw_palette = bytes([0, 0, 1])  # Filter 0, ID 0, ID 1
        pixels_pal = self.processor._reconstruct(raw_palette, width=2, height=1, color_type=3, palette=palette)
        self.assertEqual(len(pixels_pal), 1)

        # Тестируем color_type=6 (RGBA)
        raw_rgba = bytes([0, 255, 0, 0, 255, 0, 255, 0, 255])
        pixels_rgba = self.processor._reconstruct(raw_rgba, width=2, height=1, color_type=6, palette=None)
        self.assertEqual(len(pixels_rgba), 1)

    def test_reconstruct_invalid_color_type(self):
        with self.assertRaises(ValueError):
            self.processor._reconstruct(bytes([0, 1]), width=1, height=1, color_type=99, palette=None)


if __name__ == "__main__":
    unittest.main()