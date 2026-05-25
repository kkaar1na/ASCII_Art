import sys
from image_processor import ImageProcessor
from ASCII_converter import ASCIIConverter
from io_handler import IOHandler
from webcam_ascii import WebcamASCII


class ASCIIApp:
    """Консольное приложение для конвертации изображений в ASCII-арт."""

    def __init__(self) -> None:
        """Инициализирует компоненты ввода-вывода, обработки и конвертации."""
        self.io: IOHandler = IOHandler()
        self.processor: ImageProcessor = ImageProcessor()
        self.converter: ASCIIConverter = ASCIIConverter()

    def run(self) -> None:
        """Запускает основной цикл обработки и конвертации по аргументам CLI."""
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