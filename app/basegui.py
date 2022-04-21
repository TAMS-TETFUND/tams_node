import io
import json
import os
from pathlib import Path
import base64

from PIL import Image, ImageDraw, ImageTk, ImageFont
import PySimpleGUI as sg


# set application-wide theme
sg.theme("LightGreen6")


class BaseGUIWindow:
    SCREEN_SIZE = (480, 320)
    ICON_SIZE = {"h": 125, "w": 70}
    ICON_BUTTON_COLOR = (
        sg.theme_background_color(),
        sg.theme_background_color(),
    )

    @staticmethod
    def confirm_exit():
        clicked = sg.popup_ok_cancel(
            "System will shutdown. Do you want to continue?",
            title="Shutdown",
            keep_on_top=True,
        )
        if clicked == "OK":
            return False
        if clicked in ("Cancel", None):
            pass
        return True

    @staticmethod
    def _image_file_to_bytes(image64, size):
        image_file = io.BytesIO(base64.b64decode(image64))
        img = Image.open(image_file)
        img.thumbnail(size, Image.ANTIALIAS)
        bio = io.BytesIO()
        img.save(bio, format="PNG")
        imgbytes = bio.getvalue()
        return imgbytes

    @classmethod
    def get_icon(cls, icon_name, size_ratio=1):
        icons_path = os.path.join(
            Path(os.path.abspath(__file__)).parent, "icons.json"
        )
        with open(icons_path, "r") as data:
            icon_dict = json.loads(data.read())
        icon = icon_dict[icon_name]
        return cls._image_file_to_bytes(
            icon,
            (cls.ICON_SIZE["h"] * size_ratio, cls.ICON_SIZE["w"] * size_ratio),
        )

    @classmethod
    def window_init_dict(cls):
        init_dict = {
            "size": cls.SCREEN_SIZE,
            "no_titlebar": True,
            "keep_on_top": True,
            "grab_anywhere": True,
            "finalize": True,
        }
        return init_dict