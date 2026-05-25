import unittest
from unittest.mock import patch, MagicMock
import numpy as np
from webcam_ascii import WebcamASCII

class TestWebcamASCII(unittest.TestCase):
    @patch("webcam_ascii.cv2")
    def test_webcam_init(self, mock_cv2) -> None:
        """Проверяет успешную инициализацию объекта WebcamASCII без генерации исключений."""
        try:
            WebcamASCII(width=100, charset="standard")
        except Exception as e:
            self.fail(f"Initialization raised an exception: {e}")

    @patch("webcam_ascii.cv2")
    def test_webcam_run_and_exit(self, mock_cv2) -> None:
        """Проверяет освобождение ресурсов захвата видео в случае, если первый кадр оказался пустым."""
        mock_video = MagicMock()
        mock_cv2.VideoCapture.return_value = mock_video
        mock_video.read.return_value = (False, None)
        mock_cv2.getWindowProperty.return_value = 1.0

        cam = WebcamASCII(width=100, charset="standard")
        try:
            cam.run()
        except Exception as e:
            self.fail(f"Webcam run raised an exception: {e}")

        mock_cv2.VideoCapture.assert_called_once()
        mock_video.release.assert_called_once()

    def test_resize_frame(self) -> None:
        """Тестирует сохранение новой пропорциональной ширины кадра при масштабировании."""
        cam = WebcamASCII(width=100, charset="standard")
        fake_frame = np.zeros((200, 200), dtype=np.uint8)
        resized = cam._resize_frame(fake_frame, 100)
        self.assertEqual(resized.shape[1], 100)

    def test_ascii_to_image(self) -> None:
        """Проверяет генерацию трехканальной графической матрицы (изображения) на базе текстовых строк."""
        cam = WebcamASCII(width=100, charset="standard")
        lines = ["@@@@", "####"]
        img = cam._ascii_to_image(lines)
        self.assertIsInstance(img, np.ndarray)
        self.assertEqual(len(img.shape), 3)

    @patch("webcam_ascii.cv2")
    def test_webcam_run_full_loop_and_escape(self, mock_cv2) -> None:
        """Проверяет корректность одной итерации обработки кадра из видеопотока и выхода по отсутствию следующего."""
        mock_video = MagicMock()
        mock_cv2.VideoCapture.return_value = mock_video

        fake_bgr_frame = np.zeros((100, 100, 3), dtype=np.uint8)
        fake_gray_frame = np.zeros((100, 100), dtype=np.uint8)

        mock_video.read.side_effect = [(True, fake_bgr_frame), (False, None)]
        mock_cv2.cvtColor.return_value = fake_gray_frame
        mock_cv2.flip.return_value = fake_gray_frame
        mock_cv2.getWindowProperty.return_value = 1.0
        mock_cv2.getWindowImageRect.return_value = (0, 0, 100, 100)

        cam = WebcamASCII(width=100, charset="standard")
        cam.run()

        mock_cv2.cvtColor.assert_called_once_with(fake_bgr_frame, mock_cv2.COLOR_BGR2GRAY)
        mock_cv2.flip.assert_called_once_with(fake_gray_frame, 1)