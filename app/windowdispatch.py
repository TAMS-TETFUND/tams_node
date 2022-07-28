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

    def find_window_name(self, window_object: sg.Window):
        return next((k for k, v in self.items() if v == window_object), None)

    @property
    def current_window(self):
        return self._current_window

    @current_window.setter
    def current_window(self, value):
        if isinstance(value, sg.Window):
            self._current_window = value


# class WindowDispatched:
#
#     def __init__(self):
#         self._current_window: sg.Window = sg.Window('default')
#         self._current_window_obj = None
#         self._window_stack: list = []
#
#     def open_window(
#             self,
#             window_class: Type[BaseGUIWindow],
#     ) -> None:
#
#         # temporary store the current window
#         # to be closed after the new window is opened
#
#         # excluding the loading window from the stack of windows
#         if self._current_window_obj is not None and self._current_window_obj.__name__ != "LoadingWindow":
#             self._window_stack.append(self._current_window_obj)
#
#         self._current_window_obj = window_class
#         self.current_window.close()
#         self.current_window = window_class.window()
#
#     def find_window_name(self, window_object: sg.Window):
#         return self._current_window_obj.__name__
#
#     def previous_window(self):
#         if len(self._window_stack) == 0:
#             return
#
#         self._current_window_obj = self._window_stack.pop()
#         self.current_window.close()
#         self.current_window = self._current_window_obj.window()
#
#     def pop_home(self):
#         self._current_window_obj = self._window_stack[0]
#         self.current_window.close()
#         self.current_window = self._current_window_obj.window()
#         self._window_stack.clear()
#
#     @property
#     def current_window(self):
#         return self._current_window
#
#     @property
#     def window_stack(self):
#         return self._window_stack
#
#     @current_window.setter
#     def current_window(self, value):
#         if isinstance(value, sg.Window):
#             self._current_window = value
