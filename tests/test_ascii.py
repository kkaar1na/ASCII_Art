from PIL import Image
from image_processor import ImageProcessor
from ASCII_converter import ASCIIConverter

def test_load():
    proc = ImageProcessor()
    img = proc.load_image('cat.png')
    assert img is not None

def test_width():
    proc = ImageProcessor()
    img = Image.new('RGB', (200, 200))
    resized = proc.resize_image(img, width=100)
    assert resized.width == 100

def test_black_pixel():
    conv = ASCIIConverter()
    char = conv.pixel_to_char(0, "@#.")
    assert char == "@"

def test_white_pixel():
    conv = ASCIIConverter()
    char = conv.pixel_to_char(255, "@#.")
    assert char == "."

def test_charset_is_string():
    conv = ASCIIConverter()
    charset = conv.load_charset("standard")
    assert type(charset) is str