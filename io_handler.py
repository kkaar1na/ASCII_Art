import argparse


class IOHandler:
    """Обработчик аргументов командной строки и файлового ввода-вывода."""

    def __init__(self) -> None:
        """Инициализирует парсер и настраивает доступные флаги CLI."""
        self.parser: argparse.ArgumentParser = argparse.ArgumentParser(
            description="конвертер изображений в ascii арт"
        )
        self._setup_arguments()

    def _setup_arguments(self) -> None:
        """Конфигурирует параметры командной строки."""
        self.parser.add_argument("-i", "--input", help="входной png файл")
        self.parser.add_argument("-o", "--output", help="выходной текстовый файл")
        self.parser.add_argument("-c", "--charset", default="standard", help="набор символов")
        self.parser.add_argument("--webcam", action="store_true", help="режим веб-камеры")

    def parse(self) -> argparse.Namespace:
        """Разбирает и возвращает переданные аргументы командной строки."""
        return self.parser.parse_args()

    def print_to_console(self, ascii_art: str) -> None:
        """Выводит строку ASCII-арта в окно терминала."""
        print(ascii_art)

    def save_to_file(self, ascii_art: str, filepath: str) -> None:
        """Сохраняет строку ASCII-арта в текстовый файл."""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(ascii_art)