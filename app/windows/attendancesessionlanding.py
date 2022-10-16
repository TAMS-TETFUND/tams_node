from typing import Any, Dict
import PySimpleGUI as sg

from app.basegui import BaseGUIWindow
from app.guiutils import StudentRegNumberInputRouterMixin
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
            [sg.Text(f"Course: {event_dict.get('course', '')}")],
            [
                sg.Text(
                    f"Session Details: {event_dict.get('session', '')} {event_dict.get('semester', '')}"
                )
            ],
            [
                sg.Text(
                    f"Start Time: {event_dict.get('start_date', '')} {event_dict.get('start_time', '')}"
                )
            ],
            [sg.Text(f"Duration: {event_dict.get('duration', '')} Hour(s)")],
            [
                sg.Text(f"Number of valid check-ins: "),
                sg.Text(
                    "{}".format(cls.valid_check_in_count()),
                    k=cls.key("valid_checks"),
                ),
                sg.Push(),
                sg.Button("Attendance List", k=cls.key("attendance_list")),
            ],
            [sg.VPush()],
            [
                sg.Button("Take Attendance", k=cls.key("start_attendance")),
                sg.Button(
                    "End Attendance",
                    k=cls.key("end_attendance"),
                    **cls.cancel_button_kwargs(),
                ),
            ],
            [sg.HorizontalSeparator()],
            cls.navigation_pane(
                back_icon="back_disabled", next_icon="next_disabled"
            ),
        ]
        return layout

    @classmethod
    def loop(
        cls, window: sg.Window, event: str, values: Dict[str, Any]
    ) -> bool:
        """Track user interaction with window"""
        if event == cls.key("home"):
            confirm = sg.popup_yes_no(
                "Leaving attendance-taking. Do you wish to continue?",
                title="Go back?",
                keep_on_top=True,
            )
            if confirm == "Yes":
                window_dispatch.dispatch.open_window("HomeWindow")
            return True

        if event == cls.key("attendance_list"):
            window_dispatch.dispatch.open_window("AttendanceViewerWindow")
        if event == cls.key("start_attendance"):
            cls.student_reg_number_input_window()

        if event == cls.key("end_attendance"):
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
        if app_config.cp.has_option("current_attendance_session", "session_id"):
            return AttendanceRecord.objects.filter(
                attendance_session=app_config.cp.get(
                    "current_attendance_session", "session_id"
                ),
                record_type=RecordTypesChoices.SIGN_IN,
            ).count()
        else:
            return 0
