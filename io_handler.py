import argparse

class IOHandler:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="ASCII Art Converter")
        self._setup_arguments()

    def _setup_arguments(self):
        self.parser.add_argument("-i", "--input", required=True)
        self.parser.add_argument("-o", "--output")
        self.parser.add_argument("-c", "--charset", default="standard")

    def parse(self):
        return self.parser.parse_args()

    def print_to_console(self, ascii_art):
        print(ascii_art)

    def save_to_file(self, ascii_art, filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(ascii_art)