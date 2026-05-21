import sys
from image_processor import ImageProcessor
from ASCII_converter import ASCIIConverter
from io_handler import IOHandler
from webcam_ascii import WebcamASCII


class ASCIIApp:
    def __init__(self):
        self.io = IOHandler()
        self.processor = ImageProcessor()
        self.converter = ASCIIConverter()

    def run(self):
        try:
            args = self.io.parse()

            if args.webcam:
                cam = WebcamASCII(width=300, charset=args.charset)
                cam.run()
                return

            if not args.input:
                raise ValueError("укажи -i или --webcam")

            image = self.processor.load_image(args.input)
            resized = self.processor.resize_image(image, width=100)

            ascii_art = self.converter.convert_to_ascii(resized, args.charset)

            if args.output:
                self.io.save_to_file(ascii_art, args.output)
                print(f"успешно сохранено: {args.output}")
            else:
                self.io.print_to_console(ascii_art)

        except Exception as e:
            print(f"ошибка: {e}")
            sys.exit(1)