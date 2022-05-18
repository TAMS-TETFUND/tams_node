from collections import UserDict
from typing import Type

import PySimpleGUI as sg

from app.basegui import BaseGUIWindow


class WindowDispatch(UserDict):
    _current_window: sg.Window

    def __init__(self, *args, **kwargs):
        super(WindowDispatch, self).__init__(*args, **kwargs)

    def open_window(
        self,
        window_class: Type[BaseGUIWindow],
    ) -> None:
        self.update({window_class.__name__: window_class.window()})
        open_windows = self.copy()
        for key in open_windows.keys():
            if key != window_class.__name__:
                self.close_window(key)
        self.current_window = self[window_class.__name__]

    def close_window(self, window_name: str):
        return self.pop(window_name).close()

    @property
    def current_window(self):
        return self._current_window

    @current_window.setter
    def current_window(self, value):
        if isinstance(value, sg.Window):
            self._current_window = value
