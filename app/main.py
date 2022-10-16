"""This module contains the function that starts the GUI application."""

import PySimpleGUI as sg


from manage import django_setup

django_setup()

import app.appconfigparser
import app.windowdispatch


app_config = app.appconfigparser.AppConfigParser()
window_dispatch = app.windowdispatch.WindowDispatch()


def main_loop() -> None:
    """Function that starts the application."""
    import app.guiutils

    # setting the operational mode of device
    app_config.cp["tmp_settings"] = {}
    app.guiutils.update_device_op_mode()
    continue_loop = True

    while continue_loop:
        window = window_dispatch.dispatch.app_window
        event, values = window.read(timeout=500)
        current_window = window_dispatch.dispatch.current_window
        current_window_class = window_dispatch.dispatch.current_window_class
        if current_window:
            continue_loop = current_window_class.loop(window, event, values)

        if event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT:
            from app.basegui import BaseGUIWindow

            continue_loop = BaseGUIWindow.confirm_exit()

        if event in (sg.WIN_CLOSED, None):
            break
