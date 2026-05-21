class ASCIIConverter:
    def load_charset(self, name):
        try:
            with open(name, "r", encoding="utf-8") as f:
                return f.read().strip()
        except:
            pass

        charsets = {
            "standard": "@%#*+=-:. ",
            "detailed": "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. ",
            "blocks": "█▓▒░ ",
            "simple": " .:-=+*#%@"
        }

        if name in charsets:
            return charsets[name]

        return charsets["standard"]


    def pixel_to_char(self, brightness, charset):
        if len(charset) == 0:
            return " "
        index = int(brightness * (len(charset) - 1) / 255)
        return charset[index]

    def convert_to_ascii(self, image, charset_name):
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