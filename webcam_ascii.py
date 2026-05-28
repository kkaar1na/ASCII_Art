from typing import List, Tuple

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    try:
        import numpy as np
    except ImportError:
        np = None

from ASCII_converter import ASCIIConverter


class WebcamASCII:
    """Класс для захвата видеопотока и отображения его в виде ASCII-арта.

    Attributes:
        base_width: Базовая ширина для текстового кадра.
        converter: Конвертер для работы со шрифтами и наборами.
        charset: Имя или путь к набору символов.
        window_name: Название окна вывода OpenCV.
    """

    def __init__(self, width: int = 140, charset: str = "standard") -> None:
        """Инициализирует экземпляр WebcamASCII.

        Args:
            width (int): Ширина выходящего ASCII-изображения.
            charset (str): Название встроенного набора символов или
                путь к текстовому файлу.
        """
        self.base_width = width
        self.converter = ASCIIConverter()
        self.charset = charset
        self.window_name = "ascii webcam"

    def _resize_frame(self, frame, width: int):
        """Изменяет размер кадра.

        Args:
            frame (numpy.ndarray): Исходный кадр изображения.
            width (int): ширина для изменения размера.

        Returns:
            numpy.ndarray: Измененный в размерах кадр или исходный кадр,
                если библиотеки недоступны.
        """
        if not CV2_AVAILABLE or np is None:
            return frame
        h, w = frame.shape
        ratio = h / w
        new_h = int(width * ratio * 0.55)
        return cv2.resize(frame, (width, new_h))

    def _ascii_to_image(self, ascii_lines: List[str]):
        """Конвертирует список текстовых строк ASCII-арта в изображение.

        Args:
            ascii_lines (List[str]): Список строк, содержащих символы ASCII.

        Returns:
            numpy.ndarray: Трехканальное BGR-изображение с текстом,
                либо None, если библиотеки недоступны.
        """
        if not CV2_AVAILABLE or np is None:
            return None
        font = cv2.FONT_HERSHEY_SIMPLEX
        cell_w = 8
        cell_h = 12
        h = len(ascii_lines) * cell_h
        w = len(ascii_lines[0]) * cell_w if ascii_lines else 0
        img = np.ones((h, w, 3), dtype=np.uint8) * 255

        for y, line in enumerate(ascii_lines):
            for x, ch in enumerate(line):
                cv2.putText(
                    img, ch, (x * cell_w, (y + 1) * cell_h),
                    font, 0.55, (0, 0, 0), 1, cv2.LINE_AA)
        return img

    def _get_window_size(self) -> Tuple[int, int]:
        """Возвращает текущие размеры окна отображения OpenCV.

        Returns:
            Tuple[int, int]: Кортеж вида (ширина, высота) в пикселях.
                Возвращает (0, 0) в случае ошибки или если окно не найдено.
        """
        if not CV2_AVAILABLE:
            return 0, 0
        try:
            x, y, w, h = cv2.getWindowImageRect(self.window_name)
            return w, h
        except Exception:
            return 0, 0

    def run(self) -> None:
        """Запускает бесконечный цикл обработки видеопотока с веб-камеры."""
        if not CV2_AVAILABLE:
            print("OpenCV не установлен")
            return

        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("камера не открылась")
            return

        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        charset = self.converter.load_charset(self.charset)

        while True:
            try:
                if cv2.getWindowProperty(
                        self.window_name, cv2.WND_PROP_VISIBLE) < 1:
                    break
            except Exception:
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
                if win_w > 50 and win_h > 50 and ascii_img is not None:
                    ascii_img = cv2.resize(ascii_img, (win_w, win_h))
            except Exception:
                break

            cv2.imshow(self.window_name, ascii_img)

            if cv2.waitKey(1) & 0xFF == 27:
                break

        cap.release()
        cv2.destroyAllWindows()
