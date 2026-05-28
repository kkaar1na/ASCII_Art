import struct
import zlib
from typing import List, Tuple


class Image:
    """Объект декодированного изображения с матрицей пикселей."""

    def __init__(self, width: int, height: int,
                 pixels: List[List[int]]) -> None:
        """Инициализирует размеры и двумерный массив пикселей.

        Args:
            width: Ширина изображения в пикселях.
            height: Высота изображения в пикселях.
            pixels: Двумерный список значений яркости (0-255).
        """
        self.width = width
        self.height = height
        self.pixels = pixels

    def getpixel(self, pos: Tuple[int, int]) -> int:
        """Возвращает значение яркости пикселя по координатам.

        Args:
            pos: Кортеж (x, y) с координатами пикселя.

        Returns:
            Значение яркости от 0 до 255.
        """
        x, y = pos
        return self.pixels[y][x]


class ImageProcessor:
    """Процессор для низкоуровневого парсинга PNG и изменения размера."""

    def load_image(self, path: str) -> Image:
        """Загружает PNG-файл и возвращает объект Image.

        Args:
            path: Путь к PNG-файлу.

        Returns:
            Объект Image с декодированными пикселями.

        Raises:
            ValueError: Если файл не является PNG.
        """
        with open(path, "rb") as f:
            data = f.read()

        if data[:8] != b"\x89PNG\r\n\x1a\n":
            raise ValueError("это не png")

        pos = 8
        width = height = None
        color_type = None
        idat_data = b""
        palette = None

        while pos < len(data):
            length = struct.unpack(">I", data[pos:pos + 4])[0]
            pos += 4

            chunk_type = data[pos:pos + 4]
            pos += 4

            chunk_data = data[pos:pos + length]
            pos += length
            pos += 4

            if chunk_type == b'IHDR':
                width, height, bit_depth, color_type = struct.unpack(
                    ">IIBB", chunk_data[:10])
                if bit_depth != 8:
                    raise ValueError("только 8-bit png поддерживается")

            elif chunk_type == b'PLTE':
                palette = chunk_data

            elif chunk_type == b'IDAT':
                idat_data += chunk_data

            elif chunk_type == b'IEND':
                break

        raw = zlib.decompress(idat_data)
        pixels = self._reconstruct(raw, width, height, color_type, palette)
        return Image(width, height, pixels)

    def _paeth_predictor(self, a: int, b: int, c: int) -> int:
        """Вычисляет предсказание по алгоритму Paeth для дефильтрации PNG.

        Args:
            a: Значение левого пикселя.
            b: Значение верхнего пикселя.
            c: Значение диагонального пикселя.

        Returns:
            Лучшее предсказанное значение.
        """
        p = a + b - c
        pa = abs(p - a)
        pb = abs(p - b)
        pc = abs(p - c)

        if pa <= pb and pa <= pc:
            return a
        elif pb <= pc:
            return b
        else:
            return c

    def _reconstruct(self,
                     raw: bytes,
                     width: int,
                     height: int,
                     color_type: int,
                     palette: bytes) -> List[List[int]]:
        """Дефильтрует байты PNG и переводит их в матрицу оттенков серого.

        Args:
            raw: Распакованные байты изображения.
            width: Ширина изображения.
            height: Высота изображения.
            color_type: Тип цвета PNG (0,2,3,6).
            palette: Данные палитры для color_type=3.

        Returns:
            Двумерный список значений яркости.

        Raises:
            ValueError: При неподдерживаемом color_type.
        """
        pixels = []

        if color_type == 0:
            bpp = 1
        elif color_type == 2:
            bpp = 3
        elif color_type == 3:
            bpp = 1
        elif color_type == 6:
            bpp = 4
        else:
            raise ValueError(f"неподдерживаемый color_type: {color_type}")

        stride = width * bpp
        i = 0
        prev_row = [0] * stride

        for _ in range(height):
            filter_type = raw[i]
            i += 1

            row = list(raw[i:i + stride])
            i += stride

            if filter_type == 0:
                pass
            elif filter_type == 1:
                for j in range(bpp, len(row)):
                    row[j] = (row[j] + row[j - bpp]) % 256
            elif filter_type == 2:
                for j in range(len(row)):
                    row[j] = (row[j] + prev_row[j]) % 256
            elif filter_type == 3:
                for j in range(len(row)):
                    left = row[j - bpp] if j >= bpp else 0
                    up = prev_row[j]
                    row[j] = (row[j] + (left + up) // 2) % 256
            elif filter_type == 4:
                for j in range(len(row)):
                    left = row[j - bpp] if j >= bpp else 0
                    up = prev_row[j]
                    up_left = prev_row[j - bpp] if j >= bpp else 0
                    paeth = self._paeth_predictor(left, up, up_left)
                    row[j] = (row[j] + paeth) % 256

            prev_row = row

            line = []
            for x in range(width):
                if color_type == 0:
                    line.append(row[x])
                elif color_type == 2:
                    r = row[x * 3]
                    g = row[x * 3 + 1]
                    b = row[x * 3 + 2]
                    gray = int(0.299 * r + 0.587 * g + 0.114 * b)
                    line.append(gray)
                elif color_type == 3:
                    idx = row[x]
                    r = palette[idx * 3]
                    g = palette[idx * 3 + 1]
                    b = palette[idx * 3 + 2]
                    gray = int(0.299 * r + 0.587 * g + 0.114 * b)
                    line.append(gray)
                elif color_type == 6:
                    r = row[x * 4]
                    g = row[x * 4 + 1]
                    b = row[x * 4 + 2]
                    gray = int(0.299 * r + 0.587 * g + 0.114 * b)
                    line.append(gray)

            pixels.append(line)

        return pixels

    def resize_image(self, image: Image, width: int) -> Image:
        """Пропорционально изменяет размер изображения.

        Args:
            image: Исходный объект Image.
            width: Целевая ширина в пикселях.

        Returns:
            Новый объект Image с изменённым размером.
        """
        ratio = image.height / image.width
        height = int(width * ratio * 0.45)

        new_pixels = []

        for y in range(height):
            row = []
            for x in range(width):
                src_x = int(x * image.width / width)
                src_y = int(y * image.height / height)
                row.append(image.pixels[src_y][src_x])
            new_pixels.append(row)

        return Image(width, height, new_pixels)
