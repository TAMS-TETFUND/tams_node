from typing import Any, Dict, List

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
    __slots__ = ()

    @classmethod
    def window(cls) -> List[Any]:
        """Construct layout/appearance of window."""
        layout = [
            [
                sg.Push(),
                sg.Text("Select Event Type"),
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
                    key=cls.key("event_type"),
                    size=42,
                ),
                sg.Push(),
            ],
            [sg.Push(), sg.Button("Select", k=cls.key("submit"))],
            [sg.VPush()],
            [sg.HorizontalSeparator()],
            cls.navigation_pane(next_icon="next_disabled"),
        ]
        return layout

    @classmethod
    def loop(
        cls, window: sg.Window, event: str, values: Dict[str, Any]
    ) -> bool:
        """Track user interaction with window."""
        if event in (
            sg.WIN_CLOSED,
            cls.key("back"),
            cls.key("cancel"),
            cls.key("home"),
        ):
            window_dispatch.dispatch.open_window("HomeWindow")

        if event == cls.key("submit"):
            app_config.cp["new_event"] = {}
            app_config.cp["new_event"]["type"] = values[cls.key("event_type")]
            app_config.cp["new_event"]["recurring"] = "False"
            app_config.cp.save()
            if values[cls.key("event_type")].lower() not in (
                "examination",
                "quiz",
            ):
                recurring = sg.popup_yes_no(
                    f"Is this {values[cls.key('event_type')]} a weekly activity?",
                    title="Event detail",
                    keep_on_top=True,
                )
                if recurring == "Yes":
                    app_config.cp["new_event"]["recurring"] = "True"

            window_dispatch.dispatch.open_window("AcademicSessionDetailsWindow")
        return True
