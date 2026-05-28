from typing import Dict, Any


class ASCIIConverter:
    """Преобразователь пикселей изображения в текстовые символы."""

    def load_charset(self, name: str) -> str:
        """Загружает набор символов из пресета или внешнего файла."""
        try:
            with open(name, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception:
            pass

        charsets: Dict[str, str] = {
            "standard": "@%#*+=-:. ",
            "detailed": (
                "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/"
                "\\|()1{}[]?-_+~<>i!lI;:,\"^`'. "
            ),
            "blocks": "█▓▒░ ",
            "simple": " .:-=+*#%@"
        }

        if name in charsets:
            return charsets[name]

        return charsets["standard"]

    def pixel_to_char(self, brightness: int, charset: str) -> str:
        """Сопоставляет значение яркости пикселя с символом из набора."""
        if len(charset) == 0:
            return " "
        index = int(brightness * (len(charset) - 1) / 255)
        return charset[index]

    def convert_to_ascii(self, image: Any, charset_name: str) -> str:
        """Конвертирует объект изображения в итоговую строку ASCII-арта."""
        charset = self.load_charset(charset_name)
        ascii_lines = []

        for y in range(image.height):
            line = ""
            for x in range(image.width):
                brightness = image.getpixel((x, y))
                brightness = max(0, min(255, brightness))
                line += self.pixel_to_char(brightness, charset)
            ascii_lines.append(line)

        return "\n".join(ascii_lines)
