import PySimpleGUI as sg

import app.appconfigparser
import app.windowdispatch
from app.gui_utils import update_device_op_mode


app_config = app.appconfigparser.AppConfigParser()
window_dispatch = app.windowdispatch.WindowDispatch()


def main_loop():
    window_dispatch.dispatch.open_window("HomeWindow")
    # setting the operational mode of device
    app_config.cp["tmp_settings"] = {}
    update_device_op_mode()
    continue_loop = True
    window = None

    while continue_loop:
        window = window_dispatch.dispatch.current_window
        event, values = window.read(timeout=500)
        current_window = window_dispatch.dispatch.find_window_name(window)
        current_window_class = window_dispatch.dispatch.current_window_class
        if current_window:
            continue_loop = current_window_class.loop(window, event, values)
        if event == sg.WIN_CLOSED:
            break

    if window is not None:
        window.close()