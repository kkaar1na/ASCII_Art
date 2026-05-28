import unittest
from unittest.mock import patch, MagicMock
import main


class TestMainEntryPoint(unittest.TestCase):
    @patch("main.ASCIIAppGUI")
    @patch("main.QApplication")
    @patch("main.sys.exit")
    def test_main_initializes_and_starts_qt_app(
            self, mock_exit, mock_app_class, mock_gui_class) -> None:
        mock_app_instance = MagicMock()
        mock_app_class.return_value = mock_app_instance
        mock_gui_instance = MagicMock()
        mock_gui_class.return_value = mock_gui_instance

        main.main()

        mock_app_class.assert_called_once()
        mock_gui_class.assert_called_once()
        mock_gui_instance.show.assert_called_once()
        mock_app_instance.exec.assert_called_once()
        mock_exit.assert_called_once()
