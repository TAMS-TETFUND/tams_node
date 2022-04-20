import io
import json
import os
import base64
import configparser
from pathlib import Path

from PIL import Image, ImageDraw, ImageTk, ImageFont
import PySimpleGUI as sg

from manage import init_django

init_django()

from db.models import AttendanceSession

CURRENT_DIR = os.path.abspath(__file__)
CONFIG_FILE = os.path.join(Path(CURRENT_DIR).parent, "config.ini")


window_dispatch = {
    "home_window": None,
}

# set application-wide theme
sg.theme("LightGreen6")

# initializing the configparser object
app_config = configparser.ConfigParser()
app_config.read(CONFIG_FILE)


class BaseGUIWindow:
    SCREEN_SIZE = (480, 320)
    ICON_SIZE = {"h": 125, "w": 70}
    ICON_BUTTON_COLOR = (sg.theme_background_color(), sg.theme_background_color())

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
    def get_icon(cls, icon_name):
        icons_path = os.path.join(Path(CURRENT_DIR).parent, "icons.json")
        with open(icons_path, "r") as data:
            icon_dict = json.loads(data.read())
        icon = icon_dict[icon_name]
        return cls._image_file_to_bytes(icon, (cls.ICON_SIZE["h"], cls.ICON_SIZE["w"]))


class HomeWindow(BaseGUIWindow):

    @classmethod
    def make_window(cls):
        column1 = [
            [
                sg.Push(),
                sg.Button(image_data=cls.get_icon("fingerprint"), button_color=cls.ICON_BUTTON_COLOR, key="new_event"),
                sg.Push()
            ],
            [sg.Push(), sg.Text("New Event"), sg.Push()]
        ]
        column2 = [
            [
                sg.Push(),
                sg.Button(image_data=cls.get_icon("users"), button_color=cls.ICON_BUTTON_COLOR, key="continue_attendance"),
                sg.Push()
            ],
            [sg.Push(), sg.Text("Continue Attendance"), sg.Push()]
        ]
        column3 = [
            [
                sg.Push(),
                sg.Button(image_data=cls.get_icon("schedule"), button_color=cls.ICON_BUTTON_COLOR, key="schedule"),
                sg.Push()
            ],
            [sg.Push(), sg.Text("Scheduled/Recurring Events"), sg.Push()]
        ]
        layout = [
            [
                sg.Push(),
                sg.Button(image_data=cls.get_icon("power"), button_color=cls.ICON_BUTTON_COLOR, key="quit"),
            ],
            [sg.VPush()],
            [
                sg.Push(),
                sg.Column(column1),
                sg.Column(column2),
                sg.Column(column3),
                sg.Push()
            ],
            [sg.VPush()],
            [sg.Text("_" * 80)],
            [sg.Push(), sg.Text("TAMS© 2022"), sg.Push()],
        ]

        window = sg.Window(
            "Home Window",
            layout,
            size=cls.SCREEN_SIZE,
            finalize=True,
        )
        return window
    
    @staticmethod
    def window_loop(window, event, values):
        if event == "new_event":
            global window_dispatch
            window_dispatch.update({'another_win': AnotherWindow.make_window()})
            window_dispatch['home_win'].close()
            window_dispatch['home_win'] = None

        if event == "quit":
            return HomeWindow.confirm_exit()
        return True


class AnotherWindow(BaseGUIWindow):
    @classmethod
    def make_window(cls):
        layout = [
            [sg.VPush()],
            [
                sg.Push(),
                sg.Text("This is another window:"),
                sg.Push()    
            ],
            [sg.Text("Classes may work out after all")],
            [sg.Button("Quit", key="quit")],
            [sg.Button("New Event Button", key="new_event")],
        ]

        window = sg.Window(
            "Another Window",
            layout,
            size=cls.SCREEN_SIZE,
            finalize=True,
        )
        return window
    
    @staticmethod
    def window_loop(window, event, values):
        print("entering another window loop")
        if event == "new_event":
            global window_dispatch
            window_dispatch.update({'home_win': HomeWindow.make_window()})
            window_dispatch['another_win'].close()
            window_dispatch['another_win'] = None
            
        if event == "quit":
             return AnotherWindow.confirm_exit()
        return True


def main():
    global window_dispatch
    window_dispatch.update({'home_win': HomeWindow.make_window()})
    while True:
        window, event, values = sg.read_all_windows()
        window_loop_exit_code = True
        if window == window_dispatch['home_win']:
            window_loop_exit_code = HomeWindow.window_loop(window, event, values)
        if window == window_dispatch['another_win']:
            window_loop_exit_code = AnotherWindow.window_loop(window, event, values)
        if not window_loop_exit_code:
            break
        if event == sg.WIN_CLOSED:
            break
    window.close()


if __name__ == "__main__":
    main()