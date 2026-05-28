import sys
import unittest
from unittest.mock import MagicMock, mock_open, patch

if "cv2" not in sys.modules:
    sys.modules["cv2"] = MagicMock()
if "numpy" not in sys.modules:
    sys.modules["numpy"] = MagicMock()

import webcam_ascii

webcam_ascii.CV2_AVAILABLE = True

if not hasattr(webcam_ascii, "cv2") or webcam_ascii.cv2 is None:
    webcam_ascii.cv2 = sys.modules["cv2"]
if not hasattr(webcam_ascii, "np") or webcam_ascii.np is None:
    webcam_ascii.np = sys.modules["numpy"]


class DummyFrame:
    def __init__(self, shape):
        self.shape = shape
        self.dtype = "uint8"

    def __getitem__(self, item):
        return 0

    def __mul__(self, other):
        return self

    def __rmul__(self, other):
        return self


class TestWebcamASCIIFull(unittest.TestCase):

    def setUp(self) -> None:
        self.cam = webcam_ascii.WebcamASCII(120, "standard")
        self.f_2d = DummyFrame((100, 120))
        self.f_3d = DummyFrame((100, 120, 3))

    def test_init_with_builtin_charset(self) -> None:
        cam = webcam_ascii.WebcamASCII(80, "blocks")
        self.assertEqual(cam.base_width, 80)

    def test_init_with_file_charset(self) -> None:
        m_open = mock_open(read_data="XYZ")
        with patch("builtins.open", m_open):
            with patch("os.path.exists", return_value=True):
                cam = webcam_ascii.WebcamASCII(100, "c.txt")
                self.assertIsNotNone(cam.charset)

    def test_init_with_missing_file_charset(self) -> None:
        with patch("os.path.exists", return_value=False):
            cam = webcam_ascii.WebcamASCII(100, "m.txt")
            self.assertIsNotNone(cam.charset)

    def test_resize_frame_same_width(self) -> None:
        with patch.object(webcam_ascii.cv2, "resize") as m_res:
            m_res.return_value = self.f_2d
            resized = self.cam._resize_frame(self.f_2d, 120)
            self.assertIsNotNone(resized)

    def test_resize_frame_different_width(self) -> None:
        with patch.object(webcam_ascii.cv2, "resize") as m_res:
            m_res.return_value = self.f_2d
            resized = self.cam._resize_frame(self.f_2d, 100)
            self.assertIsNotNone(resized)

    def test_ascii_to_image_normal(self) -> None:
        with patch.object(webcam_ascii.np, "ones") as m_ones:
            m_ones.return_value = self.f_3d
            img = self.cam._ascii_to_image(["@@", "##"])
            self.assertIsNotNone(img)

    def test_ascii_to_image_empty(self) -> None:
        with patch.object(webcam_ascii.np, "ones") as m_ones:
            m_ones.return_value = self.f_3d
            img = self.cam._ascii_to_image([])
            self.assertIsNotNone(img)

    def test_get_window_size_default(self) -> None:
        with patch.object(webcam_ascii.cv2, "getWindowImageRect") as m_rect:
            m_rect.return_value = (0, 0, 0, 0)
            w, h = self.cam._get_window_size()
            self.assertEqual(w, 0)
            self.assertEqual(h, 0)

    def test_get_window_size_valid(self) -> None:
        with patch.object(webcam_ascii.cv2, "getWindowImageRect") as m_rect:
            m_rect.return_value = (10, 20, 800, 600)
            w, h = self.cam._get_window_size()
            self.assertEqual(w, 800)
            self.assertEqual(h, 600)

    def test_run_camera_cannot_open(self) -> None:
        mock_caps = MagicMock()
        mock_caps.isOpened.return_value = False
        with patch.object(webcam_ascii.cv2, "VideoCapture") as m_vc:
            m_vc.return_value = mock_caps
            with patch("builtins.print") as mock_print:
                self.cam.run()
                mock_print.assert_called_with("камера не открылась")

    def test_run_full_lifecycle(self) -> None:
        mock_caps = MagicMock()
        mock_caps.isOpened.return_value = True
        mock_caps.read.side_effect = [(True, self.f_3d), (False, None)]

        with patch.object(webcam_ascii.cv2, "VideoCapture") as m_vc, \
             patch.object(webcam_ascii.cv2, "namedWindow"), \
             patch.object(webcam_ascii.cv2, "getWindowProperty") as m_prop, \
             patch.object(webcam_ascii.cv2, "cvtColor") as m_cvt, \
             patch.object(webcam_ascii.cv2, "flip") as m_flip, \
             patch.object(webcam_ascii.cv2, "resize") as m_res, \
             patch.object(webcam_ascii.cv2, "imshow"), \
             patch.object(webcam_ascii.cv2, "waitKey") as m_key, \
             patch.object(self.cam, "_get_window_size") as m_size, \
             patch.object(self.cam, "_ascii_to_image") as m_img:

            m_vc.return_value = mock_caps
            m_prop.return_value = 1.0
            m_cvt.return_value = self.f_2d
            m_flip.return_value = self.f_2d
            m_res.return_value = self.f_2d
            m_size.return_value = (100, 100)
            m_img.return_value = self.f_3d
            m_key.return_value = 113

            self.cam.run()
            mock_caps.read.assert_called()
            mock_caps.release.assert_called_once()

    def test_run_termination_by_close(self) -> None:
        mock_caps = MagicMock()
        mock_caps.isOpened.return_value = True
        mock_caps.read.return_value = (True, self.f_3d)

        with patch.object(webcam_ascii.cv2, "VideoCapture") as m_vc, \
             patch.object(webcam_ascii.cv2, "namedWindow"), \
             patch.object(webcam_ascii.cv2, "getWindowProperty") as m_prop:

            m_vc.return_value = mock_caps
            m_prop.return_value = 0.0

            self.cam.run()
            mock_caps.release.assert_called_once()


if __name__ == "__main__":
    unittest.main()
