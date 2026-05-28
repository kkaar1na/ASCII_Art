import sys
import unittest
from unittest.mock import MagicMock, patch
from ascii_app import ASCIIApp


class TestASCIIApp(unittest.TestCase):

    def setUp(self) -> None:
        self.app = ASCIIApp()
        self.app.io = MagicMock()
        self.app.processor = MagicMock()
        self.app.converter = MagicMock()

    def test_run_webcam_mode(self) -> None:
        mock_args = MagicMock()
        mock_args.webcam = True
        mock_args.charset = "standard"
        self.app.io.parse.return_value = mock_args

        with patch("ascii_app.WebcamASCII") as mock_webcam_class:
            mock_cam_instance = MagicMock()
            mock_webcam_class.return_value = mock_cam_instance

            self.app.run()

            mock_webcam_class.assert_called_once_with(
                width=300, charset="standard"
            )
            mock_cam_instance.run.assert_called_once()

    def test_run_no_input_and_no_webcam_error(self) -> None:
        mock_args = MagicMock()
        mock_args.webcam = False
        mock_args.input = ""
        self.app.io.parse.return_value = mock_args

        with patch("builtins.print") as mock_print, patch(
            "sys.exit"
        ) as mock_exit:
            self.app.run()
            mock_print.assert_called_with("ошибка: укажи -i или --webcam")
            mock_exit.assert_called_with(1)

    def test_run_console_output_success(self) -> None:
        mock_args = MagicMock()
        mock_args.webcam = False
        mock_args.input = "image.png"
        mock_args.charset = "standard"
        mock_args.output = None
        self.app.io.parse.return_value = mock_args

        mock_img = MagicMock()
        mock_resized = MagicMock()
        self.app.processor.load_image.return_value = mock_img
        self.app.processor.resize_image.return_value = mock_resized
        self.app.converter.convert_to_ascii.return_value = "ASCII_ART"

        self.app.run()

        self.app.processor.load_image.assert_called_once_with("image.png")
        self.app.processor.resize_image.assert_called_once_with(
            mock_img, width=100
        )
        self.app.converter.convert_to_ascii.assert_called_once_with(
            mock_resized, "standard"
        )
        self.app.io.print_to_console.assert_called_once_with("ASCII_ART")

    def test_run_file_output_success(self) -> None:
        mock_args = MagicMock()
        mock_args.webcam = False
        mock_args.input = "image.png"
        mock_args.charset = "standard"
        mock_args.output = "output.txt"
        self.app.io.parse.return_value = mock_args

        self.app.converter.convert_to_ascii.return_value = "ASCII_ART"

        with patch("builtins.print") as mock_print:
            self.app.run()
            self.app.io.save_to_file.assert_called_once_with(
                "ASCII_ART", "output.txt"
            )
            mock_print.assert_called_with("успешно сохранено: output.txt")

    def test_run_general_exception_handling(self) -> None:
        self.app.io.parse.side_effect = Exception("Fatal Error")

        with patch("builtins.print") as mock_print, patch(
            "sys.exit"
        ) as mock_exit:
            self.app.run()
            mock_print.assert_called_with("ошибка: Fatal Error")
            mock_exit.assert_called_with(1)


if __name__ == "__main__":
    unittest.main()
