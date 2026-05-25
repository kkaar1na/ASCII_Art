import sys
from PyQt6.QtWidgets import QApplication
from gui_app import ASCIIAppGUI


def main() -> None:
    """Точка входа: запускает цикл обработки событий графического интерфейса."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = ASCIIAppGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()