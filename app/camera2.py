import os
from threading import Thread
from typing import Optional
from typing_extensions import Self

import numpy as np
import cv2

from app.basegui import BaseGUIWindow


class Camera:
    """The camera class."""

    def __init__(self) -> None:
        self.camera_ok()
        self.cap = cv2.VideoCapture(0)
        self.stopped = False
        (self.grabbed, self.frame) = self.cap.read()

    def __enter__(self) -> "Camera":
        self.start_thread()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback) -> Optional[bool]:
        self.stop()

    def start_thread(self) -> "Camera":
        """Start the thread to read frames from the video stream"""
        Thread(target=self.update, args=()).start()
        return self

    def update(self) -> None:
        """Keeps looping infinitely until the thread is stopped."""
        while True:
            if self.stopped:
                self.cap.release()
                return

            (self.grabbed, self.frame) = self.cap.read()

    def camera_ok(self) -> bool:
        """Check for presence of working camera.

        TODO: Current method implementation will not work for
        non-Unix OS's.
        """
        if os.path.exists("/dev/video0"):
            return True
        else:
            raise RuntimeError("Camera not available")

    def feed(self) -> np.ndarray:
        """Read from the camera."""
        if not self.grabbed:
            raise RuntimeError("Problem reading from camera")
        return self.frame

    def stop(self) -> None:
        """indicate that the thread should be stopped"""
        self.stopped = True

    @staticmethod
    def image_to_grayscale(img: np.ndarray) -> np.ndarray:
        """Convert image to grayscale. Purely for aesthetic reasons."""
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    @staticmethod
    def feed_to_bytes(img: np.ndarray) -> bytes:
        """Convert camera feed to bytes."""
        new_image_size = tuple(int(x * 0.6) for x in BaseGUIWindow.SCREEN_SIZE)
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

    @staticmethod
    def reduce_framesize(img: np.ndarray) -> np.ndarray:
        """Resize frame size for faster processing."""
        return cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
