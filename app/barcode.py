from typing import Any, Iterable
from typing_extensions import reveal_type

import numpy as np
import cv2
from pyzbar import pyzbar


class Barcode:
    @staticmethod
    def decode_image(image: Any) -> Iterable[pyzbar.Decoded]:
        """Decode a barcode image."""
        return pyzbar.decode(image)

    @staticmethod
    def decode_barcode(barcode: pyzbar.Decoded) -> str:
        """Get string representation of barcode"""
        return barcode.data.decode("utf-8")

    @staticmethod
    def draw_bounding_box(barcode: pyzbar.Decoded, image: np.ndarray) -> None:
        """Draw a bounding box around detected barcodes in an image."""
        (x, y, w, h) = barcode.rect
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
