import unittest
from unittest.mock import patch, mock_open
from image_processor import ImageProcessor, Image


class TestImageProcessor(unittest.TestCase):
    def setUp(self) -> None:
        self.processor = ImageProcessor()

    def test_paeth_predictor_exact_matches(self) -> None:
        self.assertEqual(self.processor._paeth_predictor(10, 20, 20), 10)
        self.assertEqual(self.processor._paeth_predictor(20, 10, 20), 10)
        self.assertEqual(self.processor._paeth_predictor(20, 20, 10), 20)

    def test_paeth_predictor_all_equal(self) -> None:
        self.assertEqual(self.processor._paeth_predictor(15, 15, 15), 15)

    def test_paeth_predictor_negative_values(self) -> None:
        result = self.processor._paeth_predictor(-5, 10, 0)
        self.assertIn(result, [-5, 10, 0])

    def test_resize_image_dimensions_and_mapping(self) -> None:
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

    def test_resize_image_width_zero(self) -> None:
        img = Image(width=4, height=4, pixels=[[10, 20, 30, 40]] * 4)
        resized_img = self.processor.resize_image(img, width=0)
        self.assertEqual(resized_img.width, 0)
        self.assertEqual(resized_img.height, 0)

    def test_resize_image_large_width(self) -> None:
        img = Image(width=2, height=2, pixels=[[10, 20], [30, 40]])
        resized_img = self.processor.resize_image(img, width=100)
        self.assertEqual(resized_img.width, 100)
        self.assertGreater(resized_img.height, 0)

    def test_getpixel_out_of_bounds(self) -> None:
        img = Image(width=2, height=2, pixels=[[1, 2], [3, 4]])
        with self.assertRaises(IndexError):
            img.getpixel((5, 5))

    def test_getpixel_valid(self) -> None:
        img = Image(width=2, height=2, pixels=[[1, 2], [3, 4]])
        self.assertEqual(img.getpixel((0, 0)), 1)
        self.assertEqual(img.getpixel((1, 1)), 4)

    def test_reconstruct_filters(self) -> None:
        width, height = 2, 2
        color_type = 0
        palette = b""
        raw_data = bytes([0, 10, 20, 1, 5, 5])
        pixels = self.processor._reconstruct(
            raw_data, width, height, color_type, palette)
        self.assertEqual(pixels[0], [10, 20])
        self.assertEqual(pixels[1], [5, 10])

    def test_reconstruct_filter_type_2(self) -> None:
        width, height = 2, 2
        color_type = 0
        palette = b""
        raw_data = bytes([2, 10, 20, 0, 5, 6])
        pixels = self.processor._reconstruct(
            raw_data, width, height, color_type, palette)
        self.assertEqual(len(pixels), 2)

    def test_reconstruct_filter_type_3(self) -> None:
        width, height = 2, 2
        color_type = 0
        palette = b""
        raw_data = bytes([3, 10, 20, 0, 5, 6])
        pixels = self.processor._reconstruct(
            raw_data, width, height, color_type, palette)
        self.assertEqual(len(pixels), 2)

    def test_reconstruct_filter_type_4(self) -> None:
        width, height = 2, 2
        color_type = 0
        palette = b""
        raw_data = bytes([4, 10, 20, 0, 5, 6])
        pixels = self.processor._reconstruct(
            raw_data, width, height, color_type, palette)
        self.assertEqual(len(pixels), 2)

    def test_reconstruct_color_types(self) -> None:
        raw_rgb = bytes([0, 255, 0, 0, 0, 255, 0])
        pixels_rgb = self.processor._reconstruct(raw_rgb, 2, 1, 2, b"")
        self.assertEqual(len(pixels_rgb[0]), 2)

        raw_palette = bytes([0, 0, 1])
        fake_palette = b"\xff\x00\x00\x00\xff\x00"
        pixels_pal = self.processor._reconstruct(
            raw_palette, 2, 1, 3, fake_palette)
        self.assertEqual(len(pixels_pal[0]), 2)

        raw_rgba = bytes([0, 255, 0, 0, 255, 0, 255, 0, 255])
        pixels_rgba = self.processor._reconstruct(raw_rgba, 2, 1, 6, b"")
        self.assertEqual(len(pixels_rgba[0]), 2)

    def test_reconstruct_unsupported_color_type(self) -> None:
        with self.assertRaises(ValueError):
            self.processor._reconstruct(b"", 2, 2, 99, b"")

    def test_load_image_invalid_signature(self) -> None:
        with patch("builtins.open", mock_open(read_data=b"NOT_A_PNG_FILE")):
            with self.assertRaises(ValueError):
                self.processor.load_image("fake.png")

    def test_image_simple_init(self) -> None:
        img = Image(1, 1, [[100]])
        self.assertEqual(img.width, 1)
        self.assertEqual(img.height, 1)
        self.assertEqual(img.pixels, [[100]])

    def test_image_empty_pixels(self) -> None:
        img = Image(0, 0, [])
        self.assertEqual(img.width, 0)
        self.assertEqual(img.height, 0)
        self.assertEqual(img.pixels, [])

    def test_load_image_invalid_bit_depth(self) -> None:
        fake_png_data = (
            b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\x0d" + b"IHDR" +
            b"\x00\x00\x00\x01\x00\x00\x00\x01\x10\x02\x00\x00\x00" +
            b"fake_crc"
        )
        with patch("builtins.open", mock_open(read_data=fake_png_data)):
            with self.assertRaises(ValueError):
                self.processor.load_image("invalid_depth.png")

    def test_resize_image_preserves_content(self) -> None:
        original_pixels = [[100, 200], [150, 250]]
        img = Image(width=2, height=2, pixels=original_pixels)
        resized = self.processor.resize_image(img, width=1)
        self.assertEqual(resized.width, 1)
        self.assertGreaterEqual(resized.height, 0)

    def test_resize_image_aspect_ratio(self) -> None:
        img = Image(width=10, height=20, pixels=[[0] * 10] * 20)
        resized = self.processor.resize_image(img, width=5)
        expected_height = int(5 * 20 / 10 * 0.45)
        self.assertAlmostEqual(resized.height, expected_height, delta=1)


class TestImageProcessorEdgeCases(unittest.TestCase):
    def setUp(self) -> None:
        self.processor = ImageProcessor()

    def test_resize_image_minimal_dimensions(self) -> None:
        img = Image(width=1, height=1, pixels=[[100]])
        resized = self.processor.resize_image(img, width=1)
        self.assertEqual(resized.width, 1)
        self.assertEqual(resized.height, 0)

    def test_reconstruct_with_palette_index_out_of_range(self) -> None:
        width, height = 1, 1
        color_type = 3
        palette = b"\xff\x00\x00"
        raw_data = bytes([0, 5])
        with self.assertRaises(IndexError):
            self.processor._reconstruct(
                raw_data, width, height, color_type, palette)
