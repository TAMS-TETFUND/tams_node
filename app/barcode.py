import cv2
from pyzbar import pyzbar

class Barcode:
    
    @staticmethod
    def decode_image(image):
        return pyzbar.decode(image)
    
    @staticmethod
    def decode_barcode(barcode):
        return barcode.data.decode('utf-8')

    @staticmethod
    def draw_bounding_box(barcode, image):
        (x, y, w, h) = barcode.rect
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 0, 255), 2)
