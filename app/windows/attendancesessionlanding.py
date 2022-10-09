from typing import Any, Dict
import PySimpleGUI as sg

from app.basegui import BaseGUIWindow
from app.gui_utils import StudentRegNumberInputRouterMixin
import app.appconfigparser
import app.windowdispatch
from db.models import (
    RecordTypesChoices,
    AttendanceRecord,
    AttendanceSession,
    AttendanceSessionStatusChoices,
)


app_config = app.appconfigparser.AppConfigParser()
window_dispatch = app.windowdispatch.WindowDispatch()


class AttendanceSessionLandingWindow(
    StudentRegNumberInputRouterMixin, BaseGUIWindow
):
    """This is the landing window for the active attendance session."""

    @classmethod
    def window(cls) -> sg.Window:
        """Construct layout/appearance of window."""
        event_dict = dict(app_config.cp["current_attendance_session"])
        layout = [
            [sg.VPush()],
            [sg.Text("Attendance Session Details")],
            [sg.HorizontalSeparator()],
            [sg.Text(f"Course: {event_dict['course']}")],
            [
                sg.Text(
                    f"Session Details: {event_dict['session']} {event_dict['semester']}"
                )
            ],
            [
                sg.Text(
                    f"Start Time: {event_dict['start_date']} {event_dict['start_time']}"
                )
            ],
            [sg.Text(f"Duration: {event_dict['duration']} Hour(s)")],
            [
                sg.Text(f"Number of valid check-ins: "),
                sg.Text(
                    "{}".format(cls.valid_check_in_count()), k="valid_checks"
                ),
            ],
            [sg.VPush()],
            [
                sg.Button("Take Attendance", k="start_attendance"),
                sg.Button(
                    "End Attendance",
                    k="end_attendance",
                    **cls.cancel_button_kwargs(),
                ),
            ],
            [sg.HorizontalSeparator()],
            cls.navigation_pane(
                back_icon="back_disabled", next_icon="next_disabled"
            ),
        ]

        window = sg.Window(
            "Attendance Session Page", layout, **cls.window_init_dict()
        )
        return window

    @classmethod
    def loop(
        cls, window: sg.Window, event: str, values: Dict[str, Any]
    ) -> bool:
        """Track user interaction with window"""
        if event == "home":
            confirm = sg.popup_yes_no(
                "Leaving attendance-taking. Do you wish to continue?",
                title="Go back?",
                keep_on_top=True,
            )
            if confirm == "Yes":
                window_dispatch.dispatch.open_window("HomeWindow")
            return True

        if event == "start_attendance":
            cls.student_reg_number_input_window()

        if event == "end_attendance":
            confirm = sg.popup_yes_no(
                "This will permanently end attendance-taking for this event. "
                "Do you wish to continue?",
                title="End Attendance Session?",
                keep_on_top=True,
            )
            if confirm == "Yes":
                att_session = AttendanceSession.objects.get(
                    id=app_config.cp.get(
                        "current_attendance_session", "session_id"
                    )
                )
                att_session.status = AttendanceSessionStatusChoices.ENDED
                att_session.save()
                app_config.cp.remove_section("current_attendance_session")
                app_config.cp.remove_section("failed_attempts")
                app_config.cp.remove_section("tmp_student")
                app_config.cp.remove_section("tmp_staff")
                window_dispatch.dispatch.open_window("HomeWindow")
        return True

    @staticmethod
    def valid_check_in_count() -> int:
        """Count of students that have logged attendance for current event."""
        return AttendanceRecord.objects.filter(
            attendance_session=app_config.cp.get(
                "current_attendance_session", "session_id"
            ),
            record_type=RecordTypesChoices.SIGN_IN,
        ).count()
