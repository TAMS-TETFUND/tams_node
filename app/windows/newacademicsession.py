from datetime import datetime
from typing import Any, Dict
from django.db.utils import IntegrityError

import PySimpleGUI as sg

from app.basegui import BaseGUIWindow
from app.gui_utils import ValidationMixin
import app.appconfigparser
import app.windowdispatch
from db.models import AcademicSession


app_config = app.appconfigparser.AppConfigParser()
window_dispatch = app.windowdispatch.WindowDispatch()


class NewAcademicSessionWindow(ValidationMixin, BaseGUIWindow):
    """Window to create a new academic session."""

    @classmethod
    def window(cls) -> sg.Window:
        """Construct layout/appearance of window."""
        current_year = datetime.now().year
        allowed_yrs = [x for x in range(current_year, current_year + 4)]
        layout = [
            [sg.Push(), sg.Text("Add New Academic Session"), sg.Push()],
            [sg.HorizontalSeparator()],
            cls.message_display_field(),
            [sg.VPush()],
            [
                sg.Text("Session:", size=12),
                sg.Spin(
                    values=allowed_yrs,
                    initial_value=current_year,
                    k="session_start",
                    expand_x=True,
                    enable_events=True,
                ),
                sg.Text("/"),
                sg.Spin(
                    values=allowed_yrs[1:],
                    initial_value=(current_year + 1),
                    k="session_end",
                    expand_x=True,
                    enable_events=True,
                ),
            ],
            [sg.Check("Is this the current session?", k="is_current_session")],
            [
                sg.Push(),
                sg.Button(
                    "Create",
                    k="create_session",
                    font="Helvetica 12",
                ),
            ],
            [sg.VPush()],
            cls.navigation_pane(next_icon="next_disabled"),
        ]
        window = sg.Window(
            "New Academic Session",
            layout,
            **cls.window_init_dict(),
        )
        return window

    @classmethod
    def loop(
        cls, window: sg.Window, event: str, values: Dict[str, Any]
    ) -> bool:
        """Track user interaction with window."""
        if event == "back":
            window_dispatch.dispatch.open_window("AcademicSessionDetailsWindow")
        if event == "home":
            window_dispatch.dispatch.open_window("HomeWindow")

        if event == "create_session":
            for val in ("session_start", "session_end"):
                try:
                    val_int = int(values[val])
                except ValueError:
                    cls.display_message(
                        "Enter numeric values for Academic Session Years",
                        window,
                    )
                    return True

                new_session = (
                    str(values["session_start"])
                    + "/"
                    + str(values["session_end"])
                )
                is_current_session = values["is_current_session"]
                val_check = cls.validate_academic_session(new_session)
                if val_check is not None:
                    cls.display_message(val_check, window)
                    return True

                try:
                    new_session_obj = AcademicSession.objects.create(
                        session=new_session,
                        is_current_session=is_current_session,
                    )
                except IntegrityError as e:
                    cls.display_message(
                        "Error. You may be trying to create a"
                        " session that already exists",
                        window,
                    )
                    print(e)
                    return True

                cls.popup_auto_close_success(
                    f"Academic session {new_session_obj.session} created successfully"
                )
                window_dispatch.dispatch.open_window("HomeWindow")
                return True

        if event == "session_start":
            try:
                session_start_int = int(values["session_start"])
            except ValueError:
                cls.display_message(
                    "Enter numeric values for Academic Session", window
                )
                return True
            else:
                if session_start_int > 0:
                    window["session_end"].update(value=session_start_int + 1)
                else:
                    window["session_end"].update(value=0)
                return True

        if event == "session_end":
            try:
                session_end_int = int(values["session_end"])
            except ValueError:
                cls.display_message(
                    "Enter numeric values for Academic Session", window
                )
                return True
            else:
                if session_end_int > 0:
                    window["session_start"].update(value=session_end_int - 1)
                else:
                    window["session_start"].update(value=0)
                return True
        return True
