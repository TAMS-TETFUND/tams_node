import os
from pathlib import Path
from typing import List

import cv2
import face_recognition


class FaceRecognition:
    @staticmethod
    def face_match(
        *, known_face_encodings, face_encoding_to_check, tolerance=0.4
    ):
        if face_recognition.compare_faces(
            known_face_encodings, face_encoding_to_check, tolerance
        )[0]:
            return True
        else:
            return False

    @classmethod
    def face_encodings(cls, image, face_location=None):
        return face_recognition.face_encodings(image, face_location)[0]

    @staticmethod
    def face_locations(image) -> List:
        return face_recognition.face_locations(image)

    @staticmethod
    def draw_bounding_box(face_location, image):
        (top, right, bottom, left) = face_location
        cv2.rectangle(image, (left, top), (right, bottom), (0, 0, 255), 2)
