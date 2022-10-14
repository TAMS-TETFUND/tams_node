from typing import Any, Dict

import PySimpleGUI as sg
from app.basegui import BaseGUIWindow
import app.appconfigparser
import app.windowdispatch
from db.models import EventTypeChoices


app_config = app.appconfigparser.AppConfigParser()
window_dispatch = app.windowdispatch.WindowDispatch()


class EventMenuWindow(BaseGUIWindow):
    """
    A window which presents options for the user to choose the
    event type for the attendance session.
    """

    @classmethod
    def window(cls) -> sg.Window:
        """Construct layout/appearance of window."""
        layout = [
            [
                sg.Push(),
                sg.Text("Select Event Type", font="Helvetica 24"),
                sg.Push(),
            ],
            [sg.HorizontalSeparator()],
            [sg.VPush()],
            [
                sg.Push(), 
                sg.Text("Event:  "),
                sg.Combo(
                    values=EventTypeChoices.labels,
                    default_value=EventTypeChoices.labels[0],
                    key="event_type",
                    size=40
                ), 
                sg.Push()
            ],
            [sg.Push(), sg.Button("Select", k="submit")],
            [sg.VPush()],
            [sg.HorizontalSeparator()],
            cls.navigation_pane(next_icon="next_disabled"),
        ]
        window = sg.Window("Event Menu", layout, **cls.window_init_dict())
        return window

    @classmethod
    def loop(
        cls, window: sg.Window, event: str, values: Dict[str, Any]
    ) -> bool:
        """Track user interaction with window."""
        if event in (sg.WIN_CLOSED, "back", "cancel", "home"):
            window_dispatch.dispatch.open_window("HomeWindow")
  
        if event == "submit":
            app_config.cp["new_event"] = {}
            app_config.cp["new_event"]["type"] = values["event_type"]
            app_config.cp["new_event"]["recurring"] = "False"
            if values["event_type"].lower() not in ("examination", "quiz"):
                recurring = sg.popup_yes_no(
                    f"Is this {values['event_type']} a weekly activity?",
                    title="Event detail",
                    keep_on_top=True,
                )
                if recurring == "Yes":
                    app_config.cp["new_event"]["recurring"] = "True"

            window_dispatch.dispatch.open_window("AcademicSessionDetailsWindow")
        return True
