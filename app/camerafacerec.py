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

    def _start_thread(self):
        Thread(target=self.face_read, args=()).start()
        return self
    
    def _stop_thread(self):
        self.stopped = True

    def __enter__(self):
        self._start_thread()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.cam.stop()
        self._stop_thread()
    
    def start_deque(self):
        if self.deque_not_empty:
            self.img, self.face_locations, self.face_count = self.attr_deque.pop()
        else:
            raise RuntimeError("attr_deque empty")

    def refresh(self):
        self.start_deque()

    def face_read(self):
        self.img_bbox = self.cam.feed()
        while True:
            if self.stopped:
                return
            self._img = self._img_bbox = self.cam.feed()
            self._face_locations = self.face_rec.face_locations(self._img)

            if len(self._face_locations) > 0:
                for face_loc in self._face_locations:
                    self.face_rec.draw_bounding_box(face_loc, self._img_bbox)
            self.img_bbox = self._img_bbox
            self.attr_deque.append([self._img, self._face_locations, len(self._face_locations)])

    def deque_not_empty(self):
        return True if len(self.attr_deque) > 0 else False
    
    # def face_count(self, image=None):
    #     if image:
    #         return len(self.face_rec.face_locations(image))
    #     else:
    #         return len(self.face_locations)

    def face_encodings(self):
        return self.face_rec.face_encodings(self.img, [self.face_locations[0]])

# The issue here is that the state of the face_count method is
# changing everytime the method is called
# also the state of self.img is changing which means that self.locations
# is also changing very rapidly?
# it is unstable for the clients of the class to access these attributes
# directly. A deque needs to exist to ensure that img, face_locations,
#  img_bbox, and consequently face_encodings will be consistent.