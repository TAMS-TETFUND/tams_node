import PySimpleGUI as sg

from app.basegui import BaseGUIWindow
from app.gui_utils import ValidationMixin
import app.appconfigparser
import app.windowdispatch
from db.models import AcademicSession, SemesterChoices


app_config = app.appconfigparser.AppConfigParser()
window_dispatch = app.windowdispatch.WindowDispatch()


class AcademicSessionDetailsWindow(ValidationMixin, BaseGUIWindow):
    """Window to choose the academic session and academic semester for
    new attendance event."""

    @classmethod
    def window(cls):
        all_academic_sessions = AcademicSession.get_all_academic_sessions()
        layout = [
            [sg.Push(), sg.Text("Academic Session Details"), sg.Push()],
            [sg.HorizontalSeparator()],
            [sg.VPush()],
            [
                [cls.message_display_field()],
                sg.Text("Select Current Session:   "),
                sg.Combo(
                    all_academic_sessions,
                    default_value=(
                        all_academic_sessions[0]
                        if all_academic_sessions
                        else cls.COMBO_DEFAULT
                    ),
                    enable_events=True,
                    key="current_session",
                    expand_y=True,
                    expand_x=True,
                ),
            ],
            [
                sg.Push(),
                sg.Text(
                    "New Academic Session?", k="new_session", enable_events=True
                ),
            ],
            [
                sg.Text("Select Current Semester: "),
                sg.Combo(
                    SemesterChoices.labels,
                    default_value=SemesterChoices.labels[0],
                    enable_events=True,
                    key="current_semester",
                    expand_y=True,
                    expand_x=True,
                ),
            ],
            [sg.VPush()],
            cls.navigation_pane(),
        ]

        window = sg.Window(
            "Academic Session Details", layout, **cls.window_init_dict()
        )
        return window

    @classmethod
    def loop(cls, window, event, values):
        if event == "next":
            if cls.validate(values, window) is not None:
                return True

            app_config.cp["DEFAULT"]["semester"] = values["current_semester"]
            app_config.cp["DEFAULT"]["session"] = values["current_session"]
            window_dispatch.dispatch.open_window("EventDetailWindow")
        elif event == "back":
            window_dispatch.dispatch.open_window("EventMenuWindow")
        elif event == "home":
            window_dispatch.dispatch.open_window("HomeWindow")
        elif event == "new_session":
            window_dispatch.dispatch.open_window("NewAcademicSessionWindow")
        return True

    @classmethod
    def validate(cls, values, window):
        required_fields = [
            (values["current_semester"], "current semester"),
            (values["current_session"], "current session"),
        ]
        if cls.validate_required_fields(required_fields, window) is not None:
            return True

        validation_val = cls.validate_semester(values["current_semester"])
        if validation_val is not None:
            cls.display_message(validation_val, window)
            return True

        validation_val = cls.validate_academic_session(
            values["current_session"]
        )
        if validation_val is not None:
            cls.display_message(validation_val, window)
            return True

        if not AcademicSession.objects.filter(
            session=values["current_session"]
        ).exists():
            cls.display_message(
                "Academic Session has not been registered.", window
            )
            return True
        return None
