from collections import deque
from threading import Thread
from typing import Any, Deque, Iterable, List, Optional, Tuple

from app.camera2 import Camera
from app.facerec import FaceRecognition


class CamFaceRec:
    """Class that handles applying face rec on camera feed.

    The class is composed of both the app.camera.Camera class and
    the app.facerec.FaceRecognition class.

    The class spins up a thread for processing the face rec operations
    as not to block the main thread of the application calling it.
    """

    def __init__(self) -> None:
        self.img_bbox = None
        self._face_locations: Iterable[Tuple[float, ...]] = []
        self._img = None
        self._img_bbox = None
        self.cam = Camera()
        self.cam.start_thread()
        self.face_rec = FaceRecognition()
        self.stopped = False
        self.attr_deque: Deque = deque(maxlen=5)

        self.img = None
        self.face_locations = None
        self.face_count = None

    def _start_thread(self) -> "CamFaceRec":
        """Start thread for processing face rec operations on images."""
        Thread(target=self.face_read, args=()).start()
        return self

    def _stop_thread(self) -> None:
        self.stopped = True

    def __enter__(self) -> "CamFaceRec":
        """The entry point of class context manager."""
        self._start_thread()
        return self

    def __exit__(
        self, exc_type: Any, exc_value: Any, exc_traceback: Any
    ) -> Optional[bool]:
        """Exit operations of class context manager."""
        self._stop_thread()

    def load_facerec_attrs(self) -> None:
        """Pop an entry from attr_deque.

        A single entry in attr_deque holds an image, location of faces
        detected in the image, and the number of faces detected in the
        image.
        """
        if self.deque_not_empty:
            (
                self.img,
                self.face_locations,
                self.face_count,
            ) = self.attr_deque.pop()
        else:
            raise RuntimeError("attr_deque empty")

    def face_read(self) -> None:
        """Detect face locations in image feed from camera"""
        self.img_bbox = self.cam.feed()
        while True:
            if self.stopped:
                self.cam.stop()
                return
            self._img = self._img_bbox = self.cam.feed()
            self._face_locations = self.face_rec.face_locations(
                self.cam.reduce_framesize(self._img)
            )
            self._face_locations = self.scale_face_locations(
                self._face_locations
            )

            if self._face_locations:
                for face_loc in self._face_locations:
                    self.face_rec.draw_bounding_box(face_loc, self._img_bbox)
            self.img_bbox = self._img_bbox
            self.attr_deque.append(
                [self._img, self._face_locations, len(self._face_locations)]
            )

    def deque_not_empty(self) -> bool:
        """Check if deque is not empty."""
        return True if len(self.attr_deque) > 0 else False

    def face_encodings(self):
        """Get face encodings for a given face location.

        Calls the face_encoding method from the FaceRec class component.
        """
        return self.face_rec.face_encodings(self.img, [self.face_locations[0]])

    @staticmethod
    def scale_face_locations(
        face_locations: Iterable[Tuple[float, ...]]
    ) -> List[Tuple[float, ...]]:
        """Scale back up face locations since when framesize is restored."""
        resized_face_locations = []
        for face_loc in face_locations:
            (top, right, bottom, left) = face_loc
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            resized_face_locations.append(tuple([top, right, bottom, left]))

        return resized_face_locations
