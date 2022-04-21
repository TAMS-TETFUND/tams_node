from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2


class Camera(PiCamera):
    def __init__(self):
        super(Camera, self).__init__()
        self.resolution = (640, 480)
        self.framerate = 32

    @property
    def raw_capture(self, size=self.resolution):
        return PiRGBArray(self, size)

    def capture(self, format="bgr", use_video_port=True):
        for frame in self.capture_continuous(self.raw_capture, format=format, use_video_port=use_video_port):
            # image = frame.array
            return cv2.imencode('.png', frame)[1].tobytes()


            
    