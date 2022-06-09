import os
from threading import Thread

import cv2

from app.basegui import BaseGUIWindow as bgw


class Camera:
    FRAME_WIDTH = 1280
    FRAME_HEIGHT = 720

    def __init__(self):
        self.camera_ok()
        self.cap = cv2.VideoCapture(0)
        # self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.FRAME_WIDTH)
        # self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.FRAME_HEIGHT)
        (self.grabbed, self.frame) = self.cap.read()

        self.stopped = False

    def __enter__(self):
        self.start_thread()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.stop()

    def start_thread(self):
        # start the thread to read frames from the video stream
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        while True:
            if self.stopped:
                return
            
            (self.grabbed, self.frame) = self.cap.read()

    def camera_ok(self):
        """method to check for camera presence. On posix systems"""
        if os.path.exists("/dev/video0"):
            return True
        else:
            raise RuntimeError("Camera not installed")

    def feed(self):
        if not self.grabbed:
            raise RuntimeError("Problem reading from camera")
        return self.frame
    
    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True

    @staticmethod
    def image_to_grayscale(img):
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


    @staticmethod
    def feed_to_bytes(img):
        new_image_size = tuple(int(x * 0.6) for x in bgw.SCREEN_SIZE)
        return cv2.imencode(
            ".png",
            cv2.resize(
                img,
                dsize=new_image_size,
                fx=0.6,
                fy=0.6,
                interpolation=cv2.INTER_AREA,
            ),
        )[1].tobytes()
