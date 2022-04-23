import time

from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import numpy as np

class Camera(PiCamera):
    def __init__(self):
        super(Camera, self).__init__()
        self.resolution = (320, 240)
        self.framerate = 24
        time.sleep(2)

    def feed(self, format="bgr", use_video_port=True):
            output = np.empty((240, 320, 3), dtype=np.uint8)
            self.capture(output, 'rgb', use_video_port=True)

            return cv2.imencode('.png', output)[1].tobytes()