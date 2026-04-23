from PIL import Image

class ASCIIConverter:
    def load_charset(self, name):
        if name in ["standard", "detailed", "blocks"]:
            try:
                with open(f"charsets/{name}", "r", encoding="utf-8") as f:
                    return f.read().strip()
            except:
                return "@%#*+=-:. "
        else:
            try:
                with open(name, "r", encoding="utf-8") as f:
                    return f.read().strip()
            except:
                return "@%#*+=-:. "

    def pixel_to_char(self, brightness, charset):
        index = int(brightness / 255 * (len(charset) - 1))
        return charset[index]

    def convert_to_ascii(self, image, charset_name):
        charset = self.load_charset(charset_name)
        ascii_lines = []
        for y in range(image.height):
            line = ""
            for x in range(image.width):
                brightness = image.getpixel((x, y))
                line += self.pixel_to_char(brightness, charset)
            ascii_lines.append(line)
        return "\n".join(ascii_lines)