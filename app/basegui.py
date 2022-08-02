import io
import json
import os
from pathlib import Path
import base64

from PIL import Image
import PySimpleGUI as sg

# set application-wide theme
sg.theme("DarkGrey")


class BaseGUIWindow:
    COMBO_DEFAULT = "--select--"
    SCREEN_SIZE = (480, 320)
    ICON_SIZE = {"h": 125, "w": 70}
    ICON_BUTTON_COLOR = (
        sg.theme_background_color(),
        sg.theme_background_color(),
    )
    BUTTON_COLOR = ("#004f00", "#004f00")
    UI_COLORS = {
        "red": "#fc2323",
        "yellow": "#fffb08",
        "green": "#08ff14",
        "blue": "#1111fc",
        "dull_yellow": "#f5ed71",
        "light_grey": "#505050",
        "lighter_grey": "#bbbbbb",
    }

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
    def get_icon(cls, icon_name, size_ratio=1, image_dimension=None):
        image_height, image_width = image_dimension or [
            cls.ICON_SIZE["h"],
            cls.ICON_SIZE["w"],
        ]
        icons_path = os.path.join(
            Path(os.path.abspath(__file__)).parent, "icons.json"
        )
        with open(icons_path, "r") as data:
            icon_dict = json.loads(data.read())
        icon = icon_dict[icon_name]
        return cls._image_file_to_bytes(
            icon,
            (image_height * size_ratio, image_width * size_ratio),
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
            "font": "Helvetica 12",
            "no_titlebar": True,
            "icon": cls.get_icon("icon"),
            "grab_anywhere": False,
            "modal": True,
            "finalize": True,
        }
        return init_dict

    @staticmethod
    def message_display_field():
        return sg.pin(
            sg.Text("", enable_events=True, k="message_display", visible=False)
        )

    @classmethod
    def cancel_button_kwargs(cls):
        kwargs_dict = {"button_color": ("#ffffff", cls.UI_COLORS["red"])}
        return kwargs_dict

    @staticmethod
    def display_message(message, window):
        window["message_display"].update(value=message, visible=True)

    @staticmethod
    def hide_message_display_field(window):
        window["message_display"].update(value="", visible=False)

    @classmethod
    def navigation_pane(cls, *, next_icon="next_grey", back_icon="back_grey"):
        # TODO: all back button takes back to home instead of the previous screen
        return [
            sg.Column(
                [
                    [
                        sg.Button(
                            image_data=cls.get_icon(back_icon, 0.4),
                            button_color=cls.ICON_BUTTON_COLOR,
                            key="back",
                            use_ttk_buttons=True,
                        ),
                        sg.Button(
                            image_data=cls.get_icon(next_icon, 0.4),
                            button_color=cls.ICON_BUTTON_COLOR,
                            key="next",
                            use_ttk_buttons=True,
                        ),
                        sg.Push(),
                        sg.Button(
                            image_data=cls.get_icon("home_grey", 0.4),
                            button_color=cls.ICON_BUTTON_COLOR,
                            key="home",
                            use_ttk_buttons=True,
                        ),
                    ]
                ],
                expand_x=True,
                pad=(0, 0),
            )
        ]
