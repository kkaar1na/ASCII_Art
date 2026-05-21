import unittest
from unittest.mock import patch, MagicMock
from webcam_ascii import WebcamASCII


class TestWebcamASCII(unittest.TestCase):

    @patch("webcam_ascii.cv2")
    def test_webcam_init(self, mock_cv2):
        try:
            WebcamASCII(width=100, charset="standard")
        except Exception as e:
            self.fail(f"Initialization raised an exception: {e}")

    @patch("webcam_ascii.cv2")
    def test_webcam_run_and_exit(self, mock_cv2):
        mock_video = MagicMock()
        mock_cv2.VideoCapture.return_value = mock_video
        mock_video.read.return_value = (False, None)

        cam = WebcamASCII(width=100, charset="standard")
        try:
            cam.run()
        except Exception as e:
            self.fail(f"Webcam run raised an exception: {e}")

        mock_cv2.VideoCapture.assert_called_once()
        mock_video.release.assert_called_once()


if __name__ == "__main__":
    unittest.main()