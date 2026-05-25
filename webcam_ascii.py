import cv2
import numpy as np
from typing import List, Tuple
from ASCII_converter import ASCIIConverter


class WebcamASCII:
    """Захватчик видеопотока веб-камеры для интерактивного рендеринга ASCII."""

    def __init__(self, width: int = 140, charset: str = "standard") -> None:
        """Настраивает параметры ширины кадра и загрузчик набора символов."""
        self.base_width: int = width
        self.converter: ASCIIConverter = ASCIIConverter()
        self.charset: str = charset
        self.window_name: str = "ascii webcam"

    def _resize_frame(self, frame: np.ndarray, width: int) -> np.ndarray:
        """Пропорционально уменьшает кадр с учетом соотношения сторон шрифта."""
        h, w = frame.shape
        ratio = h / w
        new_h = int(width * ratio * 0.55)
        return cv2.resize(frame, (width, new_h))

    def _ascii_to_image(self, ascii_lines: List[str]) -> np.ndarray:
        """Отрисовывает текстовые строки ASCII на графическом холсте OpenCV."""
        font = cv2.FONT_HERSHEY_SIMPLEX
        cell_w = 8
        cell_h = 12
        h = len(ascii_lines) * cell_h
        w = len(ascii_lines[0]) * cell_w
        img = np.ones((h, w, 3), dtype=np.uint8) * 255

        for y, line in enumerate(ascii_lines):
            for x, ch in enumerate(line):
                cv2.putText(
                    img, ch, (x * cell_w, (y + 1) * cell_h),
                    font, 0.55, (0, 0, 0), 1, cv2.LINE_AA)
        return img

    def _get_window_size(self) -> Tuple[int, int]:
        """Возвращает текущие ширину и высоту активного окна OpenCV."""
        x, y, w, h = cv2.getWindowImageRect(self.window_name)
        return w, h

    def run(self) -> None:
        """Запускает бесконечный цикл обработки кадров с веб-камеры."""
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("камера не открылась")
            return

        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        charset = self.converter.load_charset(self.charset)

        while True:
            if cv2.getWindowProperty(self.window_name, cv2.WND_PROP_VISIBLE) < 1:
                break

            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.flip(gray, 1)
            resized = self._resize_frame(gray, self.base_width)

            ascii_lines = []
            for y in range(resized.shape[0]):
                line = ""
                for x in range(resized.shape[1]):
                    brightness = resized[y, x]
                    idx = int(brightness / 255 * (len(charset) - 1))
                    line += charset[idx]
                ascii_lines.append(line)

            ascii_img = self._ascii_to_image(ascii_lines)

            try:
                win_w, win_h = self._get_window_size()
                if win_w > 50 and win_h > 50:
                    ascii_img = cv2.resize(ascii_img, (win_w, win_h))
            except cv2.error:
                break

            cv2.imshow(self.window_name, ascii_img)

            if cv2.waitKey(1) & 0xFF == 27:
                break

        cap.release()
        cv2.destroyAllWindows()