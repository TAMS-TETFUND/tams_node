import io
import json
import os
from pathlib import Path
import base64
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Type

from PIL import Image
import PySimpleGUI as sg

# set application-wide theme
sg.theme("DarkGrey")


class BaseGUIWindow:
    """The Base GUI Window class.

    Contains methods that are commonly used in application windows.
    """

    COMBO_DEFAULT: str = "--select--"
    SCREEN_SIZE: Tuple[int, int] = (480, 320)
    ICON_SIZE: Dict[str, int] = {"h": 125, "w": 70}
    ICON_BUTTON_COLOR: Tuple[str, str] = (
        sg.theme_background_color(),
        sg.theme_background_color(),
    )
    BUTTON_COLOR: Tuple[str, str] = ("#004f00", "#004f00")
    UI_COLORS: Dict[str, str] = {
        "red": "#fc2323",
        "yellow": "#fffb08",
        "green": "#08ff14",
        "blue": "#1111fc",
        "dull_yellow": "#f5ed71",
        "light_grey": "#505050",
        "lighter_grey": "#bbbbbb",
    }

    @classmethod
    def window(cls) -> Exception:
        """For defining the layout of the window.

        Implemented only in concrete child classes.
        Returns a finalized PySimpleGUI window when implemented.
        """
        raise NotImplementedError

    @classmethod
    def loop(
        cls, window: sg.Window, event: str, values: Dict[str, Any]
    ) -> Exception:
        """For handling events and user inputs.

        Implemented only in concrete window child classes.
        Returns a bool when implmented.
        """
        raise NotImplementedError

    @staticmethod
    def _image_file_to_bytes(image64: str, size: Iterable[float]) -> bytes:
        """Converts an image64 from str to byte string"""
        image_file = io.BytesIO(base64.b64decode(image64))
        img = Image.open(image_file)
        img.thumbnail(size, Image.ANTIALIAS)
        bio = io.BytesIO()
        img.save(bio, format="PNG")
        imgbytes = bio.getvalue()
        return imgbytes

    @classmethod
    def get_icon(
        cls,
        icon_name: str,
        size_ratio: float = 1.0,
        image_dimension: Iterable[int] = None,
    ) -> bytes:
        """Find an icon in icons json file.


        Returns the byte string of the icon image if icon is defined.
        """
        image_height, image_width = image_dimension or [
            cls.ICON_SIZE["h"],
            cls.ICON_SIZE["w"],
        ]
        icons_path = os.path.join(
            Path(os.path.abspath(__file__)).parent, "icons.json"
        )
        with open(icons_path, "r") as data:
            icon_dict = json.loads(data.read())
        try:
            icon = icon_dict[icon_name]
        except KeyError as e:
            raise e

        return cls._image_file_to_bytes(
            icon,
            (image_height * size_ratio, image_width * size_ratio),
        )

    @classmethod
    def popup_auto_close_success(
        cls, message: str, title: Optional[str] = None, duration: int = 2
    ) -> sg.popup_auto_close:
        """A popup for successful operations."""
        return sg.popup_auto_close(
            message,
            title=(title or "Success"),
            image=cls.get_icon("ok"),
            auto_close_duration=duration,
            keep_on_top=True,
        )

    @classmethod
    def popup_auto_close_error(
        cls, message: str, title: Optional[str] = None, duration: int = 2
    ) -> sg.popup_auto_close:
        """A popup for unsuccessful operations."""
        return sg.popup_auto_close(
            message,
            title=(title or "Error"),
            image=cls.get_icon("cancel"),
            auto_close_duration=duration,
            keep_on_top=True,
        )

    @classmethod
    def popup_auto_close_warn(
        cls, message: str, title: Optional[str] = None, duration: int = 2
    ) -> sg.popup_auto_close:
        """A popup for warning users."""
        return sg.popup_auto_close(
            message,
            title=(title or "Warning"),
            image=cls.get_icon("warning"),
            auto_close_duration=duration,
            keep_on_top=True,
        )

    @staticmethod
    def confirm_exit() -> bool:
        """Confirm user wants to exit application."""
        clicked = sg.popup_ok_cancel(
            "Shutting down attendance logger. Do you want to continue?",
            title="Shutdown",
            keep_on_top=True,
        )
        if clicked == "OK":
            return False
        if clicked in ("Cancel", None):
            return True
        return True

    @classmethod
    def window_init_dict(cls) -> Dict[str, Any]:
        """Common parameters passed into the window class during initialization."""
        init_dict = {
            "size": cls.SCREEN_SIZE,
            "font": "Helvetica 13",
            "no_titlebar": False,
            "icon": cls.get_icon("icon"),
            "grab_anywhere": False,
            "margins": (0, 0),
            "enable_close_attempted_event":True,
        }
        return init_dict

    @classmethod
    def message_display_field(cls) -> Callable[[Any], sg.Column]:
        """A field for displaying messages to the user on an app window."""
        return sg.pin(
            sg.Text("", enable_events=True, k=cls.key("message_display"), visible=False)
        )

    @classmethod
    def cancel_button_kwargs(cls) -> Dict[str, Any]:
        """Styling for window cancel buttons."""
        kwargs_dict = {"button_color": ("#ffffff", cls.UI_COLORS["red"])}
        return kwargs_dict

    @classmethod
    def display_message(cls, message: str, window: sg.Window) -> None:
        """Add a message to the message display field."""
        window[cls.key("message_display")].update(value=message, visible=True)

    @classmethod
    def hide_message_display_field(cls, window: sg.Window) -> None:
        """Clear messages from the message display field."""
        window[cls.key("message_display")].update(value="", visible=False)

    @classmethod
    def navigation_pane(
        cls, *, next_icon: str = "next_grey", back_icon: str = "back_grey"
    ) -> List[sg.Column]:
        """Navigation pane for application-wide use."""
        return [
            sg.Column(
                [
                    [
                        sg.Button(
                            image_data=cls.get_icon(back_icon, 0.4),
                            button_color=cls.ICON_BUTTON_COLOR,
                            key=cls.key("back"),
                            use_ttk_buttons=True,
                        ),
                        sg.Button(
                            image_data=cls.get_icon(next_icon, 0.4),
                            button_color=cls.ICON_BUTTON_COLOR,
                            key=cls.key("next"),
                            use_ttk_buttons=True,
                        ),
                        sg.Push(),
                        sg.Button(
                            image_data=cls.get_icon("home_grey", 0.4),
                            button_color=cls.ICON_BUTTON_COLOR,
                            key=cls.key("home"),
                            use_ttk_buttons=True,
                        ),
                    ],
                ],
                pad=(0, 0),
                key="navigation_pane",
            )
        ]    

    @classmethod
    def key(cls, suffix: str) -> str:
        """Generate key for window elements based on class name and suffix value."""
        return ''.join([cls.__name__.lower().strip('window'), '_', suffix])

    @classmethod
    def key_prefix(cls) -> str:
        """Get prefix used to generate unique key for window elements."""
        return ''.join([cls.__name__.lower().strip('window'), '_'])

    @classmethod
    def refresh_dynamic_fields(cls, window: sg.Window) -> None:
        """Refresh dynamic fields in a window.
        
        Called when the window is about to be made visible.
        For use in windows that need data from database or confifgparser
        file.
        """

    @classmethod
    def adjust_input_field_size(cls, window: sg.Window, input_fields: Iterable[str] = []) -> None:
        """Adjust input field sizes to avoid uneven widths in appearance."""
        try:
            window[cls.key("main_column")].expand(expand_x=True, expand_y=True)
        except KeyError:
            pass
        if len(input_fields) > 0:
            for key in input_fields:
                window[cls.key(key)].expand(expand_x=True)