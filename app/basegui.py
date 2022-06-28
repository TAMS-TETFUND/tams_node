import io
import json
import os
from pathlib import Path
import base64

from PIL import Image
import PySimpleGUI as sg

# set application-wide theme
sg.theme("LightGreen6")


class BaseGUIWindow:
    COMBO_DEFAULT = "--select--"
    SCREEN_SIZE = (480, 320)
    ICON_SIZE = {"h": 125, "w": 70}
    ICON_BUTTON_COLOR = (
        sg.theme_background_color(),
        sg.theme_background_color(),
    )

    @classmethod
    def window(cls):
        raise NotImplementedError

    @classmethod
    def loop(cls, window, event, values):
        raise NotImplementedError

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
    def popup_auto_close_success(cls, message, title=None, duration=2):
        return sg.popup_auto_close(
            message,
            title=(title or "Success"),
            image=cls.get_icon("ok"),
            auto_close_duration=duration,
            keep_on_top=True,
        )

    @classmethod
    def popup_auto_close_error(cls, message, title=None, duration=2):
        return sg.popup_auto_close(
            message,
            title=(title or "Error"),
            image=cls.get_icon("cancel"),
            auto_close_duration=duration,
            keep_on_top=True,
        )

    @classmethod
    def popup_auto_close_warn(cls, message, title=None, duration=2):
        return sg.popup_auto_close(
            message,
            title=(title or "Warning"),
            image=cls.get_icon("warning"),
            auto_close_duration=duration,
            keep_on_top=True,
        )

    @classmethod
    def window_init_dict(cls):
        init_dict = {
            "size": cls.SCREEN_SIZE,
            "no_titlebar": True,
            "keep_on_top": True,
            "grab_anywhere": False,
            "finalize": True,
            "use_custom_titlebar": False,
        }
        return init_dict

    @staticmethod
    def message_display_field():
        return sg.pin(
            sg.Text("", enable_events=True, k="message_display", visible=False)
        )

    @staticmethod
    def display_message(message, window):
        window["message_display"].update(value=message, visible=True)

    @staticmethod
    def hide_message_display_field(window):
        window["message_display"].update(value="", visible=False)
