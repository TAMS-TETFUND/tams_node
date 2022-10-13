from typing import Any, Dict
import PySimpleGUI as sg

from app.basegui import BaseGUIWindow


class LoadingWindow(BaseGUIWindow):
    """Window to display when an operation takes too long to complete."""

    @classmethod
    def window(cls) -> sg.Window:
        """Construct layout/appearance of window."""
        return sg.Window(
            title="Loading window",
            layout=[
                [sg.VPush()],
                [   sg.Push(),
                    sg.Image(
                        data=cls.get_icon("ring_lines", 2),
                        enable_events=True,
                        key="loading_image",
                    ),
                    sg.Push()

                ],
                [sg.Push(), sg.Text("Loading..."), sg.Push()],
                [sg.VPush()],
            ],
            **cls.window_init_dict()
        )

    @classmethod
    def loop(
        cls, window: sg.Window, event: str, values: Dict[str, Any]
    ) -> bool:
        """Track user interaction with window."""
