from typing import Any, Dict, List
import PySimpleGUI as sg

from app.basegui import BaseGUIWindow
import app.appconfigparser
import app.windowdispatch
from db.models import AttendanceRecord

app_config = app.appconfigparser.AppConfigParser()
window_dispatch = app.windowdispatch.WindowDispatch()


class AttendanceSignOutWindow(BaseGUIWindow):
    """Window for students to sign out from an active event."""
    __slots__ = ()

    @classmethod
    def window(cls) -> List[Any]:
        """Construct layout/appearance of window."""
        event_dict = app_config.cp["current_attendance_session"]
        student_dict = app_config.cp["tmp_student"]
        # student_attendance = AttendanceRecord.objects.filter(
        #     attendance_session_id=app_config.cp.get(
        #         "current_attendance_session", "session_id"
        #     ),
        #     student_id=student_dict["reg_number"],
        # )
        layout = [
            [sg.VPush()],
            [sg.Text("Student Attendance Details")],
            [sg.HorizontalSeparator()],
            [
                sg.Text("STATUS: SIGNED IN!"),
            ],
            [sg.Text(f"Course: {event_dict.get('course', '')}")],
            [
                sg.Text(
                    f"Student Name: {student_dict.get('first_name', '')} {student_dict.get('last_name', '')}"
                )
            ],
            [
                sg.Text(
                    f"Registration Number: {student_dict.get('reg_number', '')} "
                )
            ],
            # [sg.Text(f"Sign In Time: {student_attendance[0].check_in_by}")],
            [sg.VPush()],
            [
                sg.Button(
                    "Sign Out",
                    k=cls.key("sign_out"),
                    **cls.cancel_button_kwargs(),
                ),
                sg.Button(
                    "Back",
                    k=cls.key("back"),
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
        if event in (cls.key("home"), cls.key("back")):
            window_dispatch.dispatch.open_window("HomeWindow")
            return True
        if event == cls.key("sign_out"):
            # TODO: implement this
            window_dispatch.dispatch.open_window(
                "StudentFaceVerificationWindow"
            )

        return True
