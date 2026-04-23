from PIL import Image

class ImageProcessor:
    def load_image(self, path):
        return Image.open(path)

    def convert_to_grayscale(self, image):
        return image.convert("L")

    def resize_image(self, image, width):
        ratio = image.height / image.width
        height = int(width * ratio * 0.55)
        return image.resize((width, height))