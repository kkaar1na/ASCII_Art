import sys
from PyQt6.QtWidgets import QApplication
from gui_app import ASCIIAppGUI


def main() -> None:
    """Запускает цикл обработки событий графического интерфейса.

    Args:
        None

    Returns:
        None
    """
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = ASCIIAppGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
