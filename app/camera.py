import os
import time

from picamera import PiCamera
import cv2
import numpy as np

from app.basegui import BaseGUIWindow as bgw


class Camera(PiCamera):
    def __init__(self) -> None:
        super(Camera, self).__init__()
        self.resolution = (320, 240)
        self.framerate = 24
        time.sleep(1)

    def feed(self, format="bgr", use_video_port=True) -> np.array:
        output = np.empty((240, 320, 3), dtype=np.uint8)
        self.capture(output, "bgr", use_video_port=True)
        return output

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

    def save_feed(
        self, filename="demo_img", path=os.path.dirname("demo_images/")
    ):
        os.makedirs(path, exists_ok=True)
        cv2.imwrite(f"{path}/{filename}.png", self.feed())
        return self
