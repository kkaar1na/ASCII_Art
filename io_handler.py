import argparse

class IOHandler:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="конвертер изображений в ascii арт")
        self._setup_arguments()

    def _setup_arguments(self):
        self.parser.add_argument("-i", "--input", help="входной png файл")
        self.parser.add_argument("-o", "--output", help="выходной текстовый файл")
        self.parser.add_argument("-c", "--charset", default="standard", help="набор символов: standard, detailed, blocks, simple")
        self.parser.add_argument("--webcam", action="store_true", help="режим веб-камеры")

    def parse(self):
        return self.parser.parse_args()

    def print_to_console(self, ascii_art):
        print(ascii_art)

    def save_to_file(self, ascii_art, filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(ascii_art)