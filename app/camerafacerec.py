from collections import deque
from threading import Thread

from app.camera2 import Camera
from app.facerec import FaceRecognition


class CamFaceRec:
    def __init__(self):
        self.cam = Camera()
        self.cam.start_thread()
        self.face_rec = FaceRecognition()
        self.stopped = False
        self.attr_deque = deque(maxlen=5)

        self.img = None
        self.face_locations = None
        self.face_count = None
        

    def _start_thread(self):
        Thread(target=self.face_read, args=()).start()
        return self

    def _stop_thread(self):
        self.stopped = True

    def __enter__(self):
        self._start_thread()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._stop_thread()


    def load_facerec_attrs(self):
        if self.deque_not_empty:
            (
                self.img,
                self.face_locations,
                self.face_count,
            ) = self.attr_deque.pop()
        else:
            raise RuntimeError("attr_deque empty")

    def refresh(self):
        self.load_facerec_attrs()

    def face_read(self):
        self.img_bbox = self.cam.feed()
        while True:
            if self.stopped:
                self.cam.stop()
                return
            self._img = self._img_bbox = self.cam.feed()
            self._face_locations = self.face_rec.face_locations(self.cam.reduce_framesize(self._img))
            self._face_locations = self.scale_face_locations(self._face_locations)

            if len(self._face_locations) > 0:
                for face_loc in self._face_locations:
                    self.face_rec.draw_bounding_box(face_loc, self._img_bbox)
            self.img_bbox = self._img_bbox
            self.attr_deque.append(
                [self._img, self._face_locations, len(self._face_locations)]
            )

    def deque_not_empty(self):
        return True if len(self.attr_deque) > 0 else False

    def face_encodings(self):
        return self.face_rec.face_encodings(self.img, [self.face_locations[0]])

    @staticmethod
    def scale_face_locations(face_locations):
        """
        Scale back up face locations since the frame when framesize is reduced
        """
        resized_face_locations = []
        for face_loc in face_locations:
            (top, right, bottom, left) = face_loc
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            resized_face_locations.append(tuple([top, right, bottom, left]))
        
        return resized_face_locations