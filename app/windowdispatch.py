from collections import UserDict
from importlib import import_module
from typing import Any, Optional, Type, Callable

import PySimpleGUI as sg

from app.basegui import BaseGUIWindow
from app.windows.settings import APP_WINDOWS


class WindowDispatch:
    """A singleton that holds the currently open window."""

    __instance = None
    __initalized = False

    def __new__(cls) -> "WindowDispatch":
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self) -> None:
        if type(self).__initalized:
            return
        type(self).__initalized = True
        self.dispatch = WindowDict()


class WindowDict(UserDict):
    """Class for handling transitions between windows."""

    _current_window: Callable[..., Any]
    _current_window_class: BaseGUIWindow

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super(WindowDict, self).__init__(*args, **kwargs)

    def open_window(
        self,
        window_class_name: str,
    ) -> None:
        """Open a GUI window."""
        try:
            window_path = APP_WINDOWS[window_class_name]
        except KeyError:
            BaseGUIWindow.popup_auto_close_error(
                f"{window_class_name} not found in APP_WINDOWS"
            )
            return None

        window_module = import_module(window_path)

        try:
            window_class = getattr(window_module, window_class_name)
        except AttributeError:
            raise RuntimeError(
                "%s not found in specified path." % window_class_name
            )

        self.update({window_class.__name__: window_class.window()})
        open_windows = self.copy()
        for key in open_windows.keys():
            if key != window_class.__name__:
                self.close_window(key)

        self.current_window_class = window_class
        self.current_window = self[window_class.__name__]

    def close_window(self, window_name: str) -> None:
        """Close a window."""
        self.pop(window_name).close()

    def find_window_name(self, window_object: sg.Window) -> Optional[str]:
        """Find name of a given window object if it exists in WindowDict."""
        return next((k for k, v in self.items() if v == window_object), None)

    @property
    def current_window(self) -> Callable[..., Any]:
        """Name of the currently open window."""
        return self._current_window

    @current_window.setter
    def current_window(self, value: Callable[..., Any]) -> None:
        """Set current_window property."""
        self._current_window = value

    @property
    def current_window_class(self) -> BaseGUIWindow:
        """Class of currently open window."""
        return self._current_window_class

    @current_window_class.setter
    def current_window_class(self, value: BaseGUIWindow) -> None:
        """Set current_window_class property."""
        self._current_window_class = value


class WindowDispatched:
    _current_window: sg.Window
    _current_window_name = None

    def open_window(
        self,
        window_class: Type[BaseGUIWindow],
    ) -> None:
        # temporary store the current window
        # to be closed after the new window is opened

        if self._current_window_name is not None:
            self.current_window.close()

        self._current_window_name = window_class.__name__
        self.current_window = window_class.window()

    def find_window_name(self, window_object: sg.Window):
        return self._current_window_name

    @property
    def current_window(self):
        return self._current_window

    @current_window.setter
    def current_window(self, value):
        if isinstance(value, sg.Window):
            self._current_window = value
