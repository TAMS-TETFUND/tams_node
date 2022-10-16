from typing import Any, Dict
import PySimpleGUI as sg

from app.basegui import BaseGUIWindow
import app.windowdispatch

window_dispatch = app.windowdispatch.WindowDispatch()

class LoadingWindow(BaseGUIWindow):
    """Window to display when an operation takes too long to complete."""

    @classmethod
    def window(cls) -> sg.Window:
        """Construct layout/appearance of window."""
        layout=[
            [sg.VPush()],
            [
                sg.Push(),
                sg.Image(
                    data=cls.get_icon("ring_lines", 2),
                    enable_events=True,
                    key="loading_image",
                ),
                sg.Push(),
            ],
            [sg.Push(), sg.Text("Loading..."), sg.Push()],
            [sg.VPush()],
            cls.navigation_pane(next_icon="next_disabled")
        ]
        return layout

    @classmethod
    def loop(
        cls, window: sg.Window, event: str, values: Dict[str, Any]
    ) -> bool:
        """Track user interaction with window."""
        if event in (cls.key("home"), cls.key("back")):
            window_dispatch.dispatch.open_window("HomeWindow")
        return True
