from collections import UserDict
from typing import Type

import PySimpleGUI as sg

from app.basegui import BaseGUIWindow


class WindowDispatch(UserDict):
    def __init__(self, *args, **kwargs):
        super(WindowDispatch, self).__init__(*args, **kwargs)

    def open_window(
        self,
        window_class: Type[BaseGUIWindow],
        on_seperate_window: bool = False,
    ) -> sg.Window:
        self.update({window_class.__name__: window_class.window()})

        if not on_seperate_window:
            open_windows = self.copy()
            for key in open_windows.keys():
                if key != window_class.__name__:
                    self.close_window(key)

    def close_window(self, window_name: str):
        return self.pop(window_name).close()

    def find_window(self, window_object: sg.Window):
        return next((k for k, v in self.items() if v == window_object), None)
