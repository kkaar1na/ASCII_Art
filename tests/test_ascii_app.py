import unittest
from unittest.mock import patch, MagicMock
from ascii_app import ASCIIApp


class TestASCIIApp(unittest.TestCase):

    def setUp(self):
        self.app = ASCIIApp()

    @patch("ascii_app.WebcamASCII")
    def test_run_webcam_mode(self, mock_webcam_class):
        mock_cam_instance = MagicMock()
        mock_webcam_class.return_value = mock_cam_instance

        self.app.io.parse = MagicMock(return_value=MagicMock(webcam=True, charset="standard"))

        self.app.run()

        mock_webcam_class.assert_called_once_with(width=300, charset="standard")
        mock_cam_instance.run.assert_called_once()

    def test_run_no_input_and_no_webcam_raises_error(self):
        self.app.io.parse = MagicMock(return_value=MagicMock(webcam=False, input=None))

        with patch("builtins.print") as mock_print, patch("sys.exit") as mock_exit:
            self.app.run()
            mock_print.assert_called_once_with("ошибка: укажи -i или --webcam")
            mock_exit.assert_called_once_with(1)

    def test_run_to_console_success(self):
        mock_args = MagicMock(webcam=False, input="img.png", charset="standard", output=None)
        self.app.io.parse = MagicMock(return_value=mock_args)

        mock_image = MagicMock()
        mock_resized = MagicMock()

        self.app.processor.load_image = MagicMock(return_value=mock_image)
        self.app.processor.resize_image = MagicMock(return_value=mock_resized)
        self.app.converter.convert_to_ascii = MagicMock(return_value="ascii_result")
        self.app.io.print_to_console = MagicMock()

        self.app.run()

        self.app.processor.load_image.assert_called_once_with("img.png")
        self.app.processor.resize_image.assert_called_once_with(mock_image, width=100)
        self.app.converter.convert_to_ascii.assert_called_once_with(mock_resized, "standard")
        self.app.io.print_to_console.assert_called_once_with("ascii_result")

    def test_run_to_file_success(self):
        mock_args = MagicMock(webcam=False, input="img.png", charset="standard", output="out.txt")
        self.app.io.parse = MagicMock(return_value=mock_args)

        self.app.processor.load_image = MagicMock()
        self.app.processor.resize_image = MagicMock()
        self.app.converter.convert_to_ascii = MagicMock(return_value="ascii_result")
        self.app.io.save_to_file = MagicMock()

        with patch("builtins.print") as mock_print:
            self.app.run()
            self.app.io.save_to_file.assert_called_once_with("ascii_result", "out.txt")
            mock_print.assert_called_once_with("успешно сохранено: out.txt")


if __name__ == "__main__":
    unittest.main()