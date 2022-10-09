import os
from pathlib import Path
from typing import Iterable, List, Optional

import numpy as np
import cv2
import face_recognition


class FaceRecognition:
    """Class responsible for detection of faces in an image."""
    @staticmethod
    def face_match(
        *, known_face_encodings: np.ndarray, face_encoding_to_check: np.ndarray, tolerance: float = 0.5
    ) -> bool:
        """Verify if a known face encoding matches a captured face encoding."""
        if face_recognition.compare_faces(
            known_face_encodings, face_encoding_to_check, tolerance
        )[0]:
            return True
        else:
            return False

    @classmethod
    def face_encodings(cls, image: np.ndarray, face_location: Optional[Iterable[float]] = None) -> np.ndarray:
        """The encoding of a portion of an image which contains a face."""
        return face_recognition.face_encodings(image, face_location)[0]

    @staticmethod
    def face_locations(image: np.ndarray) -> List[float]:
        """List of areas on an image where a face was detected."""
        return face_recognition.face_locations(image)

    @staticmethod
    def draw_bounding_box(face_location: Iterable[float], image: np.ndarray) -> None:
        """Draw a bounding box around a detected face on the image itself."""
        (top, right, bottom, left) = face_location
        cv2.rectangle(image, (left, top), (right, bottom), (0, 0, 255), 2)
